# -*- coding:utf-8 -*-
from __future__ import print_function
import unittest
from jsonparser import *

class TestEs_parse(unittest.TestCase):
    def test_es_parse(self):
        pass

    def test_constum(self):
        dr="{1:4}"
        dstr1 = """[
                    1,2,3,
                    4,
                    [5, 6, 7],
                    {1:2, 3:4}
                    ]"""
        dstr2 = """ {1,2,3}"""
        dstr3 = "{[1,2]:,3}"
        print(es_parse(dstr1))

        print(es_parse(dstr2))
        print(es_parse(dstr3))


    def testnum(self):
        print("\n------------test number-----------")
        self.assertEqual(type(self.num("24")), type(1))
        self.assertEqual(type(self.num("1e4")), type(10000))
        self.assertEqual(type(self.num("-1.5")), type(-1.5))
        self.assertEqual(type(self.num("1.5e3")), type(1.500))

    def testliteral(self):
        print("\n------------test literal----------")
        self.assertEqual(type(self.literal("      null")), type(None))
        self.assertEqual(type(self.literal(" \t null")), type(None))
        self.assertEqual(type(self.literal(" \n false")), type(False))
        self.assertEqual(type(self.literal(" \n null")), type(None))
        self.assertEqual(type(self.literal("  true")), type(True))

    def teststring(self):
        print("\n------------test string----------")
        self.assertEqual(type(self.string("\" \\\\line1\\nline2 \"")), type(u"string"))         # input \\  is \
        self.assertEqual(type(self.string("\"  abc\\def\"")), type(u"string"))
        self.assertEqual(type(self.string("\"      null\"")), type(u"string"))
        self.assertEqual(type(self.string("\"hello world!\"")), type(u"string"))
        self.assertEqual(type(self.string("\"   \u751F\u5316\u5371\u673A  \"")), type(u"string"))

    def testarray(self):
        print("\n------------test array----------")
        self.assertEqual(type(self.array("[13,2,3]")), type([]))
        self.assertEqual(type(self.array("[13,[2,3]]")), type([]))
        self.assertEqual(type(self.array("[  13  , [ 2, 3],[4,5]]")), type([]))
        self.assertEqual(type(self.array("[13,true]")), type([]))
        self.assertEqual(type(self.array("[[11,12],[21,22]]")), type([]))
        self.assertEqual(type(self.array("[[11,  [111  ,112],  13],[21,22]]")), type([]))
        self.assertEqual(type(self.array("[[11,{\"name\":\"zz\",\"age\":24},13],[21,22]]")), type([]))

    def testobject(self):
        print("\n------------test object----------")
        self.assertEqual(type(self.array("{\"name\":\"zz\",\"age\":24}")), type({}))
        self.assertEqual(type(self.array("{\"name\":\"zz\",\"daylist\":[6,7]}")), type({}))
        self.assertEqual(type(self.array("{\"name\":{\"firstname\":\"zhao\",\"lastname\":\"zhang\"},\"age\":24,\"frient\":[1,2,3]}")), type({}))


    def object(self,str):
        print("input string = " + str)
        res = es_parse(str)
        print("output: ", end = " ")
        print(res)
        return res

    def array(self, str):
        print("input string = " + str)
        res = es_parse(str)
        print("output: ", end = " ")
        print(res)
        return res


    def string(self, str):
        print("input string = " + str)
        res = es_parse(str)
        print("output: ", end = " ")
        print(res)
        return res

    def literal(self, str):
        print("input string = " + str)
        res = es_parse(str)
        print("output: ", end = " ")
        print(res)
        return res


    def num(self,str):
        print("input string = " + str)
        res = es_parse(str)
        print("output: ", end = " ")
        print(res)
        return res

if __name__ == '__main__':
    unittest.main()

