# PyFunc: Functional Programming Pipeline for Python

PyFunc is a Python library that brings functional programming fluency to Python, enabling chainable, composable, lazy, and debuggable operations on various data structures.

## ✨ Features

- **🔗 Chainable Operations**: Method chaining for readable data transformations
- **🎯 Placeholder Syntax**: Use `_` to create lambda-free expressions  
- **⚡ Lazy Evaluation**: Operations computed only when needed
- **🔄 Function Composition**: Compose functions with `>>` and `<<` operators
- **📊 Rich Data Operations**: Works with scalars, lists, dicts, generators
- **🐛 Built-in Debugging**: Debug and trace pipeline execution
- **🔧 Extensible**: Register custom types and extend functionality
- **📝 Type Safe**: Full type hints and generic support

## 🚀 Quick Start

```bash
pip install pyfunc-pipeline
```

```python
from pyfunc import pipe, _

# Basic pipeline
result = pipe([1, 2, 3, 4]).filter(_ > 2).map(_ * 10).to_list()
# Result: [30, 40]

# String processing  
result = pipe("hello world").explode(" ").map(_.capitalize()).implode(" ").get()
# Result: "Hello World"

# Function composition
double = _ * 2
square = _ ** 2
composed = double >> square  # square(double(x))

result = pipe(5).apply(composed).get()
# Result: 100
```

## 🎯 Core Concepts

### Pipeline Chaining

Every value can be lifted into a pipeline for transformation:

```python
from pyfunc import pipe, _

# Numbers
pipe([1, 2, 3, 4]).filter(_ > 2).map(_ ** 2).sum().get()
# Result: 25

# Strings  
pipe("  hello world  ").apply(_.strip().title()).explode(" ").to_list()
# Result: ['Hello', 'World']

# Dictionaries
pipe({"a": 1, "b": 2}).map_values(_ * 10).get()
# Result: {"a": 10, "b": 20}
```

### Placeholder Syntax

The `_` placeholder creates reusable, composable expressions:

```python
from pyfunc import _

# Arithmetic operations
double = _ * 2
add_ten = _ + 10

# Method calls
normalize = _.strip().lower()

# Comparisons  
is_positive = _ > 0

# Composition
process = double >> add_ten  # add_ten(double(x))
```

### Lazy Evaluation

Operations are lazy by default - perfect for large datasets:

```python
# Processes only what's needed from 1 million items
result = pipe(range(1_000_000)).filter(_ > 500_000).take(5).to_list()
```

## 📚 Rich API

### String Operations
```python
pipe("hello,world").explode(",").map(_.capitalize()).implode(" & ").get()
# "Hello & World"

pipe("Hello {name}!").template_fill({"name": "PyFunc"}).get()  
# "Hello PyFunc!"
```

### Dictionary Operations
```python
users = {"alice": 25, "bob": 30}
pipe(users).map_values(_ + 5).map_keys(_.title()).get()
# {"Alice": 30, "Bob": 35}
```

### Advanced Transformations
```python
# Group by
data = [{"name": "Alice", "dept": "Eng"}, {"name": "Bob", "dept": "Sales"}]
pipe(data).group_by(_["dept"]).get()

# Sliding windows
pipe([1, 2, 3, 4, 5]).window(3).to_list()
# [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

# Combinations
pipe([1, 2, 3]).combinations(2).to_list()  
# [(1, 2), (1, 3), (2, 3)]
```

### Side Effects & Debugging
```python
pipe([1, 2, 3, 4])
    .debug("Input")
    .filter(_ > 2) 
    .debug("Filtered")
    .map(_ ** 2)
    .to_list()
```

## 🌟 Real-World Example

```python
from pyfunc import pipe, _

# Process user data
users = [
    {"name": "  Alice  ", "age": 30, "scores": [85, 92, 78]},
    {"name": "BOB", "age": 25, "scores": [90, 88, 95]},
    {"name": "charlie", "age": 35, "scores": [75, 80, 85]},
]

top_performers = (
    pipe(users)
    .map(lambda user: {
        "name": pipe(user["name"]).apply(_.strip().title()).get(),
        "age": user["age"], 
        "avg_score": pipe(user["scores"]).sum().get() / len(user["scores"])
    })
    .filter(lambda user: user["avg_score"] > 80)
    .sort(key=lambda user: user["avg_score"], reverse=True)
    .to_list()
)

print(top_performers)
# [{'name': 'Bob', 'age': 25, 'avg_score': 91.0}, 
#  {'name': 'Alice', 'age': 30, 'avg_score': 85.0}]
```

## 📖 Documentation

- **[Complete Documentation](DOCUMENTATION.md)** - Full API reference and examples
- **[Examples](examples/)** - Real-world usage examples  
- **[Changelog](CHANGELOG.md)** - Version history and updates

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
