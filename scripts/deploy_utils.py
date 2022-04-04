from datetime import datetime
from brownie import Arbitrager, MockToken, a, config, network, interface, web3


def pair_for(factory, token0, token1):
    b_pre = bytes.fromhex("ff")
    b_address = bytes.fromhex(factory[2:])
    b_token0 = bytes.fromhex(token0[2:])
    b_token1 = bytes.fromhex(token1[2:])

    b_salt = web3.keccak(b_token0 + b_token1)
    init_code_hash = (
        "0x96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f"
    )
    b_init_code_hash = bytes.fromhex(init_code_hash[2:])

    b_result = web3.keccak(b_pre + b_address + b_salt + b_init_code_hash)
    return web3.toChecksumAddress(b_result[12:].hex())


def deploy(uA, uB, sA, sB):
    start_time = datetime.now()
    token0 = MockToken.deploy("Pineapple", "PNA", 1e10, a[0], {"from": a[0]})
    token1 = MockToken.deploy("Watermelon", "WTM", 1e10, a[0], {"from": a[0]})
    token0, token1 = (
        (token0, token1) if token0.address < token1.address else (token1, token0)
    )

    # 1 hour from now
    deadline = int(datetime.timestamp(start_time)) + 60 * 60

    # add liquidity
    UNISWAP_V2_ROUTER = config["networks"][network.show_active()]["UNISWAP_V2_ROUTER"]
    SUSHISWAP_V2_ROUTER = config["networks"][network.show_active()][
        "SUSHISWAP_V2_ROUTER"
    ]
    u_router = interface.IUniswapV2Router01(UNISWAP_V2_ROUTER)
    s_router = interface.IUniswapV2Router01(SUSHISWAP_V2_ROUTER)

    u_factory = u_router.factory()
    u_pair = pair_for(u_factory, token0.address, token1.address)
    # s_factory = s_router.factory()
    # s_pair = pair_for(s_factory, token0.address, token1.address)

    # 0xCA5A84F964bB8f40C82B486c7aC4597E9639088e

    token0.transfer(u_pair, 1000, {"from": a[0]})
    token1.transfer(u_pair, 1000, {"from": a[0]})
    # token0.transfer(s_pair, 1000, {"from": a[0]})
    # token1.transfer(s_pair, 1000, {"from": a[0]})

    token0.approve(u_router, uA, {"from": a[0]})
    token1.approve(u_router, uB, {"from": a[0]})
    u_router.addLiquidity(token0, token1, uA, uB, 0, 0, a[0], deadline, {"from": a[0]})
    token0.approve(s_router, sA, {"from": a[0]})
    token1.approve(s_router, sB, {"from": a[0]})
    tx = s_router.addLiquidity(
        token0, token1, sA, sB, 0, 0, a[0], deadline, {"from": a[0]}
    )
    s_pair = tx.events["PairCreated"][0][0]["pair"]

    # deploy arbitrager
    arbitrager = Arbitrager.deploy(s_router, u_router, {"from": a[0]})

    elapsed = datetime.now() - start_time
    print(f"token0: {token0}")
    print(f"token1: {token1}")
    print(f"arbitrager: {arbitrager}")
    print(f"deployment finished in {elapsed.total_seconds()}s")

    return arbitrager, u_pair, s_pair, token0, token1


def deploy_case_a():
    # case A: token1 cheaper on sushiswap
    uA, uB, sA, sB = (
        10e2,
        5e2,
        1e4,
        10e4,
    )
    return deploy(uA, uB, sA, sB)


def deploy_case_b():
    # case B: token 1 cheaper on uniswap
    uA, uB, sA, sB = (
        1e2,
        10e2,
        3e4,
        10e4,
    )
    return deploy(uA, uB, sA, sB)


def main():
    deploy_case_a()
