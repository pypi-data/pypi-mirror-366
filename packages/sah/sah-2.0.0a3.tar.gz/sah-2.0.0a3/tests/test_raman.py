import sah
from pytest import approx


folder = 'tests/samples/'
example_csv = folder + 'sample_raman.txt'


def test_raman():
    # Define the Spectra data and Plotting options
    raman = sah.Spectra(
        type     = 'Raman',
        files    = [example_csv],
        units_in = 'cm1',
        units    = 'cm1',
    )
    assert raman.units == ['cm-1']
    assert raman.type == 'raman'
    assert len(raman.dfs) == 1
    # ensure there are two columns
    assert raman.dfs[0].shape[1] == 2

