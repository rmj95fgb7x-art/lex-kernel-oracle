// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title LexKernelSubscription
 * @notice Subscription-based access to kernels (alternative to pay-per-use)
 */
contract LexKernelSubscription is Ownable, ReentrancyGuard {
    
    address public immutable beneficiary = 0x44f8219cBABad92E6bf245D8c767179629D8C689;
    
    // Subscription tiers
    enum Tier { NONE, BASIC, PROFESSIONAL, ENTERPRISE }
    
    struct SubscriptionPlan {
        uint256 monthlyFee;
        uint256 kernelLimit; // Max kernel executions per month (0 = unlimited)
        bool isActive;
    }
    
    struct UserSubscription {
        Tier tier;
        uint256 expiresAt;
        uint256 executionsThisMonth;
        uint256 lastResetTimestamp;
    }
    
    mapping(Tier => SubscriptionPlan) public plans;
    mapping(address => UserSubscription) public subscriptions;
    
    event Subscribed(address indexed user, Tier tier, uint256 expiresAt);
    event SubscriptionRenewed(address indexed user, uint256 newExpiresAt);
    event KernelExecuted(address indexed user, string kernelId);
    
    constructor() {
        // Initialize subscription plans
        plans[Tier.BASIC] = SubscriptionPlan({
            monthlyFee: 0.05 ether,
            kernelLimit: 1000,
            isActive: true
        });
        
        plans[Tier.PROFESSIONAL] = SubscriptionPlan({
            monthlyFee: 0.5 ether,
            kernelLimit: 10000,
            isActive: true
        });
        
        plans[Tier.ENTERPRISE] = SubscriptionPlan({
            monthlyFee: 5 ether,
            kernelLimit: 0, // Unlimited
            isActive: true
        });
    }
    
    /**
     * @notice Subscribe to a tier
     */
    function subscribe(Tier tier) external payable nonReentrant {
        require(tier != Tier.NONE, "Invalid tier");
        SubscriptionPlan memory plan = plans[tier];
        require(plan.isActive, "Plan not active");
        require(msg.value >= plan.monthlyFee, "Insufficient payment");
        
        uint256 expiresAt = block.timestamp + 30 days;
        
        subscriptions[msg.sender] = UserSubscription({
            tier: tier,
            expiresAt: expiresAt,
            executionsThisMonth: 0,
            lastResetTimestamp: block.timestamp
        });
        
        payable(beneficiary).transfer(msg.value);
        
        emit Subscribed(msg.sender, tier, expiresAt);
    }
    
    /**
     * @notice Check if user can execute kernel
     */
    function canExecute(address user) public view returns (bool) {
        UserSubscription storage sub = subscriptions[user];
        
        if (sub.expiresAt < block.timestamp) {
            return false;
        }
        
        SubscriptionPlan memory plan = plans[sub.tier];
        
        if (plan.kernelLimit == 0) {
            return true; // Unlimited
        }
        
        return sub.executionsThisMonth < plan.kernelLimit;
    }
    
    /**
     * @notice Record kernel execution (called by registry)
     */
    function recordExecution(address user, string calldata kernelId) external {
        require(canExecute(user), "Subscription limit reached or expired");
        
        UserSubscription storage sub = subscriptions[user];
        
        // Reset counter if new month
        if (block.timestamp >= sub.lastResetTimestamp + 30 days) {
            sub.executionsThisMonth = 0;
            sub.lastResetTimestamp = block.timestamp;
        }
        
        sub.executionsThisMonth++;
        
        emit KernelExecuted(user, kernelId);
    }
}
