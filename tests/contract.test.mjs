import assert from "node:assert/strict";
import { before, beforeEach, describe, it } from "node:test";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import ganache from "ganache";
import { BrowserProvider, ContractFactory, parseEther } from "ethers";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
let artifact;
let provider;
let owner;
let contributor;
let contract;

async function expectRevert(action) {
  await assert.rejects(action, /missing revert data|execution reverted|CALL_EXCEPTION/);
}

describe("GoalSave contract", () => {
  before(() => {
    artifact = JSON.parse(fs.readFileSync(path.join(root, "artifacts", "GoalSave.json"), "utf8"));
  });

  beforeEach(async () => {
    const ganacheProvider = ganache.provider({
      logging: { quiet: true },
      wallet: { totalAccounts: 3, defaultBalance: 100 },
      chain: { chainId: 1337 }
    });
    provider = new BrowserProvider(ganacheProvider);
    owner = await provider.getSigner(0);
    contributor = await provider.getSigner(1);
    const factory = new ContractFactory(artifact.abi, artifact.bytecode, owner);
    contract = await factory.deploy();
    await contract.waitForDeployment();
  });

  it("creates a goal and indexes it by owner", async () => {
    const latest = await provider.getBlock("latest");
    const deadline = latest.timestamp + 3600;
    await (await contract.createGoal("Laptop fund", parseEther("1"), deadline)).wait();

    const goal = await contract.getGoal(1);
    assert.equal(goal.owner, await owner.getAddress());
    assert.equal(goal.name, "Laptop fund");
    assert.equal(goal.targetAmount, parseEther("1"));
    assert.deepEqual(Array.from(await contract.getGoalIds(await owner.getAddress())), [1n]);
  });

  it("accepts a contribution and records the new balance", async () => {
    const latest = await provider.getBlock("latest");
    await (await contract.createGoal("Tuition", parseEther("2"), latest.timestamp + 3600)).wait();
    await (await contract.connect(contributor).deposit(1, { value: parseEther("0.4") })).wait();
    assert.equal((await contract.getGoal(1)).savedAmount, parseEther("0.4"));
  });

  it("rejects zero deposits and invalid goals", async () => {
    const latest = await provider.getBlock("latest");
    await (await contract.createGoal("Emergency", parseEther("1"), latest.timestamp + 3600)).wait();
    await expectRevert(() => contract.deposit(1, { value: 0 }));
    await expectRevert(() => contract.deposit(99, { value: 1 }));
  });

  it("locks normal withdrawal before the target and deadline", async () => {
    const latest = await provider.getBlock("latest");
    await (await contract.createGoal("Course fee", parseEther("1"), latest.timestamp + 3600)).wait();
    await (await contract.deposit(1, { value: parseEther("0.2") })).wait();
    await expectRevert(() => contract.withdraw(1));
  });

  it("allows the owner to withdraw after reaching the target", async () => {
    const latest = await provider.getBlock("latest");
    await (await contract.createGoal("Trip", parseEther("0.5"), latest.timestamp + 3600)).wait();
    await (await contract.deposit(1, { value: parseEther("0.5") })).wait();
    await (await contract.withdraw(1)).wait();

    const goal = await contract.getGoal(1);
    assert.equal(goal.savedAmount, 0n);
    assert.equal(goal.status, 1n);
  });

  it("prevents non-owners from withdrawing", async () => {
    const latest = await provider.getBlock("latest");
    await (await contract.createGoal("Owner only", parseEther("0.1"), latest.timestamp + 3600)).wait();
    await (await contract.deposit(1, { value: parseEther("0.1") })).wait();
    await expectRevert(() => contract.connect(contributor).withdraw(1));
  });

  it("supports a clearly labelled emergency withdrawal", async () => {
    const latest = await provider.getBlock("latest");
    await (await contract.createGoal("Rainy day", parseEther("3"), latest.timestamp + 3600)).wait();
    await (await contract.deposit(1, { value: parseEther("0.25") })).wait();
    await (await contract.emergencyWithdraw(1)).wait();

    const goal = await contract.getGoal(1);
    assert.equal(goal.savedAmount, 0n);
    assert.equal(goal.status, 2n);
  });

  it("rejects direct ETH transfers so every deposit is attributed", async () => {
    await expectRevert(() => owner.sendTransaction({ to: contract.target, value: 1n }));
  });
});
