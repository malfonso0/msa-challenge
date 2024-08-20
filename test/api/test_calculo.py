import pytest


from services.api.calculo import dhondt

dhondt_test_data = [
        ([340000, 280000, 160000, 60000,15000], 7,[3, 3, 1, 0, 0]),
        ([391000, 311000,184000, 73000, 15000,12000, 2000], 21,[9, 7, 4, 1, 0, 0, 0])
    ]

@pytest.mark.parametrize("input,escanos,resultado", dhondt_test_data)
def test_dhondt(input,escanos,resultado):
    print(input)
    _result = dhondt(input,escanos)
    assert _result == resultado
