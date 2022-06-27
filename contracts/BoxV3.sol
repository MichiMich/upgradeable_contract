// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BoxV3 {
    uint256 private value;

    event ValueChanged(uint256 newValue);

    function store(uint256 newValue) public {
        value = newValue;
        emit ValueChanged(newValue);
    }

    function retrieve() public view returns (uint256) {
        return value;
    }

    function incrementBy2() public {
        value = value + 2;
        emit ValueChanged(value);
    }
}
