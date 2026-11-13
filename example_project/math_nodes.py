"""Math nodes.

Most of these are pure nodes: they have no exec pins, so they run when another node needs
their result. Random Integer is an exec node (its docstring tells why).
"""

from __future__ import annotations

import math
import random

from node_editor.node import Node


class AddNode(Node):
    """Adds two numbers: result = a + b."""

    title = "Add"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=0.0)
        self.add_input("b", default=0.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", self.get_input("a") + self.get_input("b"))


class SubtractNode(Node):
    """Subtracts b from a: result = a - b."""

    title = "Subtract"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=0.0)
        self.add_input("b", default=0.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", self.get_input("a") - self.get_input("b"))


class MultiplyNode(Node):
    """Multiplies two numbers: result = a * b."""

    title = "Multiply"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=1.0)
        self.add_input("b", default=1.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", self.get_input("a") * self.get_input("b"))


class DivideNode(Node):
    """Divides a by b: result = a / b. If b is 0, the node shows an error."""

    title = "Divide"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=0.0)
        self.add_input("b", default=1.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", self.get_input("a") / self.get_input("b"))


class ModuloNode(Node):
    """The remainder after a is divided by b. For example, 7 modulo 3 is 1."""

    title = "Modulo"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=0)
        self.add_input("b", default=1)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", self.get_input("a") % self.get_input("b"))


class PowerNode(Node):
    """Raises a number to a power: result = value ** exponent. For example, 3 ** 2 is 9."""

    title = "Power"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("value", default=0.0)
        self.add_input("exponent", default=2.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", self.get_input("value") ** self.get_input("exponent"))


class SquareRootNode(Node):
    """The square root of a number. For example, the square root of 9 is 3."""

    title = "Square Root"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("value", default=0.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", math.sqrt(self.get_input("value")))


class RoundNode(Node):
    """Rounds a number to a number of digits after the decimal point.

    With 0 digits, the result is a whole number.
    """

    title = "Round"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("value", default=0.0)
        self.add_input("digits", default=0)
        self.add_output("result")

    def compute(self) -> None:
        value = self.get_input("value")
        digits = int(self.get_input("digits"))
        self.set_output("result", round(value, digits) if digits > 0 else round(value))


class MinNode(Node):
    """The smaller of two numbers."""

    title = "Min"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=0.0)
        self.add_input("b", default=0.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", min(self.get_input("a"), self.get_input("b")))


class MaxNode(Node):
    """The larger of two numbers."""

    title = "Max"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=0.0)
        self.add_input("b", default=0.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", max(self.get_input("a"), self.get_input("b")))


class RandomIntegerNode(Node):
    """A random whole number from minimum to maximum. Both ends are possible.

    This is an exec node, so that it gives a new number each time it runs. A pure node runs
    again only when its inputs change.
    """

    title = "Random Integer"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("then")
        self.add_input("minimum", default=1)
        self.add_input("maximum", default=6)
        self.add_output("value")

    def compute(self) -> None:
        minimum = int(self.get_input("minimum"))
        maximum = int(self.get_input("maximum"))
        self.set_output("value", random.randint(minimum, maximum))
