from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
TX_HASH_RE = re.compile(r"^0x[a-fA-F0-9]{64}$")
ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
MAX_GOAL_NAME_LENGTH = 64


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def parse_positive_decimal(value, field_name: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    if number.as_tuple().exponent < -18:
        raise ValueError(f"{field_name} supports at most 18 decimal places.")
    return number


def validate_goal_payload(payload: dict) -> dict:
    name = str(payload.get("name", "")).strip()
    if not name:
        raise ValueError("Goal name is required.")
    if len(name.encode("utf-8")) > MAX_GOAL_NAME_LENGTH:
        raise ValueError("Goal name must be at most 64 UTF-8 bytes.")

    target = parse_positive_decimal(payload.get("targetEth"), "Target amount")
    deadline_text = str(payload.get("deadline", "")).strip()
    try:
        deadline = datetime.fromisoformat(deadline_text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Deadline must be a valid date and time.") from exc
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if deadline <= datetime.now(timezone.utc):
        raise ValueError("Deadline must be in the future.")

    return {
        "name": name,
        "targetEth": format(target, "f"),
        "deadlineUnix": int(deadline.timestamp()),
    }


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify(status="ok", service="GoalSave")

    @app.route("/api/config", methods=["GET"])
    def api_config():
        deployment = load_json(BASE_DIR / "deployment.json", {})
        abi = load_json(BASE_DIR / "abi" / "GoalSave.json", [])

        address = os.getenv("CONTRACT_ADDRESS", deployment.get("address", ""))
        chain_id = int(os.getenv("CHAIN_ID", deployment.get("chainId", 11155111)))
        deployment_block = int(
            os.getenv("DEPLOYMENT_BLOCK", deployment.get("deploymentBlock", 0))
        )
        configured = bool(ADDRESS_RE.fullmatch(address or "")) and address != "0x" + "0" * 40

        return jsonify(
            appName="GoalSave",
            abi=abi,
            contractAddress=address,
            chainId=chain_id,
            deploymentBlock=deployment_block,
            configured=configured,
            explorerBase="https://sepolia.etherscan.io",
        )

    @app.route("/api/validate/goal", methods=["POST"])
    def validate_goal():
        try:
            normalized = validate_goal_payload(request.get_json(silent=True) or {})
        except ValueError as exc:
            return jsonify(ok=False, error=str(exc)), 400
        return jsonify(ok=True, value=normalized)

    @app.route("/api/validate/deposit", methods=["POST"])
    def validate_deposit():
        try:
            amount = parse_positive_decimal(
                (request.get_json(silent=True) or {}).get("amountEth"), "Deposit amount"
            )
        except ValueError as exc:
            return jsonify(ok=False, error=str(exc)), 400
        return jsonify(ok=True, value={"amountEth": format(amount, "f")})

    @app.route("/api/transaction/<tx_hash>", methods=["GET"])
    def transaction_status(tx_hash: str):
        if not TX_HASH_RE.fullmatch(tx_hash):
            return jsonify(ok=False, error="Invalid transaction hash."), 400

        rpc_url = os.getenv("SEPOLIA_RPC_URL", "").strip()
        if not rpc_url:
            return jsonify(
                ok=True,
                status="unavailable",
                message="SEPOLIA_RPC_URL is not configured on the server.",
            )

        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_getTransactionReceipt",
                "params": [tx_hash],
            }
        ).encode("utf-8")
        rpc_request = urllib.request.Request(
            rpc_url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(rpc_request, timeout=8) as response:
                result = json.loads(response.read().decode("utf-8")).get("result")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            app.logger.warning("RPC lookup failed: %s", exc)
            return jsonify(ok=False, error="The blockchain RPC service is unavailable."), 502

        if result is None:
            return jsonify(ok=True, status="pending")
        status = "success" if int(result.get("status", "0x0"), 16) == 1 else "reverted"
        return jsonify(
            ok=True,
            status=status,
            blockNumber=int(result["blockNumber"], 16),
            gasUsed=int(result["gasUsed"], 16),
        )

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify(ok=False, error="Not found."), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
