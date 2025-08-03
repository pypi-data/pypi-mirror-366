# rlist
`rlist` is a small Python library that provides the `rlist` type (record list), which 
is a plain Python list extended with a few handy methods for in-place manipulation.  
The methods are inspired by the corresponding Ruby array methods.  

**Documentation:** https://maxcode123.github.io/rlist/  

**Example**
```py
from rlist import rlist

people = [
  {"age": 29, "name": "John", "sex": "M"},
  {"age": 67, "name": "Paul", "sex": "M"},
  {"age": 39, "name": "George", "sex": "M"},
  {"age": 18, "name": "Mary", "sex": "F"},
  {"age": 45: "name": "Margaret", "sex":  "F"}
]

people.select(lambda p: p["age"] > 30).reject(lambda p: "l" in p["name"]).map(lambda p: p["sex"])
```


## Installation

```console
pip install record-list
```
