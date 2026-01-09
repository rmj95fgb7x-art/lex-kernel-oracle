// SPDX-License-Identifier: Sovereign-Lex-Liberatum-1.0
pragma language solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title Kex Index Token (KEX)
 * @dev Functional Utility Fuel for the Lex Kernel Oracle.
 * Hard-capped at 1,000,000,000 units. 
 * Implements a "Truth Tax" via the burn mechanism.
 */
contract KexIndexToken is ERC20, ERC20Burnable, AccessControl {
    bytes32 public constant TRUSTEE_ROLE = keccak256("TRUSTEE_ROLE");
    bytes32 public constant ARCHITECT_ROLE = keccak256("ARCHITECT_ROLE");

    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18;

    constructor(address initialTrustee) ERC20("Kex Index Token", "KEX") {
        _grantRole(DEFAULT_ADMIN_ROLE, initialTrustee);
        _grantRole(TRUSTEE_ROLE, initialTrustee);

        // Genesis Mint: 1 Billion KEX to the Lex Liberatum Trust
        // Allocation will be managed via time-locked vaults as per TRUST_LEDGER.md
        _mint(initialTrustee, MAX_SUPPLY);
    }

    /**
     * @dev Truth Validation Burn: Specifically called during clinical validation events.
     * Captures the "Truth Tax" from commercial interactions.
     */
    function executeTruthTax(address from, uint256 amount) public onlyRole(TRUSTEE_ROLE) {
        uint256 burnAmount = (amount * 20) / 100; // 20% Burn Rate
        _burn(from, burnAmount);
    }

    // Additional hooks for Staking and Architect Streams go here
}
