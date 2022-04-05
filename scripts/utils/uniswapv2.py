import math

UINT_256_MAX = 2**256 - 1


def compute_profit_maximizing_trade(
    true_price_token_a, true_price_token_b, reserve_a, reserve_b
):
    a_to_b = reserve_a / reserve_b < true_price_token_a / true_price_token_b
    invariant = reserve_a * reserve_b
    left_side = (
        math.sqrt(invariant * 1000 * true_price_token_a / (true_price_token_b * 997))
        if a_to_b
        else math.sqrt(
            invariant * 1000 * true_price_token_b / (true_price_token_a * 997)
        )
    )
    right_side = reserve_a * 1000 if a_to_b else reserve_b * 0.997
    if left_side < right_side:
        return False, 0
    return a_to_b, left_side - right_side


def div(a, b) -> int:
    return a // b & UINT_256_MAX


def get_amount_out(amount_in, reserve_in, reserve_out) -> int:
    amount_in_with_fee = amount_in * 997
    n = amount_in_with_fee * reserve_out
    d = reserve_in * 1000 + amount_in_with_fee
    return div(n, d)


def get_amount_in(amount_out, reserve_in, reserve_out) -> int:
    n = reserve_in * amount_out * 1000
    d = (reserve_out - amount_out) * 997
    return div(n, d) + 1
