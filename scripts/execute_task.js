const hre = require("hardhat");

async function main() {
    const signers = await hre.ethers.getSigners();
    const deployer = signers[0];
    if (!deployer) throw new Error("No deployer found. Check .env");

    const network = await hre.ethers.provider.getNetwork();
    console.log(`=== LexKernel Task Execution (${network.name === 'unknown' ? 'hardhat' : network.name}) ===`);
    console.log("Deployer:", deployer.address);

    // Base Sepolia Testnet Contracts for the oracle
    const oracleAddr = "0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD";
    const jobId = "0x6330386435366661343134333461323962663366643834393565303432313466";
    const oracleFee = hre.ethers.parseUnits("0.1", 18);
    const linkAddr = "0xE4aB69C077896252FAFBD49EFD26B5D171A32410";

    // Ensure we have 2 more users
    let testUsers = signers.slice(1);
    while (testUsers.length < 2) {
        const freshWallet = hre.ethers.Wallet.createRandom(hre.ethers.provider);
        console.log(`Creating test user: ${freshWallet.address}`);
        await (await deployer.sendTransaction({ to: freshWallet.address, value: hre.ethers.parseEther("0.001") })).wait();
        testUsers.push(freshWallet);
    }

    const user1 = testUsers[0];
    const user2 = testUsers[1];
    console.log("User 1:  ", user1.address);
    console.log("User 2:  ", user2.address);

    const beneficiaryAddress = "0x44f8219cBABad92E6bf245D8c767179629D8C689";

    console.log("\n==== SMART CONTRACT DEPLOYMENT ====")

    // Deploy Registry
    console.log("\nDeploying LexKernelRegistry...");
    const Registry = await hre.ethers.getContractFactory("LexKernelRegistry");
    const registry = await Registry.deploy(oracleAddr, jobId, oracleFee, linkAddr);
    await registry.waitForDeployment();
    const registryAddress = await registry.getAddress();
    console.log("Registry deployed to:", registryAddress);
    console.log(`View on Basescan: https://sepolia.basescan.org/address/${registryAddress}`);

    // Deploy Subscription
    console.log("\nDeploying LexKernelSubscription...");
    const Subscription = await hre.ethers.getContractFactory("LexKernelSubscription");
    const subscription = await Subscription.deploy();
    await subscription.waitForDeployment();
    const subscriptionAddress = await subscription.getAddress();
    console.log("Subscription deployed to:", subscriptionAddress);
    console.log(`View on Basescan: https://sepolia.basescan.org/address/${subscriptionAddress}`);

    // Automated LINK Funding
    console.log("\nChecking LINK balance for funding...");
    const linkAbi = [
        "function transfer(address to, uint256 value) external returns (bool)",
        "function balanceOf(address owner) external view returns (uint256)"
    ];
    const linkToken = await hre.ethers.getContractAt(linkAbi, linkAddr);
    const deployerLinkBal = await linkToken.balanceOf(deployer.address);

    if (deployerLinkBal > 0n) {
        const fundAmount = network.chainId === 31337n ? hre.ethers.parseEther("10") : hre.ethers.parseEther("1");
        if (deployerLinkBal >= fundAmount) {
            process.stdout.write(`   Funding Registry with ${hre.ethers.formatEther(fundAmount)} LINK... `);
            await (await linkToken.transfer(registryAddress, fundAmount)).wait();
            console.log("Done!");
        } else {
            console.log(`   Insufficient LINK on deployer to auto-fund (Have: ${hre.ethers.formatEther(deployerLinkBal)} LINK)`);
        }
    } else {
        console.log("   Deployer has 0 LINK. Please fund manually if on testnet.");
    }

    // Register Kernels
    console.log("\nRegistering kernels...");
    const kernelConfigs = [
        { id: "kl-052-lexbank", url: "https://api.lexliberatum.io/kernels/lexbank" },
        { id: "kl-091-lextrade", url: "https://api.lexliberatum.io/kernels/lextrade" },
        { id: "kl-098-lexad", url: "https://api.lexliberatum.io/kernels/lexad" }
    ];
    for (const k of kernelConfigs) {
        const tx = await registry.registerKernel(k.id, k.url, 500000);
        await tx.wait();
        console.log(`   [OK] Registered ${k.id}`);
        console.log(`   Transaction hash: ${tx.hash}`);
    }

    // Set fee to 0.0001 ETH
    console.log("\nSetting fee...");
    const tx_registry = await registry.setFee(hre.ethers.parseEther("0.0001"));
    await tx_registry.wait();
    console.log(`   [OK] Set fee to 0.0001 ETH`);
    console.log(`   Transaction hash: ${tx_registry.hash}`);

    // Execute 5 Transactions
    console.log("\nExecuting 5 transactions...");
    const fee = hre.ethers.parseEther("0.0001");
    const params = hre.ethers.toUtf8Bytes("{}");
    const balBefore = await hre.ethers.provider.getBalance(beneficiaryAddress);

    for (let i = 0; i < 5; i++) {
        const signer = i % 2 === 0 ? user1 : user2;
        process.stdout.write(`   Tx ${i + 1} from ${signer.address.substring(0, 8)}... `);
        try {
            const tx = await registry.connect(signer).executeKernel("kl-052-lexbank", params, { value: fee });
            await tx.wait();
            console.log(`Success! (Tx: ${tx.hash})`);
        } catch (e) {
            console.log(`Failed! (${e.message.split(' (')[0]})`);
        }
    }

    // Verify Royalty
    const balAfter = await hre.ethers.provider.getBalance(beneficiaryAddress);
    console.log(`\nRoyalty Verification:`);
    console.log(`   Beneficiary Balance Before: ${hre.ethers.formatEther(balBefore)} ETH`);
    console.log(`   Beneficiary Balance After:  ${hre.ethers.formatEther(balAfter)} ETH`);
    console.log(`   Difference:                 ${hre.ethers.formatEther(balAfter - balBefore)} ETH`);

    console.log("\n==== FUNCTIONAL TESTING ====")
    // Test Subscription
    console.log("\nTesting Subscription...");
    const plan = await subscription.plans(1); // BASIC
    const tx = await subscription.subscribe(1, { value: plan.monthlyFee });
    await tx.wait();
    console.log(`   User 2 subscribed to BASIC. (Tx: ${tx.hash})`);

    const can = await subscription.canExecute(deployer.address);
    console.log(`   User 2 can execute? ${can}`);

    console.log("   Recording execution...");
    const tx2 = await subscription.recordExecution(deployer.address, "kl-052-lexbank");
    await tx2.wait();
    console.log(`   Executed! (Tx: ${tx2.hash})`);
    const sub = await subscription.subscriptions(deployer.address);
    console.log(`   Executions this month: ${sub.executionsThisMonth}`);

    console.log("\n=== DONE ===");
}

main().catch(console.error);
