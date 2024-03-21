# UFO 🛸
*uniform functional orchestrators*

Delicious monads and functional programming patterns in python!

[Check out the api docs for reference](https://benrutter.github.io/ufo-tools/index.html)

![Coverage Badge](https://img.shields.io/badge/coverage-100-green) ![Static Badge](https://img.shields.io/badge/python-%3E%3D3.8-blue)

## Project Goals

This library is meant to implement a simple tools for functional programming in python in a way that:

- Can be intergrated quickly/simply with existing code
- Maintains type safety
- Depends only on the standard library

## Quick Start

UFO is a library to help with functional programming patterns in python.

It's designed to be very small and get out your way rather than requiring use everywhere.

The library contains two modules: `wrappers` and `containers`. The wrappers are the most simple, so we can start with them.

## Wrappers

Say you have a function that mutates its arguments:

```python
def maximum_of_list_and_also_seven(some_list: list[int]):
    """
    Gets the biggest number from a list of ints, but with
    seven also included for consideration since its such
    a good number.
    """
    some_list.append(7)
    return max(some_list)
```

The function is simple enough to follow but it's doing something potentially annoying and mutating the `some_list` variables.

For instance:

```python
my_list = [1, 4]

max_item = maximum_of_list_and_also_seven(my_list)

print(max_item)  # prints out 7

print(my_list)  # [1, 4, 7]
```

Oh no! Our list changed under our feet, that's rude! A lot of the time we don't want this to happen since it can lead to confusing errors. So you could work around it in a bunch of different ways. `ufo_tools` gives you an easy one:

```python
from ufo_tools.wrappers import mutation_free

@mutation_free
def maximum_of_list_and_also_seven(some_list: list[int]):
    """
    Gets the biggest number from a list of ints, but with
    seven also included for consideration since its such
    a good number.
    """
    some_list.append(7)
    return max(some_list)
```

Phew! Now that function will get passed down deep copies of the `some_list` variable, instead of `some_list` itself, and we can all sleep easy at night.

Even better, the `@mutation_free` wrapper also makes pretty quick reading to know that the function can't mutate it's arguments.

See the documentation for some more examples (like adding in retry logic, error handling and deprecation warnings) but hopefully you get the idea. The wrappers are there as some drop in tools to help you on your way to some nice guarantees when working with python.


## Containers

Containers are a common pattern for functional programming, they let us chain together values nicely.

Say we're building up some kind on string:

```python
def make_exciting(string):
  return string + "!!!"

def make_loud(string):
  return string.upper()

def say_hello(name):
  return f"hello {name}"

name = "Sam"
greeting = say_hello(name)
loud_greeting = make_loud(greeting)
exciting_loud_greeting = make_exciting(loud_greeting)

print(exciting_loud_greeting)  # HELLO SAM!!!
```

There's a lot of variables, which in practice aren't ever used, but they *could* get used any time, so we have to keep thinking about them. We can cut down on unnecesary thinking by chaining functions in a big row:

```python
message = make_exciting(make_loud(say_hello("Sam")))
print(message)
```

Phew! Except there's enough brackets to make a lisp programmer cry, and also we're reading in the *opposite order* of the functions being called. `make_exciting` happens last, but we're reading it first which means we're back to extra thinking again! And that's what we were trying to avoid.

Fortunately containers is here to save you:

```python
from ufo.containers import Container

message = (
  Container("Sam")
  .then(say_hello)
  .then(make_loud)
  .then(make_exciting)
  .unwrap()
)
print(message)
```
That's a little easier to follow. The `unwrap` message probably looks a little strange at the end to you - all it's doing is taking the string back out of the container, so we have just a string to print.

Even better than that, we can actually use containers to do a bunch of busy work for us, say we have a whole bunch of names:

```python
names = ["Lisa", "Bart", "Homer", "Maggie", "Marge"]
greetings = [say_hello(i) for i in names]
loud_greetings = [make_loud(i) for i in greetings]
exciting_loud_greetings = [make_exciting(i) for i in loud_greetings]
```

Oh boy! I'm tired just from typing that example.

Instead, we can use an `Array` container to iterate over things:

```python
from ufo.containers import Array
messages = (
  Array("Lisa", "Bart", "Homer", "Maggie", "Marge")
  .then(say_hello)
  .then(make_loud)
  .then(make_exciting)
)
```
This makes things a little easier. The `Array` container also comes with some additional helpers for working with lists like `filter` and `reduce`.

There's containers for handling errors and Nones too - check out the API docs for full details.
