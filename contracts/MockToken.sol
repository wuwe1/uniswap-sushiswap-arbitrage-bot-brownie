pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/presets/ERC20PresetMinterPauser.sol";

contract MockToken is ERC20PresetMinterPauser {
    constructor(string memory name, string memory symbol)
        public
        ERC20PresetMinterPauser(name, symbol)
    {}
}
