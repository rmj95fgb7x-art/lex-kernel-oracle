// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title LexKernelIndex (LKI)
 * @notice Index token backed by kernel execution revenue - tradable like ETF
 */
contract LexKernelIndex is ERC20, Ownable, ReentrancyGuard {
    
    struct KernelWeight {
        string kernelId;
        uint256 weight; // Basis points (10000 = 100%)
        uint256 totalRevenue;
        uint256 executionCount;
        bool isActive;
    }
    
    // Index composition
    mapping(string => KernelWeight) public kernelWeights;
    string[] public kernelList;
    
    // Revenue tracking
    uint256 public totalIndexRevenue;
    uint256 public revenuePerToken; // Accumulated revenue per token //  ADD THIS LINE:
address public immutable beneficiary = 0x44f8219cBABad92E6bf245D8c767179629D8C689;

    mapping(address => uint256) public revenueDebt; // User's claimed revenue
    
    // Index stats
    uint256 public constant INITIAL_PRICE = 1e18; // 1 ETH per token
    uint256 public totalKernelExecutions;
    
    event KernelAdded(string indexed kernelId, uint256 weight);
    event KernelWeightUpdated(string indexed kernelId, uint256 newWeight);
    event RevenueDistributed(uint256 amount);
    event TokensMinted(address indexed user, uint256 amount, uint256 cost);
    event TokensBurned(address indexed user, uint256 amount, uint256 payout);
    event RevenueClaimed(address indexed user, uint256 amount);
    
    constructor() ERC20("Lex Kernel Index", "LKI") {}
    
    /**
     * @notice Add kernel to index with weight
     */
    function addKernel(string calldata kernelId, uint256 weight) external onlyOwner {
        require(weight > 0 && weight <= 10000, "Invalid weight");
        require(!kernelWeights[kernelId].isActive, "Kernel exists");
        
        kernelWeights[kernelId] = KernelWeight({
            kernelId: kernelId,
            weight: weight,
            totalRevenue: 0,
            executionCount: 0,
            isActive: true
        });
        
        kernelList.push(kernelId);
        emit KernelAdded(kernelId, weight);
    }
    
    /**
     * @notice Update kernel weight (rebalancing)
     */
    function updateWeight(string calldata kernelId, uint256 newWeight) external onlyOwner {
        require(kernelWeights[kernelId].isActive, "Kernel not found");
        kernelWeights[kernelId].weight = newWeight;
        emit KernelWeightUpdated(kernelId, newWeight);
    }
    
    /**
     * @notice Record kernel execution revenue
     */
    function recordRevenue(string calldata kernelId, uint256 amount) external onlyOwner {
        KernelWeight storage kernel = kernelWeights[kernelId];
        require(kernel.isActive, "Kernel not active");
        
        kernel.totalRevenue += amount;
        kernel.executionCount += 1;
        totalIndexRevenue += amount;
        totalKernelExecutions += 1;
        
        // Distribute to token holders
        if (totalSupply() > 0) {
            revenuePerToken += (amount * 1e18) / totalSupply();
        }
        
        emit RevenueDistributed(amount);
    }
    
    /**
     * @notice Mint index tokens (buy into index)
     */
    function mint(uint256 tokenAmount) external payable nonReentrant {
        uint256 cost = getTokenPrice() * tokenAmount / 1e18;
        require(msg.value >= cost, "Insufficient payment");
        
        _mint(msg.sender, tokenAmount);
        revenueDebt[msg.sender] = revenuePerToken * tokenAmount / 1e18;
        
        // Refund excess
        if (msg.value > cost) {
            payable(msg.sender).transfer(msg.value - cost);
        }
        
        emit TokensMinted(msg.sender, tokenAmount, cost);
    }
    
    /**
     * @notice Burn tokens (exit index)
     */
    function burn(uint256 tokenAmount) external nonReentrant {
        require(balanceOf(msg.sender) >= tokenAmount, "Insufficient balance");
        
        // Claim pending revenue first
        _claimRevenue(msg.sender);
        
        uint256 payout = getTokenPrice() * tokenAmount / 1e18;
        _burn(msg.sender, tokenAmount);
        
        payable(msg.sender).transfer(payout);
        emit TokensBurned(msg.sender, tokenAmount, payout);
    }
    
    /**
     * @notice Claim accumulated revenue
     */
    function claimRevenue() external nonReentrant {
        _claimRevenue(msg.sender);
    }
    
    function _claimRevenue(address user) private {
        uint256 pending = pendingRevenue(user);
        if (pending > 0) {
            revenueDebt[user] = revenuePerToken * balanceOf(user) / 1e18;
            payable(user).transfer(pending);
            emit RevenueClaimed(user, pending);
        }
    }
    
    /**
     * @notice Get current token price (NAV)
     */
    function getTokenPrice() public view returns (uint256) {
        if (totalSupply() == 0) return INITIAL_PRICE;
        uint256 nav = address(this).balance + totalIndexRevenue;
        return (nav * 1e18) / totalSupply();
    }
    
    /**
     * @notice Calculate pending revenue for user
     */
    function pendingRevenue(address user) public view returns (uint256) {
        uint256 accumulatedRevenue = revenuePerToken * balanceOf(user) / 1e18;
        return accumulatedRevenue > revenueDebt[user] ? accumulatedRevenue - revenueDebt[user] : 0;
    }
    
    /**
     * @notice Get index composition
     */
    function getComposition() external view returns (
        string[] memory kernels,
        uint256[] memory weights,
        uint256[] memory revenues
    ) {
        uint256 len = kernelList.length;
        kernels = new string[](len);
        weights = new uint256[](len);
        revenues = new uint256[](len);
        
        for (uint256 i = 0; i < len; i++) {
            string memory kernelId = kernelList[i];
            KernelWeight memory kernel = kernelWeights[kernelId];
            kernels[i] = kernelId;
            weights[i] = kernel.weight;
            revenues[i] = kernel.totalRevenue;
        }
    }
    
    /**
     * @notice Get index stats
     */
    function getIndexStats() external view returns (
        uint256 totalRevenue,
        uint256 totalExecutions,
        uint256 tokenPrice,
        uint256 marketCap,
        uint256 kernelCount
    ) {
        return (
            totalIndexRevenue,
            totalKernelExecutions,
            getTokenPrice(),
            totalSupply() * getTokenPrice() / 1e18,
            kernelList.length
        );
    }
    
    receive() external payable {}
}
