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

def token(method:Choice('xkcd', 'short')='xkcd', entropy:int=70):
    "Generate a cryptographic token with a given entropy."
    if method == 'xkcd':
	return xkcd(entropy)
    else:
	return alphanumeric(entropy)

cli(token)()
```

You can even generate CLIs for a whole module (or any other object with function attributes):

```python
import example
from cli import cli

# convert_numbers automatically converts strings to int, float or complex so
# you don't have to annotate all the functions in a module. YMMV.
cli(example, convert_numbers=True)()

# You can get a reference to the current module with sys.modules[__name__]
```
