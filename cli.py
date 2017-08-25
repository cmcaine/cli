"""
Inspect functions or objects containing funcs to produce CLIs with argparse.

Meat of this module is generate_parser and (to a lesser extent)
generate_parser_obj.

Currently there is no easy way to add documentation to parameters.

"""

import argparse
import inspect
import sys

def cli(obj):
    """
    Rtn a function that, when called with sys.argv will act like a cli to func.

    The wrapper performs simple validation and conversion on argv, then calls
    func. For details of signature interpretation, see generate_parser.

    """
    if inspect.isfunction(obj):
        return function2cli(obj)
    else:
        return obj2cli(obj)

def function2cli(func):
    """
    Rtn a function that, when called with sys.argv will act like a cli to func.

    The wrapper performs simple validation and conversion on argv, then calls
    func. For details of signature interpretation, see generate_parser.

    """
    parser = generate_parser(func)
    sig = inspect.signature(func)

    def inner(argv=None, exit=True):
        import sys
        if argv is None:
            argv = sys.argv[1:]

        result = apply_namespace(func, parser.parse_args(argv))

        if result is not None:
            print(result)
        if exit: sys.exit(0)

    return inner

def obj2cli(obj, *, convert_numbers=False):
    """
    Rtn a cli to a module, class, or other entity having function attributes.

    Each of the function attributes of obj are added as subparsers.

    """
    parser = generate_parser_obj(obj)

    def inner(argv=None, exit=True):
        import sys
        if argv is None:
            argv = sys.argv[1:]

        args = parser.parse_args(argv)
        # Delete subparser identifier
        args.__delattr__('{command}')
        func = args.__getattribute__('{func}')
        args.__delattr__('{func}')

        bind = namespace_to_bind(args, inspect.signature(func))
        if convert_numbers: _coerce_numbers(bind)

        result = func(*bind.args, **bind.kwargs)

        if result is not None:
            print(result)
        if exit: sys.exit(0)

    return inner

def _coerce_numbers(bind):
    "Coerce the values of unannotated params to numbers, if possible."

    def coerce_one(value):
        try: value = int(value) 
        except ValueError:
            try: value = float(value)
            except ValueError:
                try: value = complex(value)
                except ValueError:
                    pass
        return value

    for value, param in zip(bind.arguments.values(), bind.signature.parameters.values()):
        if _isempty(param.annotation) and value is not None:
            bind.arguments[param.name] = coerce_one(value)

    # bind is edited in-place. Return it as well for ease of use.
    return bind


def generate_parser_obj(obj):
    """
    argparse parser automatically generated by inspecting an obj and its functions.
    
    """
    parser = argparse.ArgumentParser(
            prog=obj.__name__,
            # Modules tend to have very long docstrings...
            description=inspect.cleandoc(obj.__doc__).splitlines()[0] if obj.__doc__ else None
            )
    # Dest is suppressed by default. Set it to a value that no parameter name can take.
    subparsers = parser.add_subparsers(dest='{command}')
    # Due to a stupid bug, subparsers are optional by default.
    subparsers.required = True

    def functions(obj):
        return tuple([o[1] for o in inspect.getmembers(obj) if inspect.isfunction(o[1])])

    for f in functions(obj):
        thisparser = subparsers.add_parser(
                f.__name__,
                description=inspect.cleandoc(f.__doc__) if f.__doc__ else None
                )
        generate_parser(f, thisparser)
        # Setting this so function is the value of f, rather than a later lookup of attribute 'f'.
        thisparser.set_defaults(**{'{func}':f})

    return parser

def generate_parser(func, parser=None):
    """
    argparse parser automatically generated by inspecting func.

    func signature interpretation:
        - (POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD) = positional
        - positional with default = optional positional
        - KEYWORD_ONLY = options
        - defaults = defaults
        - type annotations = type
            - TODO: str to dict?

    Special types:
        - cli.Choice
            - `def foo(x:Choice(1,2))` interpreted as `add_argument('x', choices=(1,2))`

    """
    sig = inspect.signature(func)

    if parser is None:
        parser = argparse.ArgumentParser(
                prog=func.__name__,
                description=inspect.cleandoc(func.__doc__) if func.__doc__ else None
                )

    for param in sig.parameters.values():
        kwargs = {}
        if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            name = param.name
            if not _isempty(param.default):
                kwargs["nargs"]='?'
        elif param.kind is inspect.Parameter.KEYWORD_ONLY:
            if len(param.name) == 1:
                name = f"-{param.name}"
            else:
                name = f"--{param.name}"
            if _isempty(param.default):
                kwargs["required"] = True
        else:
            raise NotImplementedError(f"Params of {param.kind} are not supported yet.")

        if not _isempty(param.default):
            kwargs["default"] = param.default
        if not _isempty(param.annotation) and type(param.annotation) is type:
            if issubclass(param.annotation, Choice):
                kwargs["choices"] = param.annotation.choices
                kwargs["type"] = param.annotation.type
            else:
                kwargs["type"] = param.annotation

        parser.add_argument(name, **kwargs)

    return parser

def namespace_to_bind(namespace, sig):
    "argparse.Namespace -> inspect.BoundArguments"
    bind = sig.bind_partial()
    for paramname in sig.parameters:
        bind.arguments[paramname] = namespace.__getattribute__(paramname)
    return bind

def apply_namespace(func, namespace):
    "Call (or apply) func with the arguments in namespace"
    bind = namespace_to_bind(namespace, inspect.signature(func))
    return func(*bind.args, **bind.kwargs)


def _isempty(thing):
    return thing is inspect.Parameter.empty


class Choice:
    """
    Use this type to annotate parameters that should accept only some values.

    e.g.
        def dispatch(cmd:Choice('spam','shutdown','banana')='spam'):
            if cmd == 'spam:
                ...

    The argparse `type` kwarg will be set to the type of the first argument. It
    is an error to provide choices with different types.

    "Note that inclusion in the choices container is checked after any type
    conversions have been performed"
    https://docs.python.org/3/library/argparse.html#choices

    """
    def __new__(self, *choices):
        _type = type(choices[0])
        for choice in choices:
            assert type(choice) == _type, "All choices must share the same type."
        return type(f'Choice{choices}', (Choice,), {'choices':choices, 'type':_type})
