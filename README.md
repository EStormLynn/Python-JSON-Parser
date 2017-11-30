# Python实现JSON生成器和递归下降解释器

## 目标
从零开始写一个JSON的解析器，特征如下：
* 符合标准的JSON解析器和生成器
* 手写递归下降的解释器（recursive descent parser）
* 使用Python语言（3.6）
* 解释器和生成器少于500行

## 实现内容
- [x] 解析字面量(true false null)
- [x] 解析数字
- [x] 解析字符串
- [ ] 解析Unicode
- [x] 解析数组
- [ ] 解析对象
- [ ] 生成器

## 详细介绍
### JSON是什么
JSON（JavaScript Object Notation）是一个用于数据交换的文本格式，先看一段JSON的数据格式，:
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