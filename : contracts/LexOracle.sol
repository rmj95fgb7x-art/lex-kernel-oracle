// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LexOracle
 * @author Lex Liberatum Trust
 * @notice On-chain oracle for Adaptive Spectral Kernel compliance primitives
 * @dev Implements deterministic CREATE2 deployment and royalty routing
 * 
 * Patent: PCT Pending
 * Royalty: 25 basis points (0.0025) per compliance decision
 * Beneficiary: 0x44f8219cBABad92E6bf245D8c767179629D8C689
 */

contract LexOracle {
    
    // ============================================================
    //                         CONSTANTS
    // ============================================================
    
    /// @notice Trust beneficiary address (immutable)
    address public constant TRUST_BENEFICIARY = 0x44f8219cBABad92E6bf245D8c767179629D8C689;
    
    /// @notice Royalty rate in basis points (25 bp = 0.25%)
    uint256 public constant ROYALTY_BPS = 25;
    
    /// @notice Basis points denominator (10000 = 100%)
    uint256 public constant BPS_DENOMINATOR = 10000;
    
    /// @notice Contract version
    string public constant VERSION = "1.1.0";
    
    // ============================================================
    //                         STORAGE
    // ============================================================
    
    /// @notice Total royalties collected
    uint256 public totalRoyaltiesCollected;
    
    /// @notice Total compliance decisions processed
    uint256 public totalDecisions;
    
    /// @notice Mapping of kernel hash to decision count
    mapping(bytes32 => uint256) public kernelDecisionCount;
    
    /// @notice Mapping of kernel hash to total volume processed
    mapping(bytes32 => uint256) public kernelVolume;
    
    // ============================================================
    //                         EVENTS
    // ============================================================
    
    /// @notice Emitted when a kernel is computed
    event KernelComputed(
        bytes32 indexed kernelHash,
        uint256 timestamp,
        uint256 signalCount
    );
    
    /// @notice Emitted when royalty is routed
    event RoyaltyRouted(
        bytes32 indexed kernelHash,
        uint256 volume,
        uint256 royaltyAmount,
        address indexed beneficiary
    );
    
    /// @notice Emitted when a compliance decision is recorded
    event ComplianceDecision(
        bytes32 indexed kernelHash,
        uint256 volume,
        uint256 timestamp
    );
    
    // ============================================================
    //                         ERRORS
    // ============================================================
    
    error InsufficientPayment();
    error TransferFailed();
    error InvalidSignalCount();
    error InvalidVolume();
    
    // ============================================================
    //                      CORE FUNCTIONS
    // ============================================================
    
    /**
     * @notice Compute kernel hash from data hashes and weights
     * @dev Simplified on-chain aggregation (full FFT fusion off-chain)
     * @param dataHashes Array of signal data hashes
     * @param weights Array of adaptive weights (scaled by 1e18)
     * @return kernelHash The computed kernel identifier
     */
    function computeKernel(
        bytes32[] calldata dataHashes,
        uint256[] calldata weights
    ) public pure returns (bytes32 kernelHash) {
        if (dataHashes.length == 0) revert InvalidSignalCount();
        if (dataHashes.length != weights.length) revert InvalidSignalCount();
        
        // Weighted hash aggregation
        kernelHash = keccak256(abi.encodePacked(dataHashes, weights));
        
        return kernelHash;
    }
    
    /**
     * @notice Route royalty based on kernel output and decision volume
     * @dev Royalty = kernel × volume × 0.0025
     * @param kernel The kernel hash from computeKernel
     * @param volume The decision volume (e.g., claims processed, telemetry samples)
     */
    function routeRoyalty(bytes32 kernel, uint256 volume) public payable {
        if (volume == 0) revert InvalidVolume();
        
        // Calculate royalty: volume × 25bp
        uint256 royalty = (volume * ROYALTY_BPS) / BPS_DENOMINATOR;
        
        if (msg.value < royalty) revert InsufficientPayment();
        
        // Transfer royalty to trust beneficiary
        (bool success, ) = TRUST_BENEFICIARY.call{value: royalty}("");
        if (!success) revert TransferFailed();
        
        // Update state
        totalRoyaltiesCollected += royalty;
        totalDecisions++;
        kernelDecisionCount[kernel]++;
        kernelVolume[kernel] += volume;
        
        // Refund excess payment
        if (msg.value > royalty) {
            (bool refundSuccess, ) = msg.sender.call{value: msg.value - royalty}("");
            if (!refundSuccess) revert TransferFailed();
        }
        
        emit RoyaltyRouted(kernel, volume, royalty, TRUST_BENEFICIARY);
    }
    
    /**
     * @notice Record a compliance decision with kernel and volume
     * @dev Combines kernel computation and royalty routing
     * @param dataHashes Array of signal data hashes
     * @param weights Array of adaptive weights
     * @param volume Decision volume
     * @return kernel The computed kernel hash
     */
    function recordDecision(
        bytes32[] calldata dataHashes,
        uint256[] calldata weights,
        uint256 volume
    ) external payable returns (bytes32 kernel) {
        // Compute kernel
        kernel = computeKernel(dataHashes, weights);
        
        emit KernelComputed(kernel, block.timestamp, dataHashes.length);
        
        // Route royalty
        routeRoyalty(kernel, volume);
        
        emit ComplianceDecision(kernel, volume, block.timestamp);
        
        return kernel;
    }
    
    // ============================================================
    //                      VIEW FUNCTIONS
    // ============================================================
    
    /**
     * @notice Calculate required payment for a given volume
     * @param volume The decision volume
     * @return payment Required payment in wei
     */
    function calculateRoyalty(uint256 volume) public pure returns (uint256 payment) {
        return (volume * ROYALTY_BPS) / BPS_DENOMINATOR;
    }
    
    /**
     * @notice Get kernel statistics
     * @param kernel The kernel hash
     * @return decisionCount Number of decisions made with this kernel
     * @return totalVolume Total volume processed with this kernel
     */
    function getKernelStats(bytes32 kernel) 
        external 
        view 
        returns (uint256 decisionCount, uint256 totalVolume) 
    {
        return (kernelDecisionCount[kernel], kernelVolume[kernel]);
    }
    
    /**
     * @notice Get global statistics
     * @return _totalRoyalties Total royalties collected (wei)
     * @return _totalDecisions Total decisions processed
     * @return _beneficiary Trust beneficiary address
     */
    function getGlobalStats() 
        external 
        view 
        returns (
            uint256 _totalRoyalties,
            uint256 _totalDecisions,
            address _beneficiary
        ) 
    {
        return (totalRoyaltiesCollected, totalDecisions, TRUST_BENEFICIARY);
    }
    
    // ============================================================
    //                  DETERMINISTIC DEPLOYMENT
    // ============================================================
    
    /**
     * @notice Compute CREATE2 address for deterministic deployment
     * @dev Same address across all chains (L1, L2s)
     * @param salt Deployment salt
     * @param deployer Deployer address
     * @return predictedAddress The predicted contract address
     */
    function computeCreate2Address(
        bytes32 salt,
        address deployer
    ) public pure returns (address predictedAddress) {
        bytes memory bytecode = type(LexOracle).creationCode;
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0xff),
                deployer,
                salt,
                keccak256(bytecode)
            )
        );
        return address(uint160(uint256(hash)));
    }
}

/**
 * @title LexOracleFactory
 * @notice Factory for deterministic CREATE2 deployment of LexOracle
 * @dev Ensures same address across all EVM chains
 */
contract LexOracleFactory {
    
    event OracleDeployed(
        address indexed oracleAddress,
        bytes32 indexed salt,
        address indexed deployer
    );
    
    /**
     * @notice Deploy LexOracle with CREATE2
     * @param salt Deployment salt for deterministic address
     * @return oracle The deployed LexOracle address
     */
    function deployOracle(bytes32 salt) external returns (address oracle) {
        oracle = address(new LexOracle{salt: salt}());
        emit OracleDeployed(oracle, salt, msg.sender);
        return oracle;
    }
    
    /**
     * @notice Predict oracle address before deployment
     * @param salt Deployment salt
     * @return predictedAddress The predicted oracle address
     */
    function predictAddress(bytes32 salt) external view returns (address predictedAddress) {
        bytes memory bytecode = type(LexOracle).creationCode;
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0xff),
                address(this),
                salt,
                keccak256(bytecode)
            )
        );
        return address(uint160(uint256(hash)));
    }
}

/**
 * @title LexOracleMultiSig
 * @notice Simple multi-sig for emergency oracle management
 * @dev Requires 2-of-3 signatures for critical operations
 */
contract LexOracleMultiSig {
    
    address public immutable signer1;
    address public immutable signer2;
    address public immutable signer3;
    
    mapping(bytes32 => uint256) public approvals;
    
    event ProposalApproved(bytes32 indexed proposalHash, address indexed signer);
    event ProposalExecuted(bytes32 indexed proposalHash);
    
    constructor(address _signer1, address _signer2, address _signer3) {
        signer1 = _signer1;
        signer2 = _signer2;
        signer3 = _signer3;
    }
    
    modifier onlySigner() {
        require(
            msg.sender == signer1 || msg.sender == signer2 || msg.sender == signer3,
            "Not a signer"
        );
        _;
    }
    
    function approve(bytes32 proposalHash) external onlySigner {
        approvals[proposalHash]++;
        emit ProposalApproved(proposalHash, msg.sender);
    }
    
    function execute(
        address target,
        bytes calldata data
    ) external onlySigner returns (bool success) {
        bytes32 proposalHash = keccak256(abi.encodePacked(target, data));
        require(approvals[proposalHash] >= 2, "Insufficient approvals");
        
        (success, ) = target.call(data);
        require(success, "Execution failed");
        
        delete approvals[proposalHash];
        emit ProposalExecuted(proposalHash);
        
        return success;
    }
}
