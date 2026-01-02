const { SubscriptionManager, SecretsManager, simulateScript, ResponseListener, ReturnType, decodeResult, FulfillmentCode } = require("@chainlink/functions-toolkit");
const { ethers } = require("hardhat");
async function main() {
  const [signer] = await ethers.getSigners();
  const functionsRouter = "0x234a5fb5Bd614a7AA2FfAB244D603abFA0Ac5C5C"; // Base Sepolia
  const subscriptionId = 1; // Your subscription ID
  const source = require("fs").readFileSync("./chainlink/source.js").toString();
  const manager = new SubscriptionManager({ signer, linkTokenAddress: "0xE4aB69C077896252FAFBD49EFD26B5D171A32410", functionsRouterAddress: functionsRouter });
  await manager.initialize();
  console.log("Deploying Chainlink Function...");
  const response = await manager.createSubscription();
  console.log("Subscription created:", response);
}
main();
