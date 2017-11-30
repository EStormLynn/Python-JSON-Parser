import unittest
from jsonparser import *

class TestEs_parse(unittest.TestCase):
    def test_es_parse(self):
        pass

    def testnum(self):
        print("\n------------test number-----------")
        self.assertEqual(self.num("24"), 24)
        self.assertEqual(self.num("1e4"), 10000)
        self.assertEqual(self.num("-1.5"), -1.5)
        self.assertEqual(self.num("1.5e3"), 1500)

    def testliteral(self):
        print("\n------------test literal----------")
        self.assertEqual(self.literal("      null"), JTYPE.NULL)
        self.assertEqual(self.literal(" \t null"), JTYPE.NULL)
        self.assertEqual(self.literal(" \n null"), JTYPE.NULL)
        self.assertEqual(self.literal(" \n false"), JTYPE.FALSE)
        self.assertEqual(self.literal("  true"), JTYPE.TRUE)

    def teststring(self):
        print("\n------------test string----------")
        self.assertEqual(self.string("\" \\\\line1\\nline2 \""), JTYPE.STRING)         # input \\  is \
        self.assertEqual(self.string("\"  abc\\def\""), JTYPE.STRING)
        self.assertEqual(self.string("\"      null\""), JTYPE.STRING)
        self.assertEqual(self.string("\"hello world!\""), JTYPE.STRING)
        self.assertEqual(self.string("\"   \u751F\u5316\u5371\u673A  \""), JTYPE.STRING)

    def testarray(self):
        print("\n------------test array----------")
        self.assertEqual(self.array("[13,2,3]"), JTYPE.ARRAY)
        self.assertEqual(self.array("[13,[2,3]]"), JTYPE.ARRAY)
        self.assertEqual(self.array("[  13  , [ 2, 3],[4,5]]"), JTYPE.ARRAY)
        self.assertEqual(self.array("[13,true]"), JTYPE.ARRAY)
        self.assertEqual(self.array("[[11,12],[21,22]]"), JTYPE.ARRAY)
        self.assertEqual(self.array("[[11,  [111  ,112],  13],[21,22]]"), JTYPE.ARRAY)
        self.assertEqual(self.array("[[11,{\"name\":\"zz\",\"age\":24},13],[21,22]]"), JTYPE.ARRAY)

    def testobject(self):
        print("\n------------test object----------")
        self.assertEqual(self.array("{\"name\":\"zz\",\"age\":24}"), JTYPE.OBJECT)
        self.assertEqual(self.array("{\"name\":\"zz\",\"daylist\":[6,7]}"), JTYPE.OBJECT)
        self.assertEqual(self.array("{\"name\":{\"firstname\":\"zhao\",\"lastname\":\"zhang\"},\"age\":24,\"frient\":[1,2,3]}"), JTYPE.OBJECT)


    def object(self,str):
        t = es_value(JTYPE.UNKNOW)
        print("input string = " + str)
        print(es_parse(t, str), gettype(t), getelement(t), "\n")
        return gettype(t)

    def array(self, str):
        t = es_value(JTYPE.UNKNOW)
        print("input string = " + str)
        print(es_parse(t, str), gettype(t), getelement(t), "\n")
        return gettype(t)


    def string(self, str):
        t = es_value(JTYPE.UNKNOW)
        print("input string = " + str)
        print(es_parse(t, str), gettype(t), getelement(t), "\n")
        return gettype(t)

    def literal(self, str):
        t = es_value(JTYPE.UNKNOW)
        print("input string = " + str)
        print(es_parse(t, str), gettype(t),"\n")
        return gettype(t)


    def num(self,str):
        t = es_value(JTYPE.UNKNOW)
        print("input string = " + str)
        print(es_parse(t, str), gettype(t), getelement(t), "\n")
        return getelement(t)


if __name__ == '__main__':
    unittest.main()
