import json
from enum import Enum

# n ➔ literal
# t ➔ true
# f ➔ false
# " ➔ string
# 0-9/- ➔ number
# [ ➔ array
# { ➔ object

# a = {"name": "zz", "age": 24}
# b = json.dumps(a)
# c = json.loads(b)
# print(type(a), type(b), type(c))
#
# print(a, b, c)

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


class PARSE_STATE(Enum):
    OK = 0,
    EXPECT_VALUE = 1
    INVALID_VALUE = 2
    ROOT_NOT_SINGULAR = 3


class es_value():
    def __init__(self, type):
        self.type = type
        self.num = 0
        self.str = ""
        self.array = []
        self.obj = {}


class context(object):
    def __init__(self, jstr):
        self.json = list(jstr)
        self.pos = 0


def isdigit(ch):
    return 1 if '0' <= ch <= '9' else 0


def is1t9(ch):
    return 1 if '1' <= ch <= '9' else 0


# 获取类型
def gettype(v):
    assert v
    return v.type

def getstring(typevalue):
    if typevalue.type == JTYPE.STRING:
        return typevalue.str

def getnumber(typevalue):
    if typevalue.type == JTYPE.NUMBER:
        return typevalue.num

def getelement(typevalue):
    if typevalue.type == JTYPE.STRING:
        return typevalue.str
    if typevalue.type == JTYPE.NUMBER:
        return typevalue.num
    if typevalue.type == JTYPE.ARRAY:
        return typevalue.array
    if typevalue.type == JTYPE.OBJECT:
        return typevalue.obj
    if typevalue.type == JTYPE.TRUE:
        return "true"
    if typevalue.type == JTYPE.FALSE:
        return "false"
    if typevalue.type == JTYPE.NULL:
        return "null"

def es_parse_whitespace(context):
    if not context.json:
        return
    pos = 0
    while context.json[pos] == ' ' or context.json[pos] == '\t' or context.json[pos] == '\n':
        pos += 1
    context.json = context.json[pos:]


def es_parse_null(context, typevalue):
    if ''.join(context.json[0:4]) != "literal":
        return PARSE_STATE.INVALID_VALUE
    else:
        typevalue.type = JTYPE.NULL
        context.json = context.json[4:]
        return PARSE_STATE.OK


def es_parse_true(context, typevalue):
    if ''.join(context.json[0:4]) != "true":
        return PARSE_STATE.INVALID_VALUE
    else:
        typevalue.type = JTYPE.TRUE
        context.json = context.json[4:]
        return PARSE_STATE.OK


def es_parse_false(context, typevalue):
    if ''.join(context.json[0:5]) != "false":
        return PARSE_STATE.INVALID_VALUE
    else:
        typevalue.type = JTYPE.FALSE
        context.json = context.json[5:]
        return PARSE_STATE.OK


def es_parse_literal(context, typevalue, literal, type):
    if ''.join(context.json[context.pos:context.pos + len(literal)]) != literal:
        return PARSE_STATE.INVALID_VALUE
    else:
        typevalue.type = type
        context.json = context.json[context.pos + len(literal):]
        return PARSE_STATE.OK


def es_parse_number(context, typevalue):
    starpos =context.pos
    pos = context.pos
    try:
        isint = 1
        if context.json[pos] == '-':
            pos += 1
        if context.json[pos] == '0':
            pos += 1
        elif not is1t9(context.json[pos]):
            return PARSE_STATE.INVALID_VALUE

        while isdigit(context.json[pos]):
            pos += 1

        if context.json[pos] == '.':
            isint = 0
            pos += 1
            if not isdigit(context.json[pos]):
                return PARSE_STATE.INVALID_VALUE
            while isdigit(context.json[pos]):
                if pos >= len(context.json):
                    break
                pos += 1

        if context.json[pos] == 'e' or context.json[pos] == 'E':
            pos += 1
            if not isdigit(context.json[pos]):
                return PARSE_STATE.INVALID_VALUE
            while isdigit(context.json[pos]):
                pos += 1
    finally:
        numstr = ''.join(context.json[starpos:pos])
        typevalue.num = float(numstr)
        if isint:
            typevalue.num = int(typevalue.num)

        typevalue.type = JTYPE.NUMBER
        context.json = context.json[pos:]
        context.pos = pos

        return PARSE_STATE.OK


def es_parse_string(context, typevalue):
    pos = context.pos + 1
    try:
        while context.json[pos] != '"':
            # 处理转意字符
            if context.json[pos] == '\\':
                if context.json[pos + 1] == '\\':
                    typevalue.str += '\\'
                elif context.json[pos + 1] == '\"':       # "
                    typevalue.str += '\"'
                elif context.json[pos + 1] == 'n':
                    typevalue.str += '\n'
                elif context.json[pos + 1] == 'b':
                    typevalue.str += '\b'
                elif context.json[pos + 1] == 'f':
                    typevalue.str += '\f'
                elif context.json[pos + 1] == 'r':
                    typevalue.str += '\r'
                elif context.json[pos + 1] == 't':
                    typevalue.str += '\t'
                else:
                    typevalue.str += ''.join(context.json[pos])
                    pos += 1
                    continue
                pos += 2
            else:
                typevalue.str += ''.join(context.json[pos])
                pos += 1

    finally:
        typevalue.type = JTYPE.STRING
        # typevalue.str = ''.join(context.json[context.pos + 1:pos])
        context.json = context.json[pos + 1:]
        context.pos = 1
        return PARSE_STATE.OK


def es_parse_array(context, typevalue):
    pos = context.pos + 1
    context.pos = pos
    if context.json[pos] == ']':
        typevalue.type == JTYPE.ARRAY
        typevalue.array == []
        return PARSE_STATE.OK
    while 1 :
        son_typevalue = es_value(JTYPE.UNKNOW)
        res = es_parse_value(context, son_typevalue)
        if res != PARSE_STATE.OK:
            break
        es_parse_whitespace(context)
        pos = 0

        if context.json[pos] == ',':
            pos += 1
            context.pos = pos
        elif context.json[pos] == ']':
            pos += 1
            context.pos = pos
            context.json = context.json[pos:]
            typevalue.array.append(getelement(son_typevalue))
            typevalue.type = JTYPE.ARRAY
            return PARSE_STATE.OK

        typevalue.array.append(getelement(son_typevalue))



    pass


def es_parse_object(context, typevalue):
    pos = context.pos + 1
    context.pos = pos
    obj = {}
    es_parse_whitespace(context)

    if context.json[pos] == '}':
        typevalue.type == JTYPE.OBJECT
        typevalue.obj == {}
        return PARSE_STATE.OK
    while 1 :
        son_key_typevalue = es_value(JTYPE.UNKNOW)
        res = es_parse_value(context, son_key_typevalue)
        if res != PARSE_STATE.OK:
            break
        es_parse_whitespace(context)
        pos = 0

        son_value_typevalue = es_value(JTYPE.UNKNOW)
        if context.json[pos] == ':':
            res2 = es_parse_value(context,son_value_typevalue)
            es_parse_whitespace(context)


        if context.json[pos] == ',':
            pos += 1
            context.pos = pos
        elif context.json[pos] == '}':
            pos += 1
            context.pos = pos
            context.json = context.json[pos:]
            typevalue.obj[getelement(son_key_typevalue)] = getelement(son_value_typevalue)
            typevalue.type = JTYPE.OBJECT
            return PARSE_STATE.OK

        typevalue.obj[getelement(son_key_typevalue)] = getelement(son_value_typevalue)

        # typevalue.array.append(getelement(son_key_typevalue))

    pass


def es_parse_value(context, typevalue):
    if context.json[context.pos] == 't':
        return es_parse_literal(context, typevalue, "true", JTYPE.TRUE)
    if context.json[context.pos] == 'f':
        return es_parse_literal(context, typevalue, "false", JTYPE.FALSE)
    if context.json[context.pos] == 'n':
        return es_parse_literal(context, typevalue, "null", JTYPE.NULL)

    if context.json[context.pos] == '"':
        return es_parse_string(context, typevalue)
    if context.json[context.pos] == '[':
        return es_parse_array(context, typevalue)
    if context.json[context.pos] == '{':
        return es_parse_object(context, typevalue)

    if context.json[context.pos] == '\0':
        return PARSE_STATE.EXPECT_VALUE
    else:
        return es_parse_number(context, typevalue)
    pass


# 解析json
def es_parse(typevalue,j_string):
    assert typevalue

    c = context(j_string)
    v = typevalue

    es_parse_whitespace(c)
    res = es_parse_value(c,v)

    if res == PARSE_STATE.OK:
        es_parse_whitespace(c)
        if c.json :
            ret = PARSE_STATE.ROOT_NOT_SINGULAR

    return res


# str = "[1,3]"
# t = es_value(JTYPE.UNKNOW)
# print("input string = " + str)
# print(es_parse(t, str), gettype(t),"\n")
