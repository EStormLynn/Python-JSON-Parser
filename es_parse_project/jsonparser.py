# -*- coding:utf-8 -*-
import re
from enum import Enum

# n ➔ literal
# t ➔ true
# f ➔ false
# " ➔ string
# 0-9/- ➔ number
# [ ➔ array
# { ➔ object


# json的数据格式
class JTYPE(Enum):
    NUMBER = 0
    STRING = 1
    ARRAY = 2
    OBJECT = 3
    NULL = 4
    FALSE = 5
    TRUE = 6
    UNKNOW = 7

state_dict = {1: "ok",
              2: "expect_value",
              3: "invalid_value",
              4: "root_not_singular"}

type_dict = {0: "number",
             1: "string",
             2: "array",
             3: "object",
             4: "null",
             5: "false",
             6: "true",
             7: "unknow"}

PARSE_STATE_OK = 1
PARSE_STATE_EXPECT_VALUE = 2
PARSE_STATE_INVALID_VALUE = 3
PARSE_STATE_ROOT_NOT_SINGULAR = 4


class EsValue(object):
    __slots__ = ('type', 'num', 'str', 'array', 'obj')
    
    def __init__(self, mytype):
        self.type = mytype


class Context(object):
    def __init__(self, jstr):
        self.json = list(jstr)
        self.pos = 0


def isdigit(ch):
    return re.compile('[0-9]+').match(ch)


def is1t9(ch):
    return re.compile('[1-9]+').match(ch)


def gettype(v):
    return v.type


def get_element(e_value):
    """获取解析后的value对象

    :param e_value: 传入json解析后的value对象
    :return: 返回value对象的类型 值
    """

    if e_value.type == JTYPE.STRING:
        return e_value.str
    if e_value.type == JTYPE.NUMBER:
        return e_value.num
    if e_value.type == JTYPE.ARRAY:
        return e_value.array
    if e_value.type == JTYPE.OBJECT:
        return e_value.obj
    if e_value.type == JTYPE.TRUE:
        return "true"
    if e_value.type == JTYPE.FALSE:
        return "false"
    if e_value.type == JTYPE.NULL:
        return "null"
    if e_value.type == JTYPE.UNKNOW:
        return "unknow"


def es_parse_whitespace(context):
    if not context.json:
        return
    pos = 0
    while pos < len(context.json):
        if re.compile('[ \t\n]+').match(context.json[pos]):
            pos += 1
        else:
            break
    context.json = context.json[pos:]


def es_parse_literal(context, e_value, literal, mytype):
    """ 解析字面量，包括null false true

    :param context: string list
    :param e_value: 字符串解析后对应的 结构对象
    :param literal: 字面量匹配的 字符串
    :param mytype: 字面量的数据类型
    :return:
    """
    if ''.join(context.json[context.pos:context.pos + len(literal)]) != literal:
        return PARSE_STATE_INVALID_VALUE
    else:
        e_value.type = mytype
        context.json = context.json[context.pos + len(literal):]
        return PARSE_STATE_OK


def es_parse_number(context, e_value):
    star_pos = context.pos
    pos = context.pos
    isint = 1
    try:
        if re.compile('[-+0]?').match(context.json[pos]):   # 首位[+-0]
            pos += 1

        elif not is1t9(context.json[pos]):
            return PARSE_STATE_INVALID_VALUE

        while isdigit(context.json[pos]):
            pos += 1

        if context.json[pos] == '.':
            isint = 0
            pos += 1
            if not isdigit(context.json[pos]):
                return PARSE_STATE_INVALID_VALUE
            while isdigit(context.json[pos]):
                if pos >= len(context.json):
                    break
                pos += 1

        if re.compile('[Ee]+').match(context.json[pos]):
            pos += 1
            if not isdigit(context.json[pos]):
                return PARSE_STATE_INVALID_VALUE
            while isdigit(context.json[pos]):
                pos += 1
    finally:
        numstr = ''.join(context.json[star_pos:pos])
        e_value.num = float(numstr)
        if isint:
            e_value.num = int(e_value.num)

        e_value.type = JTYPE.NUMBER
        context.json = context.json[pos:]
        context.pos = pos

        return PARSE_STATE_OK


def es_parse_string(context, e_value):
    pos = context.pos + 1
    e_value.str = ""
    try:
        while context.json[pos] != '"':
            # 处理转意字符
            if context.json[pos] == '\\':
                if context.json[pos + 1] == '\\':
                    e_value.str += '\\'
                elif context.json[pos + 1] == '\"':       # "
                    e_value.str += '\"'
                elif context.json[pos + 1] == 'n':
                    e_value.str += '\n'
                elif context.json[pos + 1] == 'b':
                    e_value.str += '\b'
                elif context.json[pos + 1] == 'f':
                    e_value.str += '\f'
                elif context.json[pos + 1] == 'r':
                    e_value.str += '\r'
                elif context.json[pos + 1] == 't':
                    e_value.str += '\t'
                else:
                    e_value.str += ''.join(context.json[pos])
                    pos += 1
                    continue
                pos += 2
            else:
                e_value.str += ''.join(context.json[pos])
                pos += 1

    finally:
        e_value.type = JTYPE.STRING
        context.json = context.json[pos + 1:]
        context.pos = 1
        if '\\u' in e_value.str:
            e_value.str = e_value.str.encode('latin-1').decode('unicode_escape')
        return PARSE_STATE_OK


def es_parse_array(context, e_value):
    e_value.array = []
    context.pos += 1
    while re.compile('[ \t\n]+').match(context.json[context.pos]):
        context.pos += 1
    pos = context.pos

    if context.json[pos] == ']':
        e_value.type == JTYPE.ARRAY
        return PARSE_STATE_OK
    while 1:
        es_parse_whitespace(context)
        son_e_value = EsValue(JTYPE.UNKNOW)
        res = es_parse_value(context, son_e_value)
        if res != PARSE_STATE_OK:
            break
        es_parse_whitespace(context)
        pos = 0

        if context.json[pos] == ',':
            pos += 1
            while context.json[pos] == ' ' or context.json[pos] == '\t' or context.json[pos] == '\n':
                pos += 1
            context.pos = pos
        elif context.json[pos] == ']':
            pos += 1
            context.pos = pos
            context.json = context.json[pos:]
            e_value.array.append(get_element(son_e_value))
            e_value.type = JTYPE.ARRAY
            return PARSE_STATE_OK

        e_value.array.append(get_element(son_e_value))
    return PARSE_STATE_INVALID_VALUE


def es_parse_object(context, e_value):
    e_value.obj = {}
    context.pos += 1
    while re.compile('[ \t\n]+').match(context.json[context.pos]):
        context.pos += 1
    pos = context.pos

    if context.json[pos] == '}':
        e_value.type == JTYPE.OBJECT
        return PARSE_STATE_OK
    while 1:
        son_key_typevalue = EsValue(JTYPE.UNKNOW)
        res = es_parse_value(context, son_key_typevalue)
        if res != PARSE_STATE_OK:
            break
        es_parse_whitespace(context)
        pos = 0

        son_value_typevalue = EsValue(JTYPE.UNKNOW)
        if context.json[pos] == ':':
            while re.compile('[ \t\n]+').match(context.json[context.pos]):
                context.pos += 1
            res2 = es_parse_value(context, son_value_typevalue)
            if res2 != PARSE_STATE_OK:
                break
            es_parse_whitespace(context)

        if context.json[pos] == ',':
            pos += 1
            while context.json[pos] == ' ' or context.json[pos] == '\t' or context.json[pos] == '\n':
                pos += 1
            context.pos = pos
        elif context.json[pos] == '}':
            pos += 1
            context.pos = pos
            context.json = context.json[pos:]
            e_value.obj[get_element(son_key_typevalue)] = get_element(son_value_typevalue)
            e_value.type = JTYPE.OBJECT
            return PARSE_STATE_OK

        e_value.obj[get_element(son_key_typevalue)] = get_element(son_value_typevalue)


def es_parse_value(context, e_value):
    """分析函数，解析字符串当前字符

    :param context:  string list
    :param e_value:  字符串解析后对应的 结构对象
    :return: 解析是否成功的状态码PARSE_STATE
    """
    if context.json[context.pos] == 't':
        return es_parse_literal(context, e_value, "true", JTYPE.TRUE)
    if context.json[context.pos] == 'f':
        return es_parse_literal(context, e_value, "false", JTYPE.FALSE)
    if context.json[context.pos] == 'n':
        return es_parse_literal(context, e_value, "null", JTYPE.NULL)

    if context.json[context.pos] == '"':
        return es_parse_string(context, e_value)
    if context.json[context.pos] == '[':
        return es_parse_array(context, e_value)
    if context.json[context.pos] == '{':
        return es_parse_object(context, e_value)

    if context.json[context.pos] == '\0':
        return PARSE_STATE_EXPECT_VALUE
    if re.compile('^[-+0-9]+').match(context.json[context.pos]):
        return es_parse_number(context, e_value)
    else:
        return PARSE_STATE_INVALID_VALUE


def es_parse(e_value, j_string):
    """用来将json string 解析成树型结构的对象

    :param e_value: json解析后的树型结构对象
    :param j_string: json的string
    :return: 解析是否成功的状态码PARSE_STATE
    """
    c = Context(j_string)
    v = e_value

    es_parse_whitespace(c)
    res = es_parse_value(c, v)

    if res == PARSE_STATE_OK:
        es_parse_whitespace(c)
        if c.json:
            res = PARSE_STATE_ROOT_NOT_SINGULAR
    return res


if __name__ == '__main__':
    while 1:
        print("input string : ")
        str1 = raw_input()      # python 2.7
        # str = input("input string = ")        #python 3X
        if len(str1) == 0:
            continue
        t = EsValue(JTYPE.UNKNOW)
        parse_state = es_parse(t, str1)

        if parse_state != 1:
            print("bad json\n")
            continue
        print(state_dict[parse_state] + " Json type is " + type_dict[gettype(t)] + ",  Output is: ")
        print(get_element(t))
        print('\n')
