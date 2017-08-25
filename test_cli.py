import pytest

from cli import *

### Example functions to operate on

def token(method:Choice('xkcd', 'short')='xkcd', entropy:int=70):
    "example function"
    pass

def token_no_annotation(method='xkcd', entropy=70):
    "example function"
    pass

def five(a, b, c, d, e):
    "example function"
    pass

def choice_example(x:Choice(0, 1, 2)):
    "example function"
    return locals()

### Helper functions

def tcode(func, argstr, code):
    "assert func exits with code"
    try:
        tmp=cli(func)
        tmp(argstr.split())
    except SystemExit as e:
        assert e.code == code

### Tests

def test_choices():
    tcode(choice_example, '1', 0)
    tcode(choice_example, '2', 0)
    tcode(choice_example, 'a', 2)

def test_function2cli():
    tcode(token, '-h', 0)
    tcode(token, 'xkcd', 0)
    tcode(token, 'xkcd 4', 0)
    tcode(token, 'short', 0)
    tcode(token, 'notanoption', 2)
    tcode(token, 'too many options', 2)

def test_obj2cli():
    import test_cli
    tcode(test_cli, '-h', 0)
    tcode(test_cli, 'test_choices -h', 0)

def test_coerce_numbers():
    from cli import _coerce_numbers
    helper = lambda func, s: _coerce_numbers(
            inspect.signature(func).bind_partial(*s.split())
            )

    assert helper(token_no_annotation, 'xkcd 40').args == ('xkcd', 40)
    assert helper(five, '1 2.0 3j 0xdeadbeef 077').args == (1, 2.0, 3j, '0xdeadbeef', 77)

def test_Choice():
    Choice(1,2,3)
    Choice(1.0,2.0,3.0)
    with pytest.raises(AssertionError, match='same type'):
        Choice(1.0,2,3.0)

# For other version of Choice...
# def test_Choice():
#     assert Choice(1,2,3)(1) is 1
#     assert Choice(1,2,3)(3) is 3
#     assert Choice('a', 'string')('string') == 'string'

#     with pytest.raises(ValueError) as e:
#         Choice(1,2,3)(4)

#     assert issubclass(Choice(1,2), Choice)
