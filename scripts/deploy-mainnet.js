const hre = require("hardhat");
async function main() {
  const oracle = "0x"; // Base Mainnet Chainlink
  const jobId = "0x";
  const oracleFee = "100000000000000000";
  const link = "0x"; // Base Mainnet LINK
  const [deployer] = await hre.ethers.getSigners();
  console.log("⚠️  MAINNET DEPLOYMENT");
  console.log("Deployer:", deployer.address);
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Balance:", hre.ethers.formatEther(balance), "ETH");
  const readline = require('readline').createInterface({ input: process.stdin, output: process.stdout });
  await new Promise(resolve => { readline.question('Type YES to deploy: ', answer => { readline.close(); if (answer !== 'YES') process.exit(1); resolve(); }); });
  const Registry = await hre.ethers.getContractFactory("LexKernelRegistry");
  const registry = await Registry.deploy(oracle, jobId, oracleFee, link);
  await registry.waitForDeployment();
  console.log("✅ Registry:", await registry.getAddress());
  const Subscription = await hre.ethers.getContractFactory("LexKernelSubscription");
  const subscription = await Subscription.deploy();
  await subscription.waitForDeployment();
  console.log("✅ Subscription:", await subscription.getAddress());
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
