const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LexKernelIndex", function () {
  let index, owner, user1, user2;
  
  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();
    const Index = await ethers.getContractFactory("LexKernelIndex");
    index = await Index.deploy();
    await index.waitForDeployment();
    await index.addKernel("kl-052-lexbank", 5000);
  });
  
  it("Should mint tokens", async function () {
    const price = await index.getTokenPrice();
    await index.connect(user1).mint(ethers.parseEther("10"), { value: price * 10n / ethers.parseEther("1") });
    expect(await index.balanceOf(user1.address)).to.equal(ethers.parseEther("10"));
  });
  
  it("Should distribute revenue", async function () {
    await index.connect(user1).mint(ethers.parseEther("100"), { value: ethers.parseEther("100") });
    await index.recordRevenue("kl-052-lexbank", ethers.parseEther("10"));
    const pending = await index.pendingRevenue(user1.address);
    expect(pending).to.be.gt(0);
  });
});
