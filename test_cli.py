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

def keywords(*, kw1=1, kw2=2):
    return locals()

def mandatory_keywords(*, kw1, kw2=2):
    return locals()

def varargs(*positionals, kw1=1):
    return locals()

def varargs2(pos1, pos2, *positionals, kw1=1):
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

def test_infer_type():
    parser = generate_parser(token_no_annotation)
    assert parser.parse_args('xkcd'.split()).entropy == 70
    assert parser.parse_args('xkcd 4'.split()).entropy == 4

def test_obj2cli():
    import test_cli
    tcode(test_cli, '-h', 0)
    tcode(test_cli, 'test_choices -h', 0)

def test_coerce_numbers():
    from cli import _coerce_numbers
    helper = lambda func, s: _coerce_numbers(
            inspect.signature(func).bind_partial(*s.split())
            ).args

    # When types are annotated, coerce_numbers shouldn't interfere.
    assert helper(token, 'xkcd 40') == ('xkcd', '40')

    # Otherwise convert anything that looks like a number.
    assert helper(five, '1 2.0 3j 0xdeadbeef 077') == (1, 2.0, 3j, '0xdeadbeef', 77)
    assert helper(lambda x, y: None, '-1e6 -99') == (-1e6, -99)

def test_Choice():
    Choice(1,2,3)
    Choice(1.0,2.0,3.0)
    with pytest.raises(AssertionError, match='same type'):
        Choice(1.0,2,3.0)

def test_keywords():
    tcode(keywords, '', 0)
    tcode(keywords, '--kw1=4', 0)
    tcode(keywords, '--kw2=4', 0)
    tcode(keywords, '--kw1=3 --kw2=4', 0)
    tcode(keywords, 'pos --kw1=3 --kw2=4', 2)

def test_keywords():
    tcode(mandatory_keywords, '', 2)
    tcode(mandatory_keywords, '--kw1=4', 0)
    tcode(mandatory_keywords, '--kw2=4', 2)
    tcode(mandatory_keywords, '--kw1=3 --kw2=4', 0)
    tcode(mandatory_keywords, 'pos --kw1=3 --kw2=4', 2)

def test_varargs():
    parser = generate_parser(varargs)
    assert parser.parse_args('one two three four'.split()).positionals == 'one two three four'.split()
    assert parser.parse_args('one two three four --kw1 5'.split()).positionals == 'one two three four'.split()

def test_varargs2():
    parser = generate_parser(varargs2)
    assert parser.parse_args('a b one two three four'.split()).positionals == 'one two three four'.split()
    assert parser.parse_args('a b one two three four --kw1 5'.split()).positionals == 'one two three four'.split()

# For other version of Choice...
# def test_Choice():
#     assert Choice(1,2,3)(1) is 1
#     assert Choice(1,2,3)(3) is 3
#     assert Choice('a', 'string')('string') == 'string'

#     with pytest.raises(ValueError) as e:
#         Choice(1,2,3)(4)

#     assert issubclass(Choice(1,2), Choice)
