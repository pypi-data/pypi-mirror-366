import sah
from pytest import approx


def test_material():
    H = sah.Material(elements = {'H':1})
    H.set()
    assert H.cross_section == approx(82.0, abs=1)
    D = sah.Material(elements={'D':1})
    D.set()
    assert D.cross_section == approx(7.0, abs=1)


