import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import "dotenv/config";
import { ContractFactory, JsonRpcProvider, Wallet } from "ethers";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifact = JSON.parse(fs.readFileSync(path.join(root, "artifacts", "GoalSave.json"), "utf8"));
const rpcUrl = process.env.SEPOLIA_RPC_URL;
const privateKey = process.env.PRIVATE_KEY;

if (!rpcUrl || !privateKey) {
  throw new Error("Set SEPOLIA_RPC_URL and PRIVATE_KEY in a local .env file first.");
}

const provider = new JsonRpcProvider(rpcUrl, 11155111);
const wallet = new Wallet(privateKey, provider);
const network = await provider.getNetwork();
if (network.chainId !== 11155111n) throw new Error(`Expected Sepolia (11155111), received ${network.chainId}.`);

console.log(`Deploying from ${wallet.address}...`);
const factory = new ContractFactory(artifact.abi, artifact.bytecode, wallet);
const contract = await factory.deploy();
const deploymentTx = contract.deploymentTransaction();
const receipt = await deploymentTx.wait();
const address = await contract.getAddress();

const deployment = {
  network: "sepolia",
  chainId: 11155111,
  address,
  deploymentBlock: receipt.blockNumber,
  transactionHash: receipt.hash
};
fs.writeFileSync(path.join(root, "deployment.json"), `${JSON.stringify(deployment, null, 2)}\n`);

console.log(`GoalSave deployed: ${address}`);
console.log(`Transaction: https://sepolia.etherscan.io/tx/${receipt.hash}`);
console.log("deployment.json has been updated. Commit it before deploying the Flask app.");
