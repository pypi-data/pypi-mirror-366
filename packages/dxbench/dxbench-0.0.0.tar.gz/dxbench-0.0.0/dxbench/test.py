from dxbench.bot import Bot
from dxbench.runner import run

response = """\
import pytest
from code.add import add


def test_add_positive_numbers():
    assert add(2, 3) == 5
    assert add(10, 20) == 30
    assert add(1, 1) == 2
    assert add(100, 200) == 300


def test_add_negative_numbers():
    assert add(-2, -3) == -5
    assert add(-10, -20) == -30
    assert add(-1, -1) == -2


def test_add_mixed_numbers():
    assert add(5, -3) == 2
    assert add(-5, 3) == -2
    assert add(10, -10) == 0
    assert add(-15, 20) == 5


def test_add_with_zero():
    assert add(0, 0) == 0
    assert add(5, 0) == 5
    assert add(0, 5) == 5
    assert add(-5, 0) == -5
    assert add(0, -5) == -5


def test_add_large_numbers():
    assert add(1000000, 2000000) == 3000000
    assert add(-1000000, -2000000) == -3000000
    assert add(999999999, 1) == 1000000000


def test_add_commutativity():
    assert add(3, 7) == add(7, 3)
    assert add(-4, 9) == add(9, -4)
    assert add(0, 15) == add(15, 0)


def test_add_edge_cases():
    assert add(2147483647, 0) == 2147483647  # Max 32-bit signed int
    assert add(-2147483648, 0) == -2147483648  # Min 32-bit signed int
    assert add(1, -1) == 0
    assert add(-1, 1) == 0


@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, -1, -2),
    (5, -5, 0),
    (100, 200, 300),
    (-50, 75, 25),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected


def test_add_type_hints():
    # These should all work fine since Python's int type is flexible
    result = add(5, 10)
    assert isinstance(result, int)
    assert result == 15
"""


class TestBot(Bot):
    def get_response(self, prompt: str) -> str:
        # Get your response here
        return response


bot = TestBot()
run(bot)
