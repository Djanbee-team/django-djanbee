# Style guide

This project follows the format suggested in PEP8.
This document serves as a cheat sheet for the most critical readability principles in this project.

*Each developer should configure a code formatter to automate the majority of this work.*

## Indentation
- Spaces should be used for indentation
- 4 spaces per level


```
# Correct:

# Aligned with opening delimiter.
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

# Add 4 spaces (an extra level of indentation) to distinguish arguments from the rest.
def long_function_name(
        var_one, var_two, var_three,
        var_four):
    print(var_one)

# Hanging indents should add a level.
foo = long_function_name(
    var_one, var_two,
    var_three, var_four)
```

Preferred alignment of closing bracket:

```
my_list = [
    1, 2, 3,
    4, 5, 6,
]
result = some_function_that_takes_arguments(
    'a', 'b', 'c',
    'd', 'e', 'f',
)
```

## Line length

- Maximum length 79

For flowing long blocks of text with fewer structural restrictions (docstrings or comments), the line length should be limited to 72 characters.

The preferred way of wrapping long lines is by using Python’s implied line continuation inside parentheses, brackets and braces. Long lines can be broken over multiple lines by wrapping expressions in parentheses. These should be used in preference to using a backslash for line continuation.

Backslashes may still be appropriate at times. For example, long, multiple with-statements could not use implicit continuation before Python 3.10, so backslashes were acceptable for that case:


```
with open('/path/to/some/file/you/want/to/read') as file_1, \
     open('/path/to/some/file/being/written', 'w') as file_2:
    file_2.write(file_1.read())
```

### Wrapping binary operators

```
# Correct:
# easy to match operators with operands
income = (gross_wages
          + taxable_interest
          + (dividends - qualified_dividends)
          - ira_deduction
          - student_loan_interest)
```

### Blank line rules

- Two blank lines around top-level functions and classes
- Single blank line between class methods
- Sparingly use blank lines within functions for logical sections

```
def helper():
    return "helper"


class Example:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return self.data.strip().upper()
```

## Imports

Imports should usually be on separate lines:

```
    # Correct:
    import os
    import sys
    # Wrong:
    import sys, os
```

Wildcard imports (from <module> import *) should be avoided, as they make it unclear which names are present in the namespace, confusing both readers and many automated tools.

## String formatting

- Use single quotes
- Avoid excessive use of whitespace

Immediately inside parentheses, brackets or braces:

```
# Correct:
spam(ham[1], {eggs: 2})
# Wrong:
spam( ham[ 1 ], { eggs: 2 } )
```

Between a trailing comma and a following close parenthesis:

```
# Correct:
foo = (0,)
# Wrong:
bar = (0, )
```

Immediately before a comma, semicolon, or colon:

```
# Correct:
if x == 4: print(x, y); x, y = y, x
# Wrong:
if x == 4 : print(x , y) ; x , y = y , x
```

Don’t use spaces around the = sign when used to indicate a keyword argument, or when used to indicate a default value for an unannotated function parameter:
```
# Correct:
def complex(real, imag=0.0):
    return magic(r=real, i=imag)
```

When combining an argument annotation with a default value, however, do use spaces around the = sign:
```
# Correct:
def munge(sep: AnyStr = None): ...
def munge(input: AnyStr, sep: AnyStr = None, limit=1000): ...
```

## Comments
Comments that contradict the code are worse than no comments. Always make a priority of keeping the comments up-to-date when the code changes!

Comments should be complete sentences. The first word should be capitalized, unless it is an identifier that begins with a lower case letter (never alter the case of identifiers!).

Use inline comments sparingly.

### Docstrings
Conventions for writing good documentation strings (a.k.a. “docstrings”) are immortalized in PEP 257.

Write docstrings for all public modules, functions, classes, and methods. Docstrings are not necessary for non-public methods, but you should have a comment that describes what the method does. This comment should appear after the def line.

*IMPORTANT! In this project public facing methods (e.g. base classes for managers) should have one-line docstring explanations*

*Private methods (e.g. implementation methods) should have docstrings with a concise description and explanation of return parameters*

*Further agreement on docstrings in core/commands/managers is needed*

## Naming

The following naming styles are commonly distinguished:

- b (single lowercase letter) - Loop counters (when context is very clear)
- B (single uppercase letter) - Mathematical variables (when context is very clear)
- lowercase - Package names
- lower_case_with_underscores  - Variable names/Function names/Method names/Module names/Instance variables
- UPPERCASE - (Generally avoid - use UPPER_CASE_WITH_UNDERSCORES instead)
- UPPER_CASE_WITH_UNDERSCORES - Constants/Global variables that act as constants
- CapitalizedWords (or CapWords, or CamelCase – so named because of the bumpy look of its letters [4]). This is also sometimes known as StudlyCaps. - Class names/Exception names/Type variable names

In addition, the following special forms using leading or trailing underscores are recognized (these can generally be combined with any case convention):  
- `_single_leading_underscore`: weak "internal use" indicator. E.g. `from M import *` does not import objects whose names start with an underscore. 
- `single_trailing_underscore_`: used by convention to avoid conflicts with Python keyword 
- `__double_leading_and_trailing_underscore__`: "magic" objects or attributes that live in user-controlled namespaces. E.g. `__init__`, `__import__` or `__file__`. Never invent such names; only use them as documented.  

Never use the characters `'l'` (lowercase letter el), `'O'` (uppercase letter oh), or `'I'` (uppercase letter eye) as single character variable names.  

In some fonts, these characters are indistinguishable from the numerals one and zero. When tempted to use `'l'`, use `'L'` instead.  

To better support introspection, modules should explicitly declare the names in their public API using the `__all__` attribute. Setting `__all__` to an empty list indicates that the module has no public API.  

Even with `__all__` set appropriately, internal interfaces (packages, modules, classes, functions, attributes or other names) should still be prefixed with a single leading underscore.  

Functions should return variable type and return type annotations.

