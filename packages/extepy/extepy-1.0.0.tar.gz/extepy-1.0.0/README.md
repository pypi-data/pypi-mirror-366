# extepy: Extension of Python Language

## Documentation

Docs: <https://extepy.github.io>

## Install

It can be installed with pip.

```shell
pip install --upgrade extepy
```

It works in both Python 2 and Python 3.

## Features

### Extension of `hashlib`

- `extepy.filehash(obj, method="sha256", batchsize=4096)` computes the hash value of a file.

Example:

```python
from extepy import filehash
filehash("test.txt")
```

### Extension of `importlib`

- `extepy.reload(obj, update_global=True, update_local=True)` provides advanced module and object reloading capabilities for Python, so that developer can modify code without restarting the interpreter.

This function solves key limitations of Python's built-in reloading functionality by:

- Supporting all import styles: `import X`, `import A as X`, `from A import X`, and `from A import B as X`;
- Automatically updating references without requiring reassignment;
- Offering granular control over namespace updates (global and/or local namespace).

Examples: Reload modules and objects.

```python
from mymodule import myfunction
# ... modify myfunction() in mymodule.py ...
from extepy import reload
reload(myfunction)  # reload function
```

```python
from mymodule import myfunction as myfunction1
# ... modify myfunction() in mymodule.py ...
from extepy import reload
reload(myfunction1)  # reload function alias
```

```python
import mymodule
# ... modify mymodule.py ...
from extepy import reload
reload(mymodule)  # reload module
reload("mymodule")  # reload module by module name
```

```python
import mymodule as mymodule1
# ... modify mymodule.py ...
from extepy import reload
reload(mymodule1)  # reload module alias
```

```python
from extepy import reload
from mymodule import myfunction as myfunction1, myfunction as myfunction2
# ... modify myfunction() in mymodule.py ...
reload(myfunction1)  # update both myfunction1 and myfunction2
```

Examples: Update selective namespaces

```python
from extepy import reload
myfunction = None  # global reference
def f():
    global myfunction
    from mymodule import myfunction
    # ... modify myfunction() in mymodule.py ...
    reload(myfunction, update_local=False)  # update global namespace only
```

```python
from extepy import reload
def f():
    from mymodule import myfunction
    # ... modify myfunction() in mymodule.py ...
    reload(myfunction, update_global=False)  # update the local namespace only
```
