# Uniswap Suhiswap Arbitrage Bot Brownie

Brownie version of https://github.com/6eer/uniswap-sushiswap-arbitrage-bot

With some modifications:

[x] Compute maximizing trade amount locally instead of `eth_call` to `Utils`
[ ] Use Multicall

## How to run

```bash
git clone https://github.com/wuwe1/uniswap-sushiswap-arbitrage-bot-brownieot
cd uniswap-sushiswap-arbitrage-bot-brownieot
brownie run scripts/bot_flashswap.py
```