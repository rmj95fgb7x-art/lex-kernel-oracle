const hre = require("hardhat");
async function main() {
  const oracle = "0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD"; // Base Sepolia Chainlink
  const jobId = "0x6330386435366661343134333461323962663366643834393565303432313466";
  const oracleFee = "100000000000000000"; // 0.1 LINK
  const link = "0xE4aB69C077896252FAFBD49EFD26B5D171A32410"; // Base Sepolia LINK
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with:", deployer.address);
  const Registry = await hre.ethers.getContractFactory("LexKernelRegistry");
  const registry = await Registry.deploy(oracle, jobId, oracleFee, link);
  await registry.waitForDeployment();
  console.log("Registry deployed:", await registry.getAddress());
  const Subscription = await hre.ethers.getContractFactory("LexKernelSubscription");
  const subscription = await Subscription.deploy();
  await subscription.waitForDeployment();
  console.log("Subscription deployed:", await subscription.getAddress());
  console.log("\nRegistering kernels...");
  await registry.registerKernel("kl-052-lexbank", "https://api.lexliberatum.io/kernels/lexbank", 500000);
  await registry.registerKernel("kl-091-lextrade", "https://api.lexliberatum.io/kernels/lextrade", 500000);
  console.log("Done!");
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
