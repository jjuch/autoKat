import pytest
from autokat.track import SCREEN_HEIGHT, SCREEN_WIDTH, Calibration, Coords

_trivial_calibration = Calibration(
    top_left=Coords(0, 0),
    top_right=Coords(SCREEN_WIDTH - 1, 0),
    bottom_left=Coords(0, SCREEN_HEIGHT - 1),
    bottom_right=Coords(SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1),
)


@pytest.mark.parametrize(
    "original_coords,transformed_coords",
    [
        *[(corner, corner) for corner in _trivial_calibration],
        (Coords(100, 100), Coords(100, 100)),
    ],
)
def test_trivial_calibration(original_coords: Coords, transformed_coords: Coords):
    transformed = _trivial_calibration.transform(original_coords)
    assert transformed == transformed_coords


_non_trivial_calibration = Calibration(
    top_left=Coords(10, 10),
    top_right=Coords(SCREEN_WIDTH - 1 - 20, 10),
    bottom_left=Coords(15, SCREEN_HEIGHT - 1 - 30),
    bottom_right=Coords(SCREEN_WIDTH - 1 - 25, SCREEN_HEIGHT - 20),
)


@pytest.mark.parametrize(
    "original_coords,transformed_coords", [(Coords(10, 10), Coords(0, 0))]
)
def test_non_trivial_calibration(original_coords: Coords, transformed_coords: Coords):
    transformed = _non_trivial_calibration.transform(original_coords)
    assert transformed == transformed_coords


def test_fucked_up_case():
    calibration = Calibration.from_dict(
        {"top_left": [215.2, 110.39999999999999], "top_right": [907.2, 70.39999999999999], "bottom_left": [134.4, 603.2], "bottom_right": [1021.6, 584.8]}
    )
