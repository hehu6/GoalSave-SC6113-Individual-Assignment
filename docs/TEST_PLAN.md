# GoalSave Test Plan

Record the final result and screenshot filename for each manual test after Sepolia deployment.

## Automated test summary

| ID | Layer | Scenario | Expected result |
| --- | --- | --- | --- |
| C01 | Contract | Create valid goal | Goal stored and indexed under owner |
| C02 | Contract | Deposit from another wallet | Goal balance increases |
| C03 | Contract | Zero deposit / missing goal | Transaction reverts |
| C04 | Contract | Withdraw before target/deadline | Transaction reverts |
| C05 | Contract | Withdraw after target reached | Owner receives funds; status is Withdrawn |
| C06 | Contract | Non-owner withdrawal | Transaction reverts |
| C07 | Contract | Emergency withdrawal | Funds returned; status is EmergencyClosed |
| C08 | Contract | Direct ETH transfer | Transaction reverts |
| B01 | Flask | Home and health routes | HTTP 200 |
| B02 | Flask | Config route | ABI and Sepolia chain ID returned |
| B03 | Flask | Valid goal payload | Normalized payload returned |
| B04 | Flask | Invalid goal payload | HTTP 400 with readable error |
| B05 | Flask | Invalid deposit amounts | HTTP 400 |
| B06 | Flask | Receipt hash / missing RPC | Hash validation and graceful fallback |

## Required Sepolia / browser evidence

| ID | Test | Expected result | Actual result | Screenshot |
| --- | --- | --- | --- | --- |
| M01 | Open Render link | GoalSave loads without server error | Pending | `01-render-home.png` |
| M02 | Connect MetaMask on another network | App requests Sepolia switch | Pending | `02-network-switch.png` |
| M03 | Create valid goal | Confirmed transaction and goal card | Pending | `03-create-goal.png` |
| M04 | Create blank / past-deadline goal | Validation blocks submission | Pending | `04-invalid-goal.png` |
| M05 | Deposit positive test ETH | Balance, progress, and event update | Pending | `05-deposit-success.png` |
| M06 | Deposit zero | Validation blocks submission | Pending | `06-invalid-deposit.png` |
| M07 | Withdraw too early | Button disabled or contract reverts | Pending | `07-withdraw-locked.png` |
| M08 | Reach target and withdraw | Full balance returned; goal closes | Pending | `08-withdraw-success.png` |
| M09 | Open transaction link | Correct Sepolia Etherscan receipt shown | Pending | `09-etherscan.png` |
| M10 | Refresh/reopen app | Goal and history remain available on-chain | Pending | `10-persistence.png` |

## Browser checks

- Desktop width: Chrome/Edge at 1440 × 900.
- Mobile width: DevTools responsive mode around 390 × 844.
- No horizontal scrolling.
- Buttons have clear pending/confirmed/error feedback.
- Wallet address, goal balances, and transaction links are readable.
- MetaMask account/network changes refresh application state.

## Evidence rules

- Do not fabricate screenshots or transaction hashes.
- Keep the MetaMask account address visible where useful, but never expose the seed phrase or private key.
- Use only Sepolia test ETH.
- Add the final contract address, deployment transaction, Render URL, and GitHub URL to the report.
