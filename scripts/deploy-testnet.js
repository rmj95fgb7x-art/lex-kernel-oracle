const hre = require("hardhat");

async function main() {
  const oracle = "0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD"; // Base Sepolia Chainlink
  const jobId = "0x6330386435366661343134333461323962663366643834393565303432313466";
  const oracleFee = "100000000000000000"; // 0.1 LINK
  const link = "0xE4aB69C077896252FAFBD49EFD26B5D171A32410"; // Base Sepolia LINK
  
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with:", deployer.address);
  
  // Deploy Registry
  const Registry = await hre.ethers.getContractFactory("LexKernelRegistry");
  const registry = await Registry.deploy(oracle, jobId, oracleFee, link);
  await registry.waitForDeployment();
  console.log("Registry deployed:", await registry.getAddress());
  
  // Deploy Subscription
  const Subscription = await hre.ethers.getContractFactory("LexKernelSubscription");
  const subscription = await Subscription.deploy();
  await subscription.waitForDeployment();
  console.log("Subscription deployed:", await subscription.getAddress());
  
  // Deploy Index
  const Index = await hre.ethers.getContractFactory("LexKernelIndex");
  const index = await Index.deploy();
  await index.waitForDeployment();
  console.log("Index deployed:", await index.getAddress());
  
  // Deploy Options
  const Options = await hre.ethers.getContractFactory("LexKernelOptions");
  const options = await Options.deploy(await index.getAddress());
  await options.waitForDeployment();
  console.log("Options deployed:", await options.getAddress());
  
  // Deploy AMM
  const AMM = await hre.ethers.getContractFactory("LexKernelAMM");
  const amm = await AMM.deploy(await index.getAddress());
  await amm.waitForDeployment();
  console.log("AMM deployed:", await amm.getAddress());
  
  console.log("\n=== REGISTERING ALL 70 KERNELS ===\n");
  
  // Original 60 kernels
  await registry.registerKernel("kl-001-lexdocket", "https://api.lexliberatum.io/kernels/lexdocket", 500000);
  await registry.registerKernel("kl-003-lexchart", "https://api.lexliberatum.io/kernels/lexchart", 500000);
  await registry.registerKernel("kl-008-lexpay", "https://api.lexliberatum.io/kernels/lexpay", 500000);
  await registry.registerKernel("kl-012-lexgrid", "https://api.lexliberatum.io/kernels/lexgrid", 500000);
  await registry.registerKernel("kl-017-lexvote", "https://api.lexliberatum.io/kernels/lexvote", 500000);
  await registry.registerKernel("kl-021-lexnuke", "https://api.lexliberatum.io/kernels/lexnuke", 500000);
  await registry.registerKernel("kl-027-lexblood", "https://api.lexliberatum.io/kernels/lexblood", 500000);
  await registry.registerKernel("kl-029-lexdrone", "https://api.lexliberatum.io/kernels/lexdrone", 500000);
  await registry.registerKernel("kl-033-lexwater", "https://api.lexliberatum.io/kernels/lexwater", 500000);
  await registry.registerKernel("kl-039-aml-oracle", "https://api.lexliberatum.io/kernels/aml-oracle", 500000);
  await registry.registerKernel("kl-052-lexbank", "https://api.lexliberatum.io/kernels/lexbank", 500000);
  await registry.registerKernel("kl-056-lexoil", "https://api.lexliberatum.io/kernels/lexoilpipe", 500000);
  await registry.registerKernel("kl-062-lextraffic", "https://api.lexliberatum.io/kernels/lextraffic", 500000);
  await registry.registerKernel("kl-067-lexinsure", "https://api.lexliberatum.io/kernels/lexinsure", 500000);
  await registry.registerKernel("kl-073-lexcredit", "https://api.lexliberatum.io/kernels/lexcredit", 500000);
  await registry.registerKernel("kl-074-lexfarm", "https://api.lexliberatum.io/kernels/lexfarm", 500000);
  await registry.registerKernel("kl-081-lexseismic", "https://api.lexliberatum.io/kernels/lexseismic", 500000);
  await registry.registerKernel("kl-084-lexloan", "https://api.lexliberatum.io/kernels/lexloan", 500000);
  await registry.registerKernel("kl-088-lexair", "https://api.lexliberatum.io/kernels/lexair", 500000);
  await registry.registerKernel("kl-091-lextrade", "https://api.lexliberatum.io/kernels/lextrade", 500000);
  await registry.registerKernel("kl-095-lexmine", "https://api.lexliberatum.io/kernels/lexmine", 500000);
  await registry.registerKernel("kl-098-lexad", "https://api.lexliberatum.io/kernels/lexad", 500000);
  await registry.registerKernel("kl-102-lexrail", "https://api.lexliberatum.io/kernels/lexrail", 500000);
  await registry.registerKernel("kl-105-lexfreight", "https://api.lexliberatum.io/kernels/lexfreight", 500000);
  await registry.registerKernel("kl-109-lexhospital", "https://api.lexliberatum.io/kernels/lexhospital", 500000);
  await registry.registerKernel("kl-112-lexprice", "https://api.lexliberatum.io/kernels/lexprice", 500000);
  await registry.registerKernel("kl-116-lexship", "https://api.lexliberatum.io/kernels/lexship", 500000);
  await registry.registerKernel("kl-119-lexclaim", "https://api.lexliberatum.io/kernels/lexclaim", 500000);
  await registry.registerKernel("kl-123-lexfire", "https://api.lexliberatum.io/kernels/lexfire", 500000);
  await registry.registerKernel("kl-126-lexenergy", "https://api.lexliberatum.io/kernels/lexenergy", 500000);
  await registry.registerKernel("kl-130-lexdam", "https://api.lexliberatum.io/kernels/lexdam", 500000);
  await registry.registerKernel("kl-133-lexoption", "https://api.lexliberatum.io/kernels/lexoption", 500000);
  await registry.registerKernel("kl-137-lexbridge", "https://api.lexliberatum.io/kernels/lexbridge", 500000);
  await registry.registerKernel("kl-140-lexforex", "https://api.lexliberatum.io/kernels/lexforex", 500000);
  await registry.registerKernel("kl-147-lexrisk", "https://api.lexliberatum.io/kernels/lexrisk", 500000);
  await registry.registerKernel("kl-154-lexkyc", "https://api.lexliberatum.io/kernels/lexkyc", 500000);
  await registry.registerKernel("kl-161-lexscore", "https://api.lexliberatum.io/kernels/lexscore", 500000);
  await registry.registerKernel("kl-168-lexretail", "https://api.lexliberatum.io/kernels/lexretail", 500000);
  await registry.registerKernel("kl-175-lexmed", "https://api.lexliberatum.io/kernels/lexmed", 500000);
  await registry.registerKernel("kl-182-lextax", "https://api.lexliberatum.io/kernels/lextax", 500000);
  await registry.registerKernel("kl-189-lexsupply", "https://api.lexliberatum.io/kernels/lexsupply", 500000);
  await registry.registerKernel("kl-196-lexphone", "https://api.lexliberatum.io/kernels/lexphone", 500000);
  await registry.registerKernel("kl-203-lexvideo", "https://api.lexliberatum.io/kernels/lexvideo", 500000);
  await registry.registerKernel("kl-210-lexcloud", "https://api.lexliberatum.io/kernels/lexcloud", 500000);
  await registry.registerKernel("kl-217-lexdata", "https://api.lexliberatum.io/kernels/lexdata", 500000);
  await registry.registerKernel("kl-224-lexapi", "https://api.lexliberatum.io/kernels/lexapi", 500000);
  await registry.registerKernel("kl-231-lexdns", "https://api.lexliberatum.io/kernels/lexdns", 500000);
  await registry.registerKernel("kl-238-lexemail", "https://api.lexliberatum.io/kernels/lexemail", 500000);
  await registry.registerKernel("kl-245-lexsearch", "https://api.lexliberatum.io/kernels/lexsearch", 500000);
  await registry.registerKernel("kl-252-lexiot", "https://api.lexliberatum.io/kernels/lexiot", 500000);
  await registry.registerKernel("kl-259-lexgame", "https://api.lexliberatum.io/kernels/lexgame", 500000);
  await registry.registerKernel("kl-266-lexsocial", "https://api.lexliberatum.io/kernels/lexsocial", 500000);
  await registry.registerKernel("kl-273-lexstream", "https://api.lexliberatum.io/kernels/lexstream", 500000);
  await registry.registerKernel("kl-280-lexblock", "https://api.lexliberatum.io/kernels/lexblock", 500000);
  await registry.registerKernel("kl-287-lexauction", "https://api.lexliberatum.io/kernels/lexauction", 500000);
  await registry.registerKernel("kl-294-lexfleet", "https://api.lexliberatum.io/kernels/lexfleet", 500000);
  await registry.registerKernel("kl-301-lexride", "https://api.lexliberatum.io/kernels/lexride", 500000);
  await registry.registerKernel("kl-308-lexfood", "https://api.lexliberatum.io/kernels/lexfood", 500000);
  
  // NEW 10 KERNELS
  await registry.registerKernel("kl-315-lexairport", "https://api.lexliberatum.io/kernels/lexairport", 500000);
  await registry.registerKernel("kl-322-lexhotel", "https://api.lexliberatum.io/kernels/lexhotel", 500000);
  await registry.registerKernel("kl-329-lexaudit", "https://api.lexliberatum.io/kernels/lexaudit", 500000);
  await registry.registerKernel("kl-336-lexinsure", "https://api.lexliberatum.io/kernels/lexinsure", 500000);
  await registry.registerKernel("kl-343-lexweather", "https://api.lexliberatum.io/kernels/lexweather", 500000);
  await registry.registerKernel("kl-350-lexsatellite", "https://api.lexliberatum.io/kernels/lexsatellite", 500000);
  await registry.registerKernel("kl-357-lexcyber", "https://api.lexliberatum.io/kernels/lexcyber", 500000);
  await registry.registerKernel("kl-364-lexpharma", "https://api.lexliberatum.io/kernels/lexpharma", 500000);
  await registry.registerKernel("kl-371-lexoil", "https://api.lexliberatum.io/kernels/lexoilprice", 500000);
  await registry.registerKernel("kl-378-lexedu", "https://api.lexliberatum.io/kernels/lexedu", 500000);
  
  console.log("\n✅ All 70 kernels registered!");
  
  // Add kernels to index
  console.log("\n=== ADDING KERNELS TO INDEX ===\n");
  await index.addKernel("kl-052-lexbank", 1500); // 15%
  await index.addKernel("kl-091-lextrade", 1500); // 15%
  await index.addKernel("kl-098-lexad", 1500); // 15%
  await index.addKernel("kl-140-lexforex", 1000); // 10%
  await index.addKernel("kl-231-lexdns", 2000); // 20%
  await index.addKernel("kl-266-lexsocial", 2000); // 20%
  await index.addKernel("kl-245-lexsearch", 500); // 5%
  
  console.log("✅ Index composition set!");
  
  console.log("\n=== DEPLOYMENT COMPLETE ===");
  console.log("Registry:", await registry.getAddress());
  console.log("Subscription:", await subscription.getAddress());
  console.log("Index:", await index.getAddress());
  console.log("Options:", await options.getAddress());
  console.log("AMM:", await amm.getAddress());
  console.log("\nTotal Kernels: 70");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
