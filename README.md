# Python实现JSON生成器和递归下降解释器

## 目标
从零开始写一个JSON的解析器，特征如下：
* 符合标准的JSON解析器和生成器
* 手写递归下降的解释器（recursive descent parser）
* 使用Python语言（3.6）
* 解释器和生成器少于500行
* 使用cProfile完成性能分析和优化

## 实现内容
- [x] 解析字面量(true false null)
- [x] 解析数字
- [x] 解析字符串
- [x] 解析Unicode
- [x] 解析数组
- [x] 解析对象
- [x] 单元测试
- [x] 生成器
- [ ] cProfile性能优化

## 详细介绍
### JSON是什么
JSON（JavaScript Object Notation）是一个用于数据交换的文本格式，参考ecma标准,[JSON Data Interchange Format](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf),先看一段JSON的数据格式:
```JSON
{
    "title": "Design Patterns",
    "subtitle": "Elements of Reusable Object-Oriented Software",
    "author": [
        "Erich Gamma",
        "Richard Helm",
        "Ralph Johnson",
        "John Vlissides"
    ],
    "year": 2009,
    "weight": 1.8,
    "hardcover": true,
    "publisher": {
        "Company": "Pearson Education",
        "Country": "India"
    },
    "website": null
}
```
在json的树状结构中

* null: 表示为 null
* boolean: 表示为 true 或 false
* number: 一般的浮点数表示方式，在下一单元详细说明
* string: 表示为 "..."
* array: 表示为 [ ... ]
* object: 表示为 { ... }


### 实现解释器
es_parser 是一个手写的递归下降解析器（recursive descent parser）。由于 JSON 语法特别简单，可以将分词器（tokenizer）省略，直接检测下一个字符，便可以知道它是哪种类型的值，然后调用相关的分析函数。对于完整的 JSON 语法，跳过空白后，只需检测当前字符：
```
n ➔ literal
t ➔ true
f ➔ false
" ➔ string
0-9/- ➔ number
[ ➔ array
{ ➔ object
```

对于json的typevalue和json string编写了这样2个类
```python
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
```

以解析多余的空格，制表位，换行为例：
```python
def es_parse_whitespace(context):
    if not context.json:
        return
    pos = 0
    while context.json[pos] == ' ' or context.json[pos] == '\t' or context.json[pos] == '\n':
        pos += 1
    context.json = context.json[pos:]
```


### 解析字面量
字面量包括了false，true，null三种。
```python
def es_parse_literal(context, typevalue, literal, type):
    if ''.join(context.json[context.pos:context.pos + len(literal)]) != literal:
        return PARSE_STATE.INVALID_VALUE
    else:
        typevalue.type = type
        context.json = context.json[context.pos + len(literal):]
        return PARSE_STATE.OK

def es_parse_value(context, typevalue):
    if context.json[context.pos] == 't':
        return es_parse_literal(context, typevalue, "true", JTYPE.TRUE)
    if context.json[context.pos] == 'f':
        return es_parse_literal(context, typevalue, "false", JTYPE.FALSE)
    if context.json[context.pos] == 'n':
        return es_parse_literal(context, typevalue, "null", JTYPE.NULL)
```


### 解析数字
JSON number类型，number 是以十进制表示，它主要由 4 部分顺序组成：负号、整数、小数、指数。只有整数是必需部分。

JSON 可使用科学记数法，指数部分由大写 E 或小写 e 开始，然后可有正负号，之后是一或多个数字（0-9）。

JSON 标准 [ECMA-404](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-404.pdf) 采用图的形式表示语法，可以更直观地看到解析时可能经过的路径：

![]()

python是一种动态语言，所以es_value中num可以是整数也可以是小数，
```python
class es_value():
    def __init__(self, type):
        self.type = type
        self.num = 0
```

python对于string类型，可以强制转换成float和int，但是int(string)无法处理科学记数法的情况，所以统一先转成float在转成int
```python
typevalue.num = float(numstr)
if isint:
    typevalue.num = int(typevalue.num)
```

实现的单元测试包含：
```python
def testnum(self):
    print("\n------------test number-----------")
    self.assertEqual(self.num("24"), 24)
    self.assertEqual(self.num("1e4"), 10000)
    self.assertEqual(self.num("-1.5"), -1.5)
    self.assertEqual(self.num("1.5e3"), 1500)
```

### 解析字符串