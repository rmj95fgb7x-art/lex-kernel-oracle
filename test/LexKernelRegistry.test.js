const { expect } = require("chai");
const { ethers } = require("hardhat");
describe("LexKernelRegistry", function () {
  let registry, owner, user;
  beforeEach(async function () {
    [owner, user] = await ethers.getSigners();
    const Registry = await ethers.getContractFactory("LexKernelRegistry");
    registry = await Registry.deploy("0x6090149792dAAeE9D1D568c9f9a6F6B46AA29eFD", "0x6330386435366661343134333461323962663366643834393565303432313466", "100000000000000000", "0xE4aB69C077896252FAFBD49EFD26B5D171A32410");
    await registry.waitForDeployment();
  });
  it("Should register kernel", async function () {
    await registry.registerKernel("kl-052-lexbank", "https://api.test.com", 500000);
    const kernel = await registry.getKernel("kl-052-lexbank");
    expect(kernel.isActive).to.equal(true);
  });
  it("Should execute kernel with fee", async function () {
    await registry.registerKernel("kl-052-lexbank", "https://api.test.com", 500000);
    const fee = await registry.feePerExecution();
    await expect(registry.connect(user).executeKernel("kl-052-lexbank", "0x1234", { value: fee })).to.emit(registry, "KernelExecutionRequested");
  });
  it("Should revert on insufficient fee", async function () {
    await registry.registerKernel("kl-052-lexbank", "https://api.test.com", 500000);
    await expect(registry.connect(user).executeKernel("kl-052-lexbank", "0x1234", { value: 0 })).to.be.reverted;
  });
});
