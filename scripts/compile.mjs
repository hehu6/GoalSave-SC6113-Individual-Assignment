import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import solc from "solc";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourcePath = path.join(root, "contracts", "GoalSave.sol");
const source = fs.readFileSync(sourcePath, "utf8");

const input = {
  language: "Solidity",
  sources: { "GoalSave.sol": { content: source } },
  settings: {
    evmVersion: "paris",
    optimizer: { enabled: true, runs: 200 },
    outputSelection: {
      "*": { "*": ["abi", "evm.bytecode.object", "evm.deployedBytecode.object", "metadata"] }
    }
  }
};

const output = JSON.parse(solc.compile(JSON.stringify(input)));
const errors = (output.errors || []).filter((item) => item.severity === "error");
if (errors.length) {
  for (const error of errors) console.error(error.formattedMessage);
  process.exit(1);
}

const compiled = output.contracts["GoalSave.sol"].GoalSave;
const artifact = {
  contractName: "GoalSave",
  compiler: solc.version(),
  abi: compiled.abi,
  bytecode: `0x${compiled.evm.bytecode.object}`,
  deployedBytecode: `0x${compiled.evm.deployedBytecode.object}`
};

fs.mkdirSync(path.join(root, "artifacts"), { recursive: true });
fs.mkdirSync(path.join(root, "abi"), { recursive: true });
fs.writeFileSync(path.join(root, "artifacts", "GoalSave.json"), `${JSON.stringify(artifact, null, 2)}\n`);
fs.writeFileSync(path.join(root, "abi", "GoalSave.json"), `${JSON.stringify(compiled.abi, null, 2)}\n`);

const vendorSource = path.join(root, "node_modules", "ethers", "dist", "ethers.umd.min.js");
const vendorTarget = path.join(root, "static", "vendor", "ethers.umd.min.js");
if (fs.existsSync(vendorSource)) fs.copyFileSync(vendorSource, vendorTarget);

console.log(`Compiled GoalSave with ${solc.version()}`);
console.log(`ABI entries: ${compiled.abi.length}`);
console.log(`Bytecode size: ${compiled.evm.deployedBytecode.object.length / 2} bytes`);
