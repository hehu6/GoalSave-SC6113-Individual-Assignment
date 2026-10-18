"use strict";

const SEPOLIA_CHAIN_ID = 11155111;
const SEPOLIA_HEX = "0xaa36a7";
const state = {
  config: null,
  provider: null,
  signer: null,
  contract: null,
  account: null,
  goals: []
};

const $ = (selector) => document.querySelector(selector);
const elements = {
  connectButton: $("#connectButton"),
  networkBadge: $("#networkBadge"),
  walletLabel: $("#walletLabel"),
  totalSaved: $("#totalSaved"),
  activeGoals: $("#activeGoals"),
  readyGoals: $("#readyGoals"),
  walletBalance: $("#walletBalance"),
  goalGrid: $("#goalGrid"),
  goalEmpty: $("#goalEmpty"),
  setupNotice: $("#setupNotice"),
  activityList: $("#activityList"),
  goalDialog: $("#goalDialog"),
  depositDialog: $("#depositDialog"),
  goalForm: $("#goalForm"),
  depositForm: $("#depositForm"),
  toastRegion: $("#toastRegion")
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function shortAddress(address) {
  return address ? `${address.slice(0, 6)}…${address.slice(-4)}` : "";
}

function formatEth(value, digits = 4) {
  const number = Number(ethers.formatEther(value));
  return `${number.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: Math.min(2, digits) })} ETH`;
}

function formatDate(unixSeconds) {
  return new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" })
    .format(new Date(Number(unixSeconds) * 1000));
}

function setBusy(button, busy, busyText = "Waiting for MetaMask…") {
  if (!button) return;
  if (busy) {
    button.dataset.originalText = button.textContent;
    button.textContent = busyText;
    button.disabled = true;
  } else {
    button.textContent = button.dataset.originalText || button.textContent;
    button.disabled = false;
  }
}

function toast(title, message, type = "success", timeout = 5200) {
  const item = document.createElement("div");
  item.className = `toast ${type}`;
  item.innerHTML = `<i>${type === "error" ? "!" : "✓"}</i><div><strong>${escapeHtml(title)}</strong><p>${escapeHtml(message)}</p></div>`;
  elements.toastRegion.appendChild(item);
  window.setTimeout(() => item.remove(), timeout);
}

function friendlyError(error) {
  const raw = error?.shortMessage || error?.reason || error?.info?.error?.message || error?.message || "Unknown error";
  if (/user rejected|ACTION_REJECTED|denied transaction/i.test(raw)) return "The MetaMask request was cancelled.";
  if (/insufficient funds/i.test(raw)) return "The wallet does not have enough Sepolia ETH for this transaction and gas.";
  if (/WithdrawalLocked/i.test(raw)) return "This goal is still locked. Reach the target or wait until the deadline.";
  if (/NotGoalOwner/i.test(raw)) return "Only the wallet that created this goal may withdraw it.";
  if (/GoalNotActive/i.test(raw)) return "This goal is already closed.";
  return raw.replace(/^execution reverted: /i, "").slice(0, 220);
}

async function apiJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "Request failed.");
  return body;
}

async function loadConfig() {
  state.config = await apiJson("/api/config");
  elements.setupNotice.hidden = state.config.configured;
}

async function ensureSepolia() {
  const current = await window.ethereum.request({ method: "eth_chainId" });
  if (current === SEPOLIA_HEX) return;
  try {
    await window.ethereum.request({
      method: "wallet_switchEthereumChain",
      params: [{ chainId: SEPOLIA_HEX }]
    });
  } catch (error) {
    if (error.code !== 4902) throw error;
    await window.ethereum.request({
      method: "wallet_addEthereumChain",
      params: [{
        chainId: SEPOLIA_HEX,
        chainName: "Sepolia test network",
        nativeCurrency: { name: "Sepolia ETH", symbol: "ETH", decimals: 18 },
        rpcUrls: ["https://ethereum-sepolia-rpc.publicnode.com"],
        blockExplorerUrls: ["https://sepolia.etherscan.io"]
      }]
    });
  }
}

async function connectWallet() {
  if (!window.ethereum) {
    toast("MetaMask not found", "Install the MetaMask browser extension, then refresh this page.", "error");
    return false;
  }
  setBusy(elements.connectButton, true, "Connecting…");
  try {
    await ensureSepolia();
    state.provider = new ethers.BrowserProvider(window.ethereum);
    await state.provider.send("eth_requestAccounts", []);
    state.signer = await state.provider.getSigner();
    state.account = await state.signer.getAddress();
    state.contract = state.config.configured
      ? new ethers.Contract(state.config.contractAddress, state.config.abi, state.signer)
      : null;
    await loadDashboard();
    return true;
  } catch (error) {
    state.provider = null;
    state.signer = null;
    state.contract = null;
    state.account = null;
    toast("Wallet connection failed", friendlyError(error), "error");
    return false;
  } finally {
    setBusy(elements.connectButton, false);
    updateWalletState(Boolean(state.account));
  }
}

function updateWalletState(connected) {
  elements.networkBadge.classList.toggle("online", connected);
  elements.networkBadge.classList.remove("wrong");
  elements.networkBadge.innerHTML = `<i></i>${connected ? "Sepolia" : "Not connected"}`;
  elements.connectButton.textContent = connected ? shortAddress(state.account) : "Connect wallet";
  elements.walletLabel.textContent = connected ? `Wallet ${state.account}` : "Connect MetaMask to load your goals";
}

async function ensureReady() {
  if (!state.account && !(await connectWallet())) return false;
  if (!state.config.configured || !state.contract) {
    toast("Deployment required", "Add the deployed Sepolia contract address before using this action.", "error");
    elements.setupNotice.scrollIntoView({ behavior: "smooth", block: "center" });
    return false;
  }
  return true;
}

function isReadyToWithdraw(goal) {
  return goal.savedAmount >= goal.targetAmount || Date.now() >= Number(goal.deadline) * 1000;
}

async function loadDashboard() {
  if (!state.account || !state.provider) return;
  const balance = await state.provider.getBalance(state.account);
  elements.walletBalance.textContent = formatEth(balance, 3);

  if (!state.contract) {
    state.goals = [];
    renderGoals();
    elements.activityList.innerHTML = '<div class="activity-empty">Deploy the contract to load on-chain activity.</div>';
    return;
  }

  const ids = await state.contract.getGoalIds(state.account);
  state.goals = await Promise.all(ids.map(async (id) => {
    const goal = await state.contract.getGoal(id);
    return {
      id,
      owner: goal.owner,
      name: goal.name,
      targetAmount: goal.targetAmount,
      savedAmount: goal.savedAmount,
      deadline: goal.deadline,
      createdAt: goal.createdAt,
      status: goal.status
    };
  }));
  renderGoals();
  await loadActivity();
}

function renderGoals() {
  const active = state.goals.filter((goal) => goal.status === 0n);
  const total = active.reduce((sum, goal) => sum + goal.savedAmount, 0n);
  const ready = active.filter(isReadyToWithdraw).length;
  elements.totalSaved.textContent = formatEth(total);
  elements.activeGoals.textContent = String(active.length);
  elements.readyGoals.textContent = String(ready);
  elements.goalEmpty.hidden = state.goals.length > 0;
  elements.goalGrid.innerHTML = "";

  for (const goal of [...state.goals].reverse()) {
    const status = Number(goal.status);
    const statusLabel = ["Active", "Withdrawn", "Emergency closed"][status];
    const progress = goal.targetAmount === 0n ? 0 : Math.min(100, Number(goal.savedAmount * 10000n / goal.targetAmount) / 100);
    const readyNow = isReadyToWithdraw(goal);
    const card = document.createElement("article");
    card.className = "goal-card";
    card.innerHTML = `
      <div class="goal-top">
        <div><span class="goal-id">GOAL #${goal.id}</span><h3>${escapeHtml(goal.name)}</h3></div>
        <span class="status-pill ${status ? "closed" : ""}">${statusLabel}</span>
      </div>
      <div class="goal-numbers"><strong>${formatEth(goal.savedAmount)}</strong><span>of ${formatEth(goal.targetAmount)}</span></div>
      <div class="progress-track" aria-label="${progress}% funded"><i style="width:${progress}%"></i></div>
      <div class="goal-meta">
        <div><span>Progress</span><strong>${progress.toFixed(1)}%</strong></div>
        <div><span>Deadline</span><strong>${formatDate(goal.deadline)}</strong></div>
      </div>
      ${status === 0 ? `<div class="goal-actions">
        <button class="button button-primary" data-action="deposit" data-goal="${goal.id}" data-name="${escapeHtml(goal.name)}">Deposit</button>
        <button class="button button-outline" data-action="withdraw" data-goal="${goal.id}" ${readyNow ? "" : "disabled"}>Withdraw</button>
        <button class="button button-danger" data-action="emergency" data-goal="${goal.id}">Close early</button>
      </div>` : ""}
    `;
    elements.goalGrid.appendChild(card);
  }
}

const eventPresentation = {
  GoalCreated: { label: "Goal created", icon: "+" },
  DepositAdded: { label: "Deposit", icon: "↓" },
  GoalReached: { label: "Target reached", icon: "✓" },
  GoalWithdrawn: { label: "Withdrawal", icon: "↑" },
  EmergencyWithdrawal: { label: "Early close", icon: "!" }
};

async function loadActivity() {
  if (!state.contract || !state.account) return;
  elements.activityList.innerHTML = '<div class="activity-empty">Reading Sepolia events…</div>';
  try {
    const latest = await state.provider.getBlockNumber();
    const fromBlock = state.config.deploymentBlock > 0
      ? state.config.deploymentBlock
      : Math.max(0, latest - 50000);
    const filterSets = [
      state.contract.filters.GoalCreated(null, state.account),
      state.contract.filters.DepositAdded(null, state.account),
      state.contract.filters.GoalReached(null, state.account),
      state.contract.filters.GoalWithdrawn(null, state.account),
      state.contract.filters.EmergencyWithdrawal(null, state.account)
    ];
    const groups = await Promise.all(filterSets.map((filter) => state.contract.queryFilter(filter, fromBlock, "latest")));
    const events = groups.flat().sort((a, b) => b.blockNumber - a.blockNumber || b.index - a.index).slice(0, 20);
    if (!events.length) {
      elements.activityList.innerHTML = '<div class="activity-empty">No GoalSave events found for this wallet yet.</div>';
      return;
    }
    elements.activityList.innerHTML = events.map((event) => {
      const meta = eventPresentation[event.fragment.name];
      const goalId = event.args.goalId;
      const amount = event.fragment.name === "GoalCreated"
        ? `Target ${formatEth(event.args.targetAmount)}`
        : event.args.amount !== undefined
          ? formatEth(event.args.amount)
          : event.args.savedAmount !== undefined
            ? formatEth(event.args.savedAmount)
            : "—";
      const txShort = `${event.transactionHash.slice(0, 8)}…${event.transactionHash.slice(-6)}`;
      return `<div class="activity-row">
        <span class="activity-type"><i>${meta.icon}</i>${meta.label}</span>
        <code>#${goalId}</code>
        <strong>${amount}</strong>
        <a href="${state.config.explorerBase}/tx/${event.transactionHash}" target="_blank" rel="noreferrer"><code>${txShort}</code> ↗</a>
      </div>`;
    }).join("");
  } catch (error) {
    elements.activityList.innerHTML = '<div class="activity-empty">Event history could not be loaded. Try Refresh or check the deployment block.</div>';
    toast("Activity lookup failed", friendlyError(error), "error");
  }
}

function openGoalDialog() {
  ensureReady().then((ready) => {
    if (!ready) return;
    const local = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
    local.setMinutes(local.getMinutes() - local.getTimezoneOffset());
    $("#goalDeadline").value = local.toISOString().slice(0, 16);
    elements.goalDialog.showModal();
  });
}

async function handleGoalSubmit(event) {
  event.preventDefault();
  if (!(await ensureReady())) return;
  const submit = elements.goalForm.querySelector('[type="submit"]');
  setBusy(submit, true);
  try {
    const deadline = new Date($("#goalDeadline").value);
    const validation = await apiJson("/api/validate/goal", {
      method: "POST",
      body: JSON.stringify({
        name: $("#goalName").value,
        targetEth: $("#goalTarget").value,
        deadline: deadline.toISOString()
      })
    });
    const value = validation.value;
    const tx = await state.contract.createGoal(value.name, ethers.parseEther(value.targetEth), value.deadlineUnix);
    toast("Transaction submitted", `Creating the goal: ${shortAddress(tx.hash)}`);
    await tx.wait();
    elements.goalDialog.close();
    elements.goalForm.reset();
    toast("Goal created", "The savings goal is confirmed on Sepolia.");
    await loadDashboard();
  } catch (error) {
    toast("Could not create goal", friendlyError(error), "error");
  } finally {
    setBusy(submit, false);
  }
}

function openDepositDialog(goalId, name) {
  $("#depositGoalId").value = goalId;
  $("#depositTitle").textContent = `Deposit to ${name}`;
  elements.depositDialog.showModal();
}

async function handleDepositSubmit(event) {
  event.preventDefault();
  if (!(await ensureReady())) return;
  const submit = elements.depositForm.querySelector('[type="submit"]');
  setBusy(submit, true);
  try {
    const validation = await apiJson("/api/validate/deposit", {
      method: "POST",
      body: JSON.stringify({ amountEth: $("#depositAmount").value })
    });
    const goalId = $("#depositGoalId").value;
    const tx = await state.contract.deposit(goalId, { value: ethers.parseEther(validation.value.amountEth) });
    toast("Deposit submitted", `Waiting for Sepolia confirmation: ${shortAddress(tx.hash)}`);
    await tx.wait();
    elements.depositDialog.close();
    elements.depositForm.reset();
    toast("Deposit confirmed", "The goal balance and on-chain history are updated.");
    await loadDashboard();
  } catch (error) {
    toast("Deposit failed", friendlyError(error), "error");
  } finally {
    setBusy(submit, false);
  }
}

async function withdrawGoal(goalId, emergency = false) {
  if (!(await ensureReady())) return;
  const message = emergency
    ? "Close this goal early and return its current balance? This action cannot be undone."
    : "Withdraw this goal's full balance to the connected wallet?";
  if (!window.confirm(message)) return;
  try {
    const tx = emergency
      ? await state.contract.emergencyWithdraw(goalId)
      : await state.contract.withdraw(goalId);
    toast("Transaction submitted", `Waiting for confirmation: ${shortAddress(tx.hash)}`);
    await tx.wait();
    toast(emergency ? "Goal closed early" : "Withdrawal confirmed", "The on-chain goal status is now updated.");
    await loadDashboard();
  } catch (error) {
    toast("Withdrawal failed", friendlyError(error), "error");
  }
}

function bindEvents() {
  elements.connectButton.addEventListener("click", connectWallet);
  $("#createGoalButton").addEventListener("click", openGoalDialog);
  $("#heroCreateButton").addEventListener("click", openGoalDialog);
  document.querySelector('[data-action="create"]').addEventListener("click", openGoalDialog);
  $("#refreshButton").addEventListener("click", async () => {
    if (await ensureReady()) await loadDashboard();
  });
  elements.goalForm.addEventListener("submit", handleGoalSubmit);
  elements.depositForm.addEventListener("submit", handleDepositSubmit);
  document.querySelectorAll("[data-close]").forEach((button) => button.addEventListener("click", () => button.closest("dialog").close()));

  elements.goalGrid.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const goalId = button.dataset.goal;
    if (button.dataset.action === "deposit") openDepositDialog(goalId, button.dataset.name);
    if (button.dataset.action === "withdraw") withdrawGoal(goalId, false);
    if (button.dataset.action === "emergency") withdrawGoal(goalId, true);
  });

  if (window.ethereum) {
    window.ethereum.on("accountsChanged", (accounts) => {
      if (!accounts.length) window.location.reload();
      else connectWallet();
    });
    window.ethereum.on("chainChanged", () => window.location.reload());
  }
}

async function init() {
  try {
    if (!window.ethers) throw new Error("The local Ethers.js library could not be loaded.");
    await loadConfig();
    bindEvents();
    if (window.ethereum) {
      const accounts = await window.ethereum.request({ method: "eth_accounts" });
      const chainId = await window.ethereum.request({ method: "eth_chainId" });
      if (accounts.length && chainId === SEPOLIA_HEX) await connectWallet();
      else if (accounts.length && chainId !== SEPOLIA_HEX) {
        elements.networkBadge.classList.add("wrong");
        elements.networkBadge.innerHTML = "<i></i> Wrong network";
      }
    }
  } catch (error) {
    toast("Application setup failed", friendlyError(error), "error", 9000);
  }
}

document.addEventListener("DOMContentLoaded", init);
