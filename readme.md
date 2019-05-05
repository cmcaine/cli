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

Explicitly, `cli(token)` creates a new function that accepts an array of strings, parses *and automatically converts* them according to rules derived from the function signature, applies the parsed arguments to the original `token` and prints the output. `cli(token)()` calls that function using the default `sys.argv`.

## But wait, there's more!

Keyword arguments (optional or mandatory) are supported as is one varargs argument per function. **Arguments will be automatically converted** into the type of their default argument (if it is not None) or their type annotation.

The exact mapping from function signature to argparse rules is specified in the docstring of `generate_parser()`, but the idea is that it should be fairly intuitive.

You can even generate CLIs for a whole module (or any other object with function attributes):

```python
import example
from cli import cli, opportunistic, coerce_number

# You can use opportunistic(coerce_number) to convert any string that looks
# like a number to a number so you don't have to annotate all the functions in a
# module. YMMV.
cli(example, default_type=opportunistic(coerce_number))()

# If you want one, you can get a reference to the current module with
# sys.modules[__name__]
```

## Lower level API

`generate_parser(your_function_here)` will return an `argparse.Parser` instance. `apply_namespace(your_function_here, namespace)` will apply a namespace object (as returned by `parser.parse_args()`) to a function.

`generate_parser_obj(your_module_or_class_here)` will return an `argparse.Parser` with one subparser per callable on the

## Code quality

The code is very short, clearly documented inline and all advertised features are tested.

## Reference

Function signature interpretation:
    - (`POSITIONAL_ONLY`, `POSITIONAL_OR_KEYWORD`) = positional
    - positional with default = optional positional
    - `KEYWORD_ONLY` = options
    - defaults = defaults
	- Boolean special casing
	    - If the default is `True` or `False`, the option does not take any
	      arguments. Instead, if the option is given on the
	      commandline, the opposite value to the default is given to
	      the function.
	    - Example:
		```python
		def rm(*, force=False):
		    pass

		cli(rm)(['--force']) # ~== rm(force=True)
		cli(rm)([]) # ~== rm(force=False)
		```
    - type annotations = type
	- If the `type` is callable, it is called by `argparse` on the relevant substring
	- If the type is `bool`, it is replaced by `coerce_bool`
	- Provide your own custom function or handle the strings in your
	  function body if you need something fancier.

Special types:
    - cli.Choice
	- `def foo(x:Choice(1,2))` interpreted as `add_argument('x', choices=(1,2), type=int)`

```python
def example(positional, arguments):
    pass

def defaults(normally_one=1):
    pass

def typed(positional:bool, positional2:int):
    pass

# keyword some-positional-arg --keyword2=foo --keyword1=4
def keyword(positional, *, keyword1=3, keyword2='default_filename'):
    pass

# Mandatory keywords are bad, but you can have them if you want.
def mandatory_keywords(positional, *, keyword1, keyword2):
    pass

def varargs(pos1, pos2, *rest):
    pass

def choice_from_list(person:Choice('Ann', 'Bob', 'Charlie'))
    pass

# `flags --flag` is similar to flags(flag=True)
# `flags --inverse_flag` is similar to flags(inverse_flag=False)
def flags(*, flag=False, inverse_flag=True):
    pass
```

## Related work

Other nice ways to make CLIs:

 - [docopt](https://docopt.org)
 - [cli2](https://pypi.org/project/cli2/)
