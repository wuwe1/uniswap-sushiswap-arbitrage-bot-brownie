import math
from typing import Tuple

UINT_256_MAX = 2**256 - 1


def compute_profit_maximizing_trade(
    s_a: int, s_b: int, u_a: int, u_b: int
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
    a_to_b = u_a / u_b < s_a / s_b
    invariant = u_a * u_b
    left_side = (
        math.sqrt(div(invariant * 1000 * s_a, (s_b * 997)))
        if a_to_b
        else math.sqrt(div(invariant * 1000 * s_b, (s_a * 997)))
    )
    left_side = int(left_side)
    right_side = u_a * 1000 if a_to_b else div(u_b * 1000, 997)
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
