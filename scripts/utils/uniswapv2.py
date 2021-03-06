import math
from typing import Tuple

UINT_256_MAX = 2**256 - 1


def compute_profit_maximizing_trade(
    sa: int, sb: int, ua: int, ub: int
) -> Tuple[bool, int]:
    """
    a -> b:
            _____________
          ╲╱ sa⋅sb⋅ua⋅ub
    -ua + ───────────────
                sb
    b -> a:
            _____________
          ╲╱ sa⋅sb⋅ua⋅ub
    -ub + ───────────────
                sa
    """
    a_to_b = ua / ub < sa / sb
    k = ua * ub
    scale = 1000 / 997
    left_side = (
        math.sqrt(k * sa / sb * scale) if a_to_b else math.sqrt(k * sb / sa * scale)
    )
    right_side = ua * scale if a_to_b else ub * scale
    if left_side < right_side:
        return False, 0
    return a_to_b, int(left_side - right_side)


def div(a, b) -> int:
    return a // b & UINT_256_MAX


def get_amount_out(amount_in, reserve_in, reserve_out) -> int:
    """
    amount_in: x
    reserve_in: in
    reserve_out: out
    0.997⋅out⋅x
    ───────────
    in + 0.997⋅x
    """
    amount_in_with_fee = amount_in * 997
    n = amount_in_with_fee * reserve_out
    d = reserve_in * 1000 + amount_in_with_fee
    return div(n, d)


def get_amount_in(amount_out, reserve_in, reserve_out) -> int:
    """
    amount_out: y
    reserve_in: in
    reserve_out: out
    1000⋅in⋅y
    ───────────
    997⋅(out - y)
    """
    n = reserve_in * amount_out * 1000
    d = (reserve_out - amount_out) * 997
    return div(n, d) + 1


def compute_equal_price_trade(sa, sb, ua, ub):
    """
    make two dex price equal after trade

    from s get a, swap a for b in u:
    Eq((sa - x) / (sb + (sb * x)/(sa - x)), (ua + x) / (ub - (ub * x)/ (ua + x)))
                         _____________
    -sa⋅ua⋅(sb + ub) + ╲╱ sa⋅sb⋅ua⋅ub ⋅(sa + ua)
    ────────────────────────────────────────────
                sa⋅sb - ua⋅ub

    from s get b, swap b for a in u:
    Eq((sa + (sa * x)/(sb - x)) / (sb - x), (ua - (ua * x)/(ub + x)) / (ub + x))
                         _____________
    -sb⋅ub⋅(sa + ua) + ╲╱ sa⋅sb⋅ua⋅ub ⋅(sb + ub)
    ────────────────────────────────────────────
                sa⋅sb - ua⋅ub
    """
    a_to_b = ua / ub < sa / sb
    k1 = sa * sb * ua * ub
    left_side = math.sqrt(k1) * (sa + ua) if a_to_b else math.sqrt(k1) * (sb + ub)
    left_side = left_side * 1000 / 997
    right_side = (
        sa * ua * (sb + ub) * 1000 / 997 if a_to_b else sb * ub * (sa + ua) * 1000 / 997
    )
    if left_side < right_side:
        return False, 0
    else:
        return a_to_b, int((left_side - right_side) / (sa * sb - ua * ub))
