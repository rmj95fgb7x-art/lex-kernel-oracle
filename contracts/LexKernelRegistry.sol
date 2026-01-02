// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";

/**
 * @title LexKernelRegistry
 * @notice Production-ready kernel execution registry with Chainlink integration
 * @dev Handles kernel registration, execution requests, and royalty distribution
 */
contract LexKernelRegistry is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;

    // ============ STATE VARIABLES ============
    
    address public immutable beneficiary = 0x44f8219cBABad92E6bf245D8c767179629D8C689;
    uint256 public feePerExecution = 0.0025 ether; // 25 basis points (0.25%)
    
    // Chainlink oracle configuration
    address public oracle;
    bytes32 public jobId;
    uint256 public oracleFee;
    
    // Kernel tracking
    mapping(string => KernelMetadata) public kernels;
    mapping(bytes32 => ExecutionRequest) public requests;
    
    uint256 public totalExecutions;
    uint256 public totalFeesCollected;
    
    // ============ STRUCTS ============
    
    struct KernelMetadata {
        string kernelId;        // e.g., "kl-052-lexbank"
        bool isActive;
        uint256 executionCount;
        uint256 feesCollected;
        string endpoint;        // Off-chain API endpoint
        uint256 gasLimit;       // Max gas for callback
    }
    
    struct ExecutionRequest {
        bytes32 requestId;
        string kernelId;
        address requester;
        bytes parameters;
        uint256 timestamp;
        bool fulfilled;
        bytes result;
    }
    
    // ============ EVENTS ============
    
    event KernelRegistered(string indexed kernelId, string endpoint);
    event KernelExecutionRequested(
        bytes32 indexed requestId,
        string indexed kernelId,
        address indexed requester,
        bytes parameters
    );
    event KernelExecutionFulfilled(
        bytes32 indexed requestId,
        string indexed kernelId,
        bytes result
    );
    event FeeUpdated(uint256 oldFee, uint256 newFee);
    event FeeWithdrawn(address indexed beneficiary, uint256 amount);
    
    // ============ ERRORS ============
    
    error KernelNotActive(string kernelId);
    error InsufficientFee(uint256 required, uint256 provided);
    error RequestNotFound(bytes32 requestId);
    error RequestAlreadyFulfilled(bytes32 requestId);
    error KernelAlreadyRegistered(string kernelId);
    
    // ============ CONSTRUCTOR ============
    
    constructor(
        address _oracle,
        bytes32 _jobId,
        uint256 _oracleFee,
        address _link
    ) ConfirmedOwner(msg.sender) {
        setChainlinkToken(_link);
        oracle = _oracle;
        jobId = _jobId;
        oracleFee = _oracleFee;
    }
    
    // ============ CORE FUNCTIONS ============
    
    /**
     * @notice Register a new kernel
     * @param kernelId Unique kernel identifier (e.g., "kl-052-lexbank")
     * @param endpoint Off-chain API endpoint URL
     * @param gasLimit Max gas for callback
     */
    function registerKernel(
        string calldata kernelId,
        string calldata endpoint,
        uint256 gasLimit
    ) external onlyOwner {
        if (kernels[kernelId].isActive) {
            revert KernelAlreadyRegistered(kernelId);
        }
        
        kernels[kernelId] = KernelMetadata({
            kernelId: kernelId,
            isActive: true,
            executionCount: 0,
            feesCollected: 0,
            endpoint: endpoint,
            gasLimit: gasLimit
        });
        
        emit KernelRegistered(kernelId, endpoint);
    }
    
    /**
     * @notice Execute a kernel with parameters
     * @param kernelId Kernel to execute
     * @param parameters JSON-encoded parameters
     * @return requestId Chainlink request ID
     */
    function executeKernel(
        string calldata kernelId,
        bytes calldata parameters
    ) external payable returns (bytes32 requestId) {
        KernelMetadata storage kernel = kernels[kernelId];
        
        if (!kernel.isActive) {
            revert KernelNotActive(kernelId);
        }
        
        if (msg.value < feePerExecution) {
            revert InsufficientFee(feePerExecution, msg.value);
        }
        
        // Build Chainlink request
        Chainlink.Request memory req = buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfillKernelExecution.selector
        );
        
        // Set request parameters
        req.add("kernelId", kernelId);
        req.add("endpoint", kernel.endpoint);
        req.addBytes("parameters", parameters);
        
        // Send Chainlink request
        requestId = sendChainlinkRequestTo(oracle, req, oracleFee);
        
        // Store request
        requests[requestId] = ExecutionRequest({
            requestId: requestId,
            kernelId: kernelId,
            requester: msg.sender,
            parameters: parameters,
            timestamp: block.timestamp,
            fulfilled: false,
            result: ""
        });
        
        // Update stats
        kernel.executionCount++;
        kernel.feesCollected += msg.value;
        totalExecutions++;
        totalFeesCollected += msg.value;
        
        // Transfer fee to beneficiary
        payable(beneficiary).transfer(msg.value);
        
        emit KernelExecutionRequested(requestId, kernelId, msg.sender, parameters);
    }
    
    /**
     * @notice Chainlink callback - fulfills kernel execution
     * @param requestId Request ID
     * @param result Execution result from off-chain kernel
     */
    function fulfillKernelExecution(
        bytes32 requestId,
        bytes memory result
    ) public recordChainlinkFulfillment(requestId) {
        ExecutionRequest storage request = requests[requestId];
        
        if (request.timestamp == 0) {
            revert RequestNotFound(requestId);
        }
        
        if (request.fulfilled) {
            revert RequestAlreadyFulfilled(requestId);
        }
        
        request.fulfilled = true;
        request.result = result;
        
        emit KernelExecutionFulfilled(requestId, request.kernelId, result);
    }
    
    // ============ VIEW FUNCTIONS ============
    
    /**
     * @notice Get kernel metadata
     */
    function getKernel(string calldata kernelId) 
        external 
        view 
        returns (KernelMetadata memory) 
    {
        return kernels[kernelId];
    }
    
    /**
     * @notice Get execution request details
     */
    function getRequest(bytes32 requestId) 
        external 
        view 
        returns (ExecutionRequest memory) 
    {
        return requests[requestId];
    }
    
    /**
     * @notice Get global statistics
     */
    function getStats() external view returns (
        uint256 executions,
        uint256 fees,
        address beneficiaryAddress
    ) {
        return (totalExecutions, totalFeesCollected, beneficiary);
    }
    
    // ============ ADMIN FUNCTIONS ============
    
    /**
     * @notice Update execution fee
     */
    function setFee(uint256 newFee) external onlyOwner {
        uint256 oldFee = feePerExecution;
        feePerExecution = newFee;
        emit FeeUpdated(oldFee, newFee);
    }
    
    /**
     * @notice Toggle kernel active status
     */
    function setKernelActive(string calldata kernelId, bool active) 
        external 
        onlyOwner 
    {
        kernels[kernelId].isActive = active;
    }
    
    /**
     * @notice Update oracle configuration
     */
    function updateOracle(
        address _oracle,
        bytes32 _jobId,
        uint256 _oracleFee
    ) external onlyOwner {
        oracle = _oracle;
        jobId = _jobId;
        oracleFee = _oracleFee;
    }
    
    /**
     * @notice Withdraw LINK tokens
     */
    function withdrawLink() external onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }
}
