"""

Purpose
=======

A critical part of testing is providing useful **diagnostics** on failure.
One of the great things about test-driven development (TDD) is that you always
get a preview of the feedback your test will give when it fails. This also
allows you to consider whether this is going to be useful in the future, if
some other change to the codebase causes a regression in the tested
functionality.

.. seealso::

    .. raw:: html
        :file: ../../docs/source/_static/feedback-on-diagnostics.svg

    From `Growing Object-Oriented Software`_ by Nat Pryce and Steve Freeman.

    © 2010 Nat Pryce, licensed under `CC BY-SA 4.0`_.

    .. _Growing Object-Oriented Software: http://growing-object-oriented-software.com/index.html
    .. _CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/

Example
+++++++

Consider the following test:

.. code-block:: python

    import unittest


    def my_func() -> list[str]:
        return []


    class TestMyFunction(unittest.TestCase):

        def test_my_function_returns_three_items(self):
            self.assertTrue(len(my_func()) == 3)


    if __name__ == "__main__":
        unittest.main()

This is absolutely fine when ``my_func`` works correctly - it describes the
intended behaviour, and ensures that it keeps happening. But what if something
*breaks*? OK, the test fails, but what does it tell us about *why* it failed?

.. code-block:: text

        self.assertTrue(len(my_func()) == 3)
    AssertionError: False is not true


We can do better than this; *how many* items did it return, then?

.. code-block:: python

    class TestMyFunction(unittest.TestCase):

        def test_my_function_returns_three_items(self):
            self.assertEqual(len(my_func()), 3)

.. code-block:: text

        self.assertEqual(len(my_func()), 3)
    AssertionError: 0 != 3

This is a bit better, and in the trivial empty list case that's all the
information we need, but what if it said e.g. ``1 != 3``; *what* one item is in
the list?

This is one of the great things about `pytest`_; even from a plain
``assert`` it tries to tell you as much as possible about what went wrong:

.. code-block:: text

    >       assert len(my_func()) == 3
    E       assert 0 == 3
    E        +  where 0 = len([])
    E        +    where [] = my_func()

But even in vanilla :py:mod:`unittest` we can use JoyThief's matchers to
write a more diagnostically useful test. For example, we can use
:py:class:`~joythief.objects.InstanceOf` to say *"it must be a list
containing three strings"*:

.. code-block:: python

    from joythief.objects import InstanceOf

    # ...

    class TestMyFunction(unittest.TestCase):

        def test_my_function_returns_three_items(self):
            self.assertEqual(
                my_func(),
                [InstanceOf(str), InstanceOf(str), InstanceOf(str)],
            )

Now we're passing the whole value to :py:meth:`~unittest.TestCase.assertEqual`,
so the feedback actually shows the list and any content it *does* have:

.. code-block:: text

        self.assertEqual(
    AssertionError: Lists differ: [] != [InstanceOf(<class 'str'>), InstanceOf(<cl[34 chars]r'>)]

    Second list contains 3 additional elements.
    First extra element 0:
    InstanceOf(<class 'str'>)

    - []
    + [InstanceOf(<class 'str'>),
    +  InstanceOf(<class 'str'>),
    +  InstanceOf(<class 'str'>)]

Visualisation
+++++++++++++

The trick up JoyThief's sleeve is that, if a matcher has been compared equal
to a single value and never to any other, it represents itself *as that
value*. Extending the above example to show how this can be useful: if the
list contains three items, but they're not all strings:

.. code-block:: python

    def my_func() -> list[str]:
        return ["foo", "bar", 123]

then the values that were acceptable are shown as such in the output:

.. code-block:: text

        self.assertEqual(
    AssertionError: Lists differ: ['foo', 'bar', 123] != ['foo', 'bar', InstanceOf(<class 'str'>)]

    First differing element 2:
    123
    InstanceOf(<class 'str'>)

    - ['foo', 'bar', 123]
    + ['foo', 'bar', InstanceOf(<class 'str'>)]

This is helpful anywhere else a visual diff is shown, for example in pytest's
output:

.. code-block:: text

    >       assert my_func() == [InstanceOf(str), InstanceOf(str), InstanceOf(str)]
    E       AssertionError: assert ['foo', 'bar', 123] == ['foo', 'bar'...class 'str'>)]
    E
    E         At index 2 diff: 123 != InstanceOf(<class 'str'>)
    E         Use -v to get more diff

or in tools like the `PyCharm`_ test runner.

.. _PyCharm: https://www.jetbrains.com/pycharm/
.. _pytest: https://docs.pytest.org/en/stable/
"""

from .core import Matcher

__all__ = ["Matcher"]

Matcher = Matcher
"""The core generic matcher type.

.. versionadded:: 0.5.0 previously only exposed from :py:mod:`joythief.core`

Can be extended, to create your own custom matchers, or used in type
definitions.

.. code-block:: python

    from joythief import Matcher
    from joythief.strings import StringContaining


    def contains_only(valid_chars: str) -> Matcher[str]:
        return StringContaining(rf"^[{valid_chars}]+$")

"""
