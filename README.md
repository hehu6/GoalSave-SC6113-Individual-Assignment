# GoalSave — SC6113 Individual Assignment

GoalSave is a goal-based savings DApp for Ethereum Sepolia. A user creates a named savings goal, deposits test ETH through MetaMask, follows progress on a responsive dashboard, and withdraws once the target or deadline is reached. An explicit early-close action is available for emergencies and is recorded separately on-chain.

> Educational project only. It uses Sepolia test ETH and is not a production financial service.

## Submission links

- Render application: **add after deployment**
- Sepolia contract: <https://sepolia.etherscan.io/address/0x80c18baaf6102a26f5fedd337ef33ff1576c69fd>
- GitHub repository: <https://github.com/hehu6/GoalSave-SC6113-Individual-Assignment>

## Assignment deliverables

| Required item | Location |
| --- | --- |
| Solidity contract | `contracts/GoalSave.sol` |
| ABI | `abi/GoalSave.json` |
| Python Flask | `app.py` |
| HTML | `templates/index.html` |
| CSS | `static/styles.css` |
| JavaScript | `static/app.js` |
| Render configuration | `render.yaml`, `Procfile` |
| Smart-contract tests | `tests/contract.test.mjs` |
| Flask tests | `tests/test_app.py` |
| Test plan | `docs/TEST_PLAN.md` |
| Report | `docs/GoalSave_SC6113_Report.pdf` |
| Editable report generator | `docs/report_source.py` |

## Architecture

```text
Browser UI (HTML/CSS/JS)
  ├─ MetaMask + Ethers.js ───────> GoalSave.sol on Sepolia
  │                                  └─ emits verifiable events
  └─ Flask JSON endpoints ───────> validation, ABI/config, receipt lookup
                                     └─ hosted on Render
```

Flask never receives or stores a wallet private key. State-changing transactions are signed in MetaMask. Goal state and transaction history come from the contract, so a database is not required.

## Smart-contract rules

1. `createGoal(name, targetAmount, deadline)` creates a wallet-owned goal.
2. `deposit(goalId)` accepts a positive ETH contribution to an active goal.
3. `withdraw(goalId)` is owner-only and unlocks after the target is reached or deadline passes.
4. `emergencyWithdraw(goalId)` returns current savings and permanently labels the goal as emergency closed.
5. Direct ETH transfers revert so every deposit is attributed to a goal.
6. Checks-effects-interactions and a non-reentrancy guard protect withdrawal calls.

## Run locally

### 1. Python application

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

### 2. Compile the contract and generate the ABI

Install Node.js 20+ and pnpm, then run:

```bash
pnpm install
pnpm run compile
```

Compilation writes `artifacts/GoalSave.json`, `abi/GoalSave.json`, and the local browser copy of Ethers.js.

### 3. Run the automated tests

```bash
pnpm test
python -m unittest discover -s tests -p "test_*.py" -v
```

The contract suite runs against a temporary in-memory Ganache chain. No wallet or test ETH is needed.

To regenerate the eight-page report after editing the identity/link values at the top of `docs/report_source.py`:

```bash
pip install -r requirements-dev.txt
python docs/report_source.py
```

Replace the local preview images with real Render, MetaMask, and Etherscan evidence before the final PDF is submitted.

## Deploy the smart contract to Sepolia

### Recommended classroom-friendly method: Remix + MetaMask

1. Open [Remix](https://remix.ethereum.org/), create `GoalSave.sol`, and paste `contracts/GoalSave.sol`.
2. Compile with Solidity `0.8.30`, optimizer enabled, 200 runs.
3. In **Deploy & Run**, choose **Injected Provider - MetaMask** and verify the network is Sepolia.
4. Click **Deploy** and approve the transaction.
5. On Sepolia Etherscan, record the contract address, deployment transaction, and deployment block.
6. Update `deployment.json` with those three values.

### Script method

Copy `.env.example` to `.env`, use a disposable test-only wallet, then run:

```bash
pnpm run deploy:sepolia
```

Never commit `.env` or a private key. The script verifies chain ID `11155111` and updates `deployment.json` after confirmation.

## Deploy Flask to Render

1. Push the project to your own public or private GitHub repository.
2. In Render, choose **New → Blueprint** and select the repository. `render.yaml` supplies the build/start commands.
3. Set these Render environment variables:
   - `CONTRACT_ADDRESS`: deployed Sepolia address
   - `DEPLOYMENT_BLOCK`: block number from Etherscan
   - `CHAIN_ID`: `11155111`
   - `SEPOLIA_RPC_URL`: optional; enables the server receipt-status endpoint
4. Deploy, open the Render URL, and check `/health` returns `{"service":"GoalSave","status":"ok"}`.
5. Add the Render, contract, and GitHub links to this README and the report.

## Manual demonstration flow

1. Open the Render site in a desktop browser with MetaMask.
2. Connect a Sepolia account.
3. Create a goal such as **Professional course**, target `0.02 ETH`, deadline next week.
4. Deposit `0.01 ETH`; confirm the balance and event history update.
5. Try normal withdrawal: it should remain locked before the target/deadline.
6. Deposit the remaining `0.01 ETH`, then withdraw successfully.
7. Open both transactions on Sepolia Etherscan.
8. Create a second small goal and demonstrate **Close early**.

Use small amounts of free Sepolia test ETH. Do not use real ETH.

## Security and limitations

- Input validation is performed in both Flask/JavaScript and Solidity.
- Only the goal owner may withdraw.
- Withdrawals update state before the external ETH call and use a re-entrancy guard.
- The UI checks Sepolia chain ID before constructing the contract.
- The app is not audited and must not be used with real funds.
- Event queries through MetaMask may be slow on free RPC endpoints; `DEPLOYMENT_BLOCK` limits the query range.
- Emergency withdrawal weakens savings discipline by design, but it is explicit, irreversible, and independently recorded.

## Project structure

```text
GoalSave-SC6113/
├── abi/GoalSave.json
├── artifacts/GoalSave.json
├── contracts/GoalSave.sol
├── docs/
│   ├── GoalSave_SC6113_Report.pdf
│   ├── report_source.py
│   ├── TEST_PLAN.md
│   └── screenshots/
├── scripts/
│   ├── compile.mjs
│   └── deploy.mjs
├── static/
│   ├── app.js
│   ├── styles.css
│   └── vendor/ethers.umd.min.js
├── templates/index.html
├── tests/
│   ├── contract.test.mjs
│   └── test_app.py
├── app.py
├── deployment.json
├── render.yaml
└── requirements.txt
```

## Course reference and declaration

The development approach was informed by the lecturer's public SC6113 `paynow` storage example: <https://gist.github.com/teohteiktoe/84327003ab22a8829a681b84e4b3ad19>. That example stores three values and does not transfer ETH. GoalSave's financial logic, UI, tests, and documentation are a separate implementation.

Before submission, replace the placeholders in the report, review and understand every file, and follow NTU's academic-integrity rules. You are responsible for explaining the design and demonstrating the transactions.
