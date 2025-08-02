# textstatslite

Simple Python package to compute statistics on a text:
- Word count
- Sentence count
- Character count
- Average word length
- Most frequent words

## Usage

```python
from textstatslite import core

text = "Python is simple. Python is powerful."
print(core.count_words(text))
print(core.most_frequent_words(text))
