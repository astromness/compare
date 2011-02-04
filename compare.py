"""The compare module contains the components you need to
compare values and ensure that your expectations are met.

To make use of this module, you simply import the `expect`
starter into your spec/test file, and specify the expectation
you have about two values.
"""


# core
# ====

class Expr(object):
    """Encapsulates a python expression, primitive value or callable
    that is to be evaluated and compared to another value.

    Serves as the basic construct for describing an expectation.
    Generally you would not use this class directly, instead it is
    available through the "expect" alias which allows for a more 
    pythonic syntax.
    
    It initializes with primitives, native types and expressions::
    
        >>> e = Expr("Foo")
        >>> e.actual == "Foo"
        True
        
        >>> e = Expr(['a', 'b'])
        >>> e.actual == ['a', 'b']
        True
    
        >>> Expr(4 + 7).actual == 11
        True
    
        >>> Expr(4 == 7).actual == False
        True
    """
    def __init__(self, expr):
        self.actual = expr

class UnmetExpectation(AssertionError):
    """Error that is raised if an expectation is not met.
    
    This error class inherits AssertionError so it is compatible with
    unittest assertion errors and plain old python "assert" errors.
    """
    pass
    
# provide a usable alias for the Expr class
expect = Expr
"""This is an alias for the ``Expr`` class that starts an expectation contruct.
It makes it easier to construct a readable assertion/expectation for some 
value, callable or expression that you are interested in.

When you apply expect to a value or expression, that value is stored as an 
attribute on the `Expr` instance that is returned. For instance the example 
below shows how the "actual" attribute is the evaluated expression::

    >>> expect(5 + 10).actual == 15
    True
    
If expect is applied to a callable, it does not evaluate immediately. Whether or 
not the callable is evaluated depends on the mather that is applied. So as you 
can see from the example below, the callable is stored as-is::

    >>> def call_me():
    ...     return "I was called..."
    >>> expect(call_me).actual      # doctest: +ELLIPSIS
    <function call_me at 0x...>

However, if the function is called and passed into expect, the actual value stored 
is of course the return value of the callable::

    >>> expect(call_me).actual == "I was called..."
    True
"""

def matcher(func):
    """Decorator to register a function as a matcher. It attaches the
    decorated function to the Expr class so that it is available through
    the "expect" starter.
    
    The matcher being registered is expected to accept at least a single parameter
    "self", which is the Expr object it is attached to.
    
    Here is a trivial example showing how to create and register a matcher::
    
        >>> def to_equal_foo(self):
        ...     assert self.actual == "foo"
        >>> matcher(to_equal_foo)
    
    Now you may use the matcher with the expect syntax::
    
        >>> expect("foo").to_equal_foo()
    
    Typically, a matcher would also accept a second parameter "expected", 
    which is the python expression, primitive or callable that the actual 
    value would be compared to.
    
    Another trivial matcher example. This time it takes a value to compare with
    and it spits out a helpful message if the comparison fails::
    
        >>> def to_equal(self, expected):
        ...     assert self.actual == expected, "Expected '%s' to equal '%s'" % (self.actual, expected)
        >>> matcher(to_equal)
        
    You may now use the matcher in an expectation::
        
        >>> expect("foo").to_equal("foo")
        
    When the matcher fails, it tells you what went wrong::
        
        >>> expect("foo").to_equal("BAR")
        Traceback (most recent call last):
            ...
        AssertionError: Expected 'foo' to equal 'BAR'
    """
    setattr(expect, func.__name__, func)

def ensure(expr, outcome, message=""):
    """Compares the result of the given boolean expression to the anticipated
    boolean outcome.
    
    All the the default matchers delegate to the trusty `ensure` helper to handle 
    the actual determination of pass/fail for a given comparison. If there is a match, 
    all is well. If the comparison fails, it raises an UnmetExpectation error with 
    the given message.
    
    Stays quite if the comparison lines up::
    
        >>> ensure(5 == 5, True)
    
    Raises an error if the comparison fails::
    
        >>> ensure('Foo' == 'foo', True)
        Traceback (most recent call last):
            ...
        UnmetExpectation
    
    Raises an error with the given message if the comparison fails::
    
        >>> actual = 'Foo'
        >>> expected = 'foo'
        >>> message = "'%s' does not equal '%s'" % (actual, expected)
        >>> ensure(actual == expected, True, message)
        Traceback (most recent call last):
            ...
        UnmetExpectation: 'Foo' does not equal 'foo'
    """
    if expr != outcome:
        raise UnmetExpectation(message)


# Matchers
# ========

@matcher
def to_equal(self, expected):
    """Compares values based on simple equality "=="
    
    Passes if the values are equal::
    
        >>> expect(555).to_equal(555)
    
    Fails if the values are not equal::
    
        >>> expect('waiting...').to_equal('done!')
        Traceback (most recent call last):
            ...
        UnmetExpectation: Expected 'waiting...' to equal 'done!'
    """
    message = "Expected %r to equal %r" % (self.actual, expected)
    ensure(self.actual == expected, True, message)

@matcher
def to_be(self, expected):
    """Compares values based on identity ("is")
    
    Passes if the values are identical::
    
        >>> a1 = a2 = ['foo', 'bar']
        >>> expect(a1).to_be(a2)
    
    Fails if the values are not identical::
    
        >>> b1 = ['foo', 'bar']
        >>> expect(a1).to_be(b1)
        Traceback (most recent call last):
            ...
        UnmetExpectation: Expected ['foo', 'bar'] to be ['foo', 'bar']
    """
    message = "Expected %r to be %r" % (self.actual, expected)
    ensure(self.actual is expected, True, message)
    
@matcher
def to_contain(self, expected):
    """Checks if the actual value contains the expected value.
    
    It applies to lists, strings, dict keys
    
    Passes if the expected value is in the actual value::
    
        >>> fruits = ['apple', 'orange', 'pear']
        >>> expect(fruits).to_contain('apple')
    
    Fails if the expected value cannot be found in the actual value::
    
        >>> mammals = ['dog', 'whale', 'cat']
        >>> expect(mammals).to_contain('fly')
        Traceback (most recent call last):
            ...
        UnmetExpectation: Expected ['dog', 'whale', 'cat'] to contain 'fly'
    
    Works for stings::

        >>> foo = "There is a BAR in here"
        >>> expect(foo).to_contain('BAR')
    
    And dict keys::
    
        >>> pos = {'x': 40, 'y': 500}
        >>> expect(pos).to_contain('x')
    """
    message = "Expected %r to contain %r" % (self.actual, expected)
    ensure(expected in self.actual, True, message)
    
@matcher
def to_return(self, expected):
    """Compares the return value of a callable to the expected value
    
    Passes if the callable returns the expected value::
    
        >>> def foo():
        ...     return "Foo"
        >>> expect(foo).to_return('Foo')
    
    Fails if the callable does not return the expected value::
    
        >>> def bar():
        ...     return "Barf"
        >>> expect(bar).to_return('Bar')
        Traceback (most recent call last):
            ...
        UnmetExpectation: Expected callable to return 'Bar' but got 'Barf'
    """
    actual = self.actual()
    message = "Expected callable to return %r but got %r" % (expected, actual)
    ensure(actual == expected, True, message)
