import pytest
from scripts.utils.uniswapv2 import get_amount_in, get_amount_out

test_get_amount_in_params = [
    [332, 1000, 1000, 499],
    [300000000000000000, 2802485372577, 1352290969467094876036463, 623591],
]


@pytest.mark.parametrize("params", test_get_amount_in_params)
def test_get_amount_in(params):
    amount_out, reserve_in, reserve_out, amount_in = params
    assert get_amount_in(amount_out, reserve_in, reserve_out) == amount_in


test_get_amount_out_params = [
    [500, 1000, 1000, 332],
    [
        50000000000000000000,
        51253778522000054136628,
        5687448808186918780971335115431,
        5526301574683727631721925538,
    ],
]


@pytest.mark.parametrize("params", test_get_amount_out_params)
def test_get_amount_out(params):
    amount_in, reserve_in, reserve_out, amount_out = params
    assert get_amount_out(amount_in, reserve_in, reserve_out) == amount_out
