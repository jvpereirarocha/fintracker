from pytest import mark


@mark.parametrize(
    "x, y, result",
    [
        (1, 2, 3),
        (1, 4, 5),
        (1, -1, 0),
    ],
)
def test_x_and_y(x, y, result):
    assert x + y == result
