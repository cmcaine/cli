# CLI

> An extremely easy to use library to generate python CLIs from functions through introspection.

Automatically generate the equivalent of this:

```python
import argparse
parser = argparse.ArgumentParser(description="Generate a cryptographic token with a given entropy.")
parser.add_argument('method', nargs='?', default='xkcd', choices=('xkcd', 'short'))
parser.add_argument('entropy', nargs='?', default=70, type=int)
args = parser.parse_args()

if args.method == 'xkcd':
    print(xkcd(args.entropy))
else:
    print(alphanumeric(args.entropy))
```

from this:

```python
from cli import Choice, cli

def token(method:Choice('xkcd', 'short')='xkcd', entropy=70):
    "Generate a cryptographic token with a given entropy."
    if method == 'xkcd':
	return xkcd(entropy)
    else:
	return alphanumeric(entropy)

cli(token)()
```

Keyword arguments (optional or mandatory) are supported as is one varargs argument per function. Arguments will be automatically converted into the type of their default argument (if it is not None) or their type annotation.

You can even generate CLIs for a whole module (or any other object with function attributes):

```python
import example
from cli import cli

# convert_numbers automatically converts strings to int, float or complex so
# you don't have to annotate all the functions in a module. YMMV.
cli(example, convert_numbers=True)()

# You can get a reference to the current module with sys.modules[__name__]
```

## Code quality

The code is very short, clearly documented inline and all advertised features are tested.
