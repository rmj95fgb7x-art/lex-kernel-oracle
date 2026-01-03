const hre = require("hardhat");
async function main() {
  console.log("Deploying Kernel Index System...");
  
  // Deploy Index Token
  const Index = await hre.ethers.getContractFactory("LexKernelIndex");
  const index = await Index.deploy();
  await index.waitForDeployment();
  console.log("LKI Index:", await index.getAddress());
  
  // Deploy Options
  const Options = await hre.ethers.getContractFactory("LexKernelOptions");
  const options = await Options.deploy(await index.getAddress());
  await options.waitForDeployment();
  console.log("Options:", await options.getAddress());
  
  // Deploy AMM
  const AMM = await hre.ethers.getContractFactory("LexKernelAMM");
  const amm = await AMM.deploy(await index.getAddress());
  await amm.waitForDeployment();
  console.log("AMM:", await amm.getAddress());
  
  // Add kernels to index
  console.log("\nAdding kernels to index...");
  await index.addKernel("kl-052-lexbank", 2000); // 20%
  await index.addKernel("kl-091-lextrade", 1500); // 15%
  await index.addKernel("kl-098-lexad", 1500); // 15%
  await index.addKernel("kl-140-lexforex", 1000); // 10%
  await index.addKernel("kl-231-lexdns", 2000); // 20%
  await index.addKernel("kl-266-lexsocial", 2000); // 20%
  
  console.log("✅ Index deployed and configured!");
}
main();
