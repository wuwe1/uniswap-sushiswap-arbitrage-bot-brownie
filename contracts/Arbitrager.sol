pragma solidity 0.8.10;

import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router01.sol";
import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Pair.sol";
import "@uniswap/v2-core/contracts/interfaces/IERC20.sol";

contract Arbitrager {
    address immutable sFactory;
    IUniswapV2Router01 immutable uRouter;

    constructor(address _sFactory, address _uRouter) public {
        sFactory = _sFactory;
        uRouter = IUniswapV2Router01(_uRouter);
    }

    function uniswapV2Call(
        address _sender,
        uint256 _amount0,
        uint256 _amount1,
        bytes calldata _data
    ) external {
        // no need to do access control here
        address[] memory path = new address[](2);
        (uint256 amountRequired, uint256 deadline) = abi.decode(
            _data,
            (uint256, uint256)
        );
        address token0 = IUniswapV2Pair(msg.sender).token0();
        address token1 = IUniswapV2Pair(msg.sender).token1();
        if (_amount0 == 0) {
            uint256 amountEntryToken = _amount1;
            IERC20 entryToken = IERC20(token1);
            IERC20 exitToken = IERC20(token0);
            entryToken.approve(address(uRouter), amountEntryToken);
            path[0] = token1;
            path[1] = token0;
            uint256 amountReceived = uRouter.swapExactTokensForTokens(
                amountEntryToken,
                amountRequired,
                path,
                address(this),
                deadline
            )[1];
            exitToken.transfer(msg.sender, amountRequired);
            exitToken.transfer(_sender, amountReceived - amountRequired);
        } else {
            uint256 amountEntryToken = _amount0;
            IERC20 entryToken = IERC20(token0);
            IERC20 exitToken = IERC20(token1);
            entryToken.approve(address(uRouter), amountEntryToken);
            path[0] = token0;
            path[1] = token1;
            uint256 amountReceived = uRouter.swapExactTokensForTokens(
                amountEntryToken,
                amountRequired,
                path,
                address(this),
                deadline
            )[1];
            exitToken.transfer(msg.sender, amountRequired);
            exitToken.transfer(_sender, amountReceived - amountRequired);
        }
    }
}
