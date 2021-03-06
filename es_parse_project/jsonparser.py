# -*- coding:utf-8 -*-
import re
import json

# n ➔ literal
# t ➔ true
# f ➔ false
# " ➔ string
# 0-9/- ➔ number
# [ ➔ array
# { ➔ object


JTYPE_NUMBER = 0
JTYPE_STRING = 1
JTYPE_ARRAY = 2
JTYPE_OBJECT = 3
JTYPE_NULL = 4
JTYPE_FALSE = 5
JTYPE_TRUE = 6
JTYPE_UNKNOW = 7

PARSE_STATE_OK = 1
PARSE_STATE_EXPECT_VALUE = 2
PARSE_STATE_INVALID_VALUE = 3
PARSE_STATE_ROOT_NOT_SINGULAR = 4


class MyException(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class EsValue(object):
    __slots__ = ('type', 'num', 'str', 'array', 'obj')
    
    def __init__(self):
        self.type = JTYPE_UNKNOW


class Context(object):
    def __init__(self, jstr):
        self.json = jstr
        self.pos = 0


def is1t9(ch):
    return re.compile('[1-9]+').match(ch)


def gettype(v):
    return v.type


def get_element(e_value):
    """获取解析后的value对象

    :param e_value: 传入json解析后的value对象
    :return: 返回value对象的类型 值
    """

    if e_value.type == JTYPE_STRING:
        return e_value.str
    if e_value.type == JTYPE_NUMBER:
        return e_value.num
    if e_value.type == JTYPE_ARRAY:
        return e_value.array
    if e_value.type == JTYPE_OBJECT:
        return e_value.obj
    if e_value.type == JTYPE_TRUE:
        return True
    if e_value.type == JTYPE_FALSE:
        return False
    if e_value.type == JTYPE_NULL:
        return None
    if e_value.type == JTYPE_UNKNOW:
        return "unknow"


def es_parse_whitespace(context):
    if not context.json:
        return
    pos = 0
    while re.compile('[\s]+').match(context.json[pos]):
        pos += 1
    context.json = context.json[pos:]


def es_parse_literal(context, literal, mytype):
    """ 解析字面量，包括null false true

    :param context: string list
    :param literal: 字面量匹配的 字符串
    :param mytype: 字面量的数据类型
    :return:
    """
    e_value = EsValue()
    if ''.join(context.json[context.pos:context.pos + len(literal)]) != literal:
        raise MyException("PARSE_STATE_INVALID_VALUE, literal error")
    e_value.type = mytype
    context.json = context.json[context.pos + len(literal):]
    return PARSE_STATE_OK, e_value


def es_parse_number(context):
    e_value = EsValue()
    star_pos = context.pos
    pos = context.pos
    isint = 1
    try:
        if re.compile('[-+0]+').match(context.json[pos]):   # 首位[+-0]
            pos += 1

        elif not is1t9(context.json[pos]):
            raise MyException("PARSE_STATE_INVALID_VALUE, number error")
        while context.json[pos].isdigit():
            pos += 1

        if context.json[pos] != '.' and context.json[pos] != 'e' and context.json[pos] != 'E':
            raise MyException("PARSE_STATE_INVALID_VALUE, number error")

        if context.json[pos] == '.':
            isint = 0
            pos += 1
            if not context.json[pos].isdigit():
                raise MyException("PARSE_STATE_INVALID_VALUE, number error")
            while context.json[pos].isdigit():
                if pos >= len(context.json):
                    break
                pos += 1

        if re.compile('[Ee]+').match(context.json[pos]):
            pos += 1
            if not context.json[pos].isdigit():
                raise MyException("PARSE_STATE_INVALID_VALUE, number error")
            while context.json[pos].isdigit():
                pos += 1

    finally:
        numstr = ''.join(context.json[star_pos:pos])
        e_value.num = float(numstr)
        if isint:
            e_value.num = int(e_value.num)

        e_value.type = JTYPE_NUMBER
        context.json = context.json[pos:]
        context.pos = pos - star_pos

        return PARSE_STATE_OK, e_value


def es_parse_string(context):
    charlist = {
        '\\"': '\"',
        "\\'": "\'",
        "\\b": "\b",
        "\\f": "\f",
        "\\r": "\r",
        "\\n": "\n",
        "\\t": "\t",
        "\\u": "u",
        "\\\\": "\\",
        "\\/": "/",
        "\\a": "\a",
        "\\v": "\v"
    }
    pos = context.pos + 1
    e_value = EsValue()
    e_value.str = ""
    try:
        while context.json[pos] != '"':
            # 处理转意字符
            if context.json[pos] == '\\':
                c = context.json[pos:pos + 2]
                if c in charlist:
                    e_value.str += charlist[c]
                else:
                    e_value.str += ''.join(context.json[pos])
                    pos += 1
                    continue
                pos += 2
            else:
                e_value.str += ''.join(context.json[pos])
                pos += 1

    finally:
        e_value.type = JTYPE_STRING
        context.json = context.json[pos + 1:]
        context.pos = 1
        if '/u' in e_value.str:
            e_value.str = e_value.str.encode('latin-1').decode('unicode_escape')
        return PARSE_STATE_OK, e_value


def es_parse_array(context):
    e_value = EsValue()
    e_value.array = []
    context.pos += 1
    while re.compile('[\s]+').match(context.json[context.pos]):
        context.pos += 1
    pos = context.pos

    if context.json[pos] == ']':
        e_value.type = JTYPE_ARRAY
        context.json = context.json[pos+1:]
        return PARSE_STATE_OK, e_value
    while 1:
        # es_parse_whitespace(context)
        son_e_state, son_e_value = es_parse_value(context)
        if son_e_state != PARSE_STATE_OK:
            break
        es_parse_whitespace(context)
        pos = 0

        if context.json[pos] == ',':
            pos += 1
            while re.compile('[\s]+').match(context.json[pos]):
                pos += 1
            context.pos = pos
        elif context.json[pos] == ']':
            pos += 1
            context.pos = pos
            context.json = context.json[pos:]
            e_value.array.append(get_element(son_e_value))
            e_value.type = JTYPE_ARRAY
            return PARSE_STATE_OK, e_value
        else:
            return PARSE_STATE_INVALID_VALUE, e_value

        e_value.array.append(get_element(son_e_value))
    return PARSE_STATE_INVALID_VALUE, e_value


def es_parse_object(context):
    e_value = EsValue()
    e_value.obj = {}
    context.pos += 1
    while re.compile('[\s]+').match(context.json[context.pos]):
        context.pos += 1
    pos = context.pos

    if context.json[pos] == '}':    # 检测合法空串
        context.json = context.json[pos + 1:]
        e_value.type = JTYPE_OBJECT
        return PARSE_STATE_OK, e_value
    while 1:
        obe_res = es_parse_value(context)
        son_key_state, son_key_typevalue = obe_res
        if son_key_state != PARSE_STATE_OK:
            break
        if not isinstance(get_element(son_key_typevalue), basestring) and \
           not isinstance(get_element(son_key_typevalue), int) and \
           not isinstance(get_element(son_key_typevalue), unicode):
            raise MyException("json object key %s error, must be string or int" % type(get_element(son_key_typevalue)))
        es_parse_whitespace(context)
        pos = 0

        # son_value_typevalue = EsValue()
        if context.json[pos] == ':':
            while re.compile('[\s]+').match(context.json[context.pos]):
                context.pos += 1
            res2 = es_parse_value(context)
            son_value_state, son_value_typevalue = res2
            if son_value_state != PARSE_STATE_OK:
                break
            es_parse_whitespace(context)
        else:
            raise MyException("this dict key [%s] lost value " % get_element(son_key_typevalue))

        if context.json[pos] == ',':
            pos += 1
            while re.compile('[\s]+').match(context.json[pos]):
                pos += 1
            context.pos = pos
        elif context.json[pos] == '}':
            pos += 1
            context.pos = pos
            context.json = context.json[pos:]
            e_value.obj[get_element(son_key_typevalue)] = get_element(son_value_typevalue)
            e_value.type = JTYPE_OBJECT
            return PARSE_STATE_OK, e_value
        elif son_value_typevalue.type == 7:
            raise MyException("PARSE_STATE_INVALID_VALUE, object format error")

        e_value.obj[get_element(son_key_typevalue)] = get_element(son_value_typevalue)


def es_parse_value(context):
    """分析函数，解析字符串当前字符

    :param context:  string list
    :return: 解析是否成功的状态码PARSE_STATE
    """
    e_value = EsValue()
    if context.json[context.pos] == 't':
        return es_parse_literal(context, "true", JTYPE_TRUE)
    if context.json[context.pos] == 'f':
        return es_parse_literal(context, "false", JTYPE_FALSE)
    if context.json[context.pos] == 'n':
        return es_parse_literal(context, "null", JTYPE_NULL)

    if context.json[context.pos] == '"':
        return es_parse_string(context)
    if context.json[context.pos] == '[':
        return es_parse_array(context)
    if context.json[context.pos] == '{':
        return es_parse_object(context)

    if context.json[context.pos] == '\0':
        return PARSE_STATE_EXPECT_VALUE
    if re.compile('^[-+\d]+').match(context.json[context.pos]):
        return es_parse_number(context)
    else:
        return PARSE_STATE_INVALID_VALUE, e_value


def es_loads(j_string):
    """用来将json string 解析成树型结构的对象

    :param j_string: json的string
    :return: 解析后的结构
    """
    c = Context(j_string)

    try:

        es_parse_whitespace(c)
        parse_res = es_parse_value(c)

        if parse_res[0] == PARSE_STATE_OK:
            es_parse_whitespace(c)
            if c.json:
                raise MyException("PARSE_STATE_INVALID_VALUE,format error")
        else:
            raise MyException("PARSE_STATE_INVALID_VALUE")

        return get_element(parse_res[1])

    except MyException, e:
        print(e.message)
    except (TypeError, SyntaxError), e:
        print(e)


def es_load(filepath):
    """

    :param filepath: load的文件名
    :return: 解析后的Python object
    """
    f = open(filepath, 'r')
    fread = unicode(f.read(), "UTF-8")
    return es_loads(fread)


def es_dumps(obj):
    obj_str = ""

    if isinstance(obj, bool):
        if obj is True:
            obj_str += "True"
        else:
            obj_str += "False"
    elif obj is None:
        obj_str += "null"

    elif isinstance(obj, basestring):
        for ch in obj.decode('utf-8'):
            if u'\u4e00' <= ch <= u'\u9fff':
                obj_str += "\"" + repr(obj.decode('UTF-8')) + "\""
                break
        else:
            obj_str += "\"" + obj + "\""

    elif isinstance(obj, list):
        obj_str += '['
        if len(obj):
            for i in obj:
                obj_str += es_dumps(i) + ", "
            obj_str = obj_str[:-2]
        obj_str += ']'

    elif isinstance(obj, int) or isinstance(obj, float):     # number
        obj_str += str(obj)

    elif isinstance(obj, dict):
        obj_str += '{'
        if len(obj):
            for (k, v) in obj.items():
                obj_str += es_dumps(k) + ": "
                obj_str += es_dumps(v) + ", "
            obj_str = obj_str[:-2]
        obj_str += '}'

    return obj_str


def es_dump(obj, filename):
    """Python object encode to string, save file

    :param obj: Python对象
    :param filename: 保存文件名
    :return: object string
    """
    f = open(filename, 'w')
    fwrite = es_dumps(obj)
    f.write(fwrite[1:-1])
    return fwrite


if __name__ == '__main__':
    data = {
        "姓名": "jack",
        "title": "Design Patterns",
        "subtitle": "Elements of Reusable Object-Oriented Software",
        "author":
            [
                "Erich Gamma",
                "Richard Helm",
                "Ralph Johnson",
                "John Vlissides"],
        "year": -2009,
        "weight": 1.8,
        "hardcover": 1,
        "publisher": {
            "Company": "Pearson Education",
            "Country": "India"
        },
        "website": 2
    }

    datastring = json.dumps(data)
    res = es_loads(datastring)
    print(res)
