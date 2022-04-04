import math
import time
import eth_abi
from brownie import web3, interface, a
from .deploy_utils import deploy_case_a


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


def get_amount_out(amount_in, reserve_in, reserve_out):
    return (0.997 * reserve_out * amount_in) / (reserve_in + amount_in)


def get_amount_in(amount_out, reserve_in, reserve_out):
    return (reserve_in * amount_out) / (reserve_out - amount_out) * (1000 / 997)


def arbitrage(arbitrager, u_pair, s_pair, token0, token1, block_number, timestamp):
    u_pair = interface.IUniswapV2Pair(u_pair)
    s_pair = interface.IUniswapV2Pair(s_pair)
    (uA, uB, _) = u_pair.getReserves()
    (sA, sB, _) = s_pair.getReserves()
    a_to_b, amount_in = compute_profit_maximizing_trade(sA, sB, uA, uB)
    print("a to b:", a_to_b)
    print("amount_in:", amount_in)
    if a_to_b:
        # uA/uB < sA/sB
        # (sushiswap) flashswap A -> (uniswap) get B -> (sushiswap) repaid B
        u_token1_out = get_amount_out(amount_in, uA, uB)
        s_token1_repaid = get_amount_in(amount_in, sB, sA)
        difference = u_token1_out - s_token1_repaid
        print(f"Get {u_token1_out} token1 from Uniswap")
        print(f"Repaid {s_token1_repaid} token1 to Sushiswap")
        print(f"Profit: {difference} token1")
        if difference <= 0:
            print(f"No arbitrage opportunity on {block_number}")
            return

        callback_data = eth_abi.encode_abi(
            ["uint256", "uint256"], [int(s_token1_repaid), timestamp + 60 * 60]
        )
        s_pair.swap(amount_in, 0, arbitrager, callback_data, {"from": a[1]})
        print("token1 balance:", token1.balanceOf(a[1]))
    else:
        # uA/uB > sA/sB
        # (sushiswap) flashswap B -> (uniswap) get A -> (sushiswap) repaid A
        u_token0_out = get_amount_out(amount_in, uB, uA)
        s_token0_repaid = get_amount_in(amount_in, sA, sB)
        difference = u_token0_out - s_token0_repaid
        print(f"Get {u_token0_out} token0 from Uniswap")
        print(f"Repaid {s_token0_repaid} token0 to Sushiswap")
        print(f"Profit: {difference} token0")
        if difference <= 0:
            print(f"No arbitrage opportunity on {block_number}")
            return
        callback_data = eth_abi.encode_abi(
            ["uint256", "uint256"], [int(s_token0_repaid + 1), timestamp + 60 * 60]
        )
        s_pair.swap(0, amount_in, arbitrager, callback_data, {"from": a[1]})
        print("token0 balance:", token0.balanceOf(a[1]))


def main():
    latest_block = 0
    arbitrager, u_pair, s_pair, token0, token1 = deploy_case_a()
    while True:
        time.sleep(1)
        incoming_block = web3.eth.get_block("latest")
        incoming_block_number = incoming_block["number"]
        incoming_block_timestamp = incoming_block["timestamp"]
        if incoming_block_number > latest_block:
            latest_block = incoming_block_number
            arbitrage(
                arbitrager,
                u_pair,
                s_pair,
                token0,
                token1,
                latest_block,
                incoming_block_timestamp,
            )
        else:
            continue
