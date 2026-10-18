from pathlib import Path
import shutil

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


STUDENT_NAME = "HE HUZHENGXIONG"
STUDENT_ID = "G2509011E"
GITHUB_URL = "https://github.com/hehu6/GoalSave-SC6113-Individual-Assignment"
RENDER_URL = "https://goalsave-sc6113.onrender.com"
CONTRACT_ADDRESS = "0x80c18baaf6102a26f5fedd337ef33ff1576c69fd"
DEPLOYMENT_BLOCK = "11939866"
DEPLOYMENT_TX = "0x8ebf4a34d05ac7626a89cbfb4a6a78e3ca1725584b9ac3a2af6e6a3c1c7a9370"
WITHDRAWAL_TX = "0xf5f6315cbab1288cc38179799ae135a8ba09033b923bcef038ca2c5991b4e09f"
WALLET_ADDRESS = "0xBF51ed4F673890aD94c1210624a58a83d8230865"

ROOT = Path(__file__).resolve().parents[1]
THREAD_ROOT = ROOT.parents[1]
OUTPUT_DIR = THREAD_ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = OUTPUT_DIR / "GoalSave_SC6113_Final_Report.pdf"
REPO_COPY = ROOT / "docs" / "GoalSave_SC6113_Report.pdf"
SHOTS = ROOT / "docs" / "screenshots"

PAGE_W, PAGE_H = A4
INK = colors.HexColor("#111510")
MUTED = colors.HexColor("#62675E")
PAPER = colors.HexColor("#F7F6F0")
CARD = colors.HexColor("#FFFDF8")
LINE = colors.HexColor("#D9D9D9")
GREEN = colors.HexColor("#6E8B08")
NIGHT = colors.HexColor("#182018")
PALE_GRAY = colors.HexColor("#F0F1ED")


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Kicker", fontName="Courier-Bold", fontSize=8.2, leading=10.5, textColor=GREEN, spaceAfter=9, tracking=1.1))
styles.add(ParagraphStyle(name="TitleX", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=31, leading=34, textColor=INK, spaceAfter=11))
styles.add(ParagraphStyle(name="Subtitle", fontName="Helvetica", fontSize=12.5, leading=18, textColor=MUTED, spaceAfter=10))
styles.add(ParagraphStyle(name="H1X", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=INK, spaceAfter=11))
styles.add(ParagraphStyle(name="H2X", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=INK, spaceBefore=5, spaceAfter=6))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13.6, textColor=colors.HexColor("#343830"), spaceAfter=6))
styles.add(ParagraphStyle(name="BulletX", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.0, leading=13.2, leftIndent=10, firstLineIndent=-8, textColor=colors.HexColor("#343830"), spaceAfter=4))
styles.add(ParagraphStyle(name="SmallX", fontName="Helvetica", fontSize=7.6, leading=10.5, textColor=MUTED, spaceAfter=4))
styles.add(ParagraphStyle(name="CaptionX", fontName="Helvetica", fontSize=7.5, leading=9.5, alignment=TA_CENTER, textColor=MUTED, spaceBefore=3))
styles.add(ParagraphStyle(name="TableHeadX", fontName="Helvetica-Bold", fontSize=7.5, leading=9.5, textColor=colors.white))
styles.add(ParagraphStyle(name="TableCellX", fontName="Helvetica", fontSize=7.3, leading=10, textColor=INK))
styles.add(ParagraphStyle(name="TableCellSmallX", fontName="Helvetica", fontSize=6.7, leading=8.7, textColor=INK))


def P(text, style="BodyX"):
    return Paragraph(text, styles[style])


def bullets(items):
    return [P(f"- {item}", "BulletX") for item in items]


def section_title(number, kicker, title, intro=None):
    result = [P(f"{number}  {kicker.upper()}", "Kicker"), P(title, "H1X")]
    if intro:
        result.append(P(intro))
    result.append(Spacer(1, 2 * mm))
    return result


def data_table(rows, widths, small=False, header=True):
    body_style = "TableCellSmallX" if small else "TableCellX"
    formatted = []
    for row_index, row in enumerate(rows):
        style = "TableHeadX" if header and row_index == 0 else body_style
        formatted.append([cell if hasattr(cell, "wrap") else P(str(cell), style) for cell in row])
    table = Table(formatted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    start = 0
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), NIGHT))
        start = 1
    for row_index in range(start, len(rows)):
        fill = CARD if (row_index - start) % 2 == 0 else PALE_GRAY
        commands.append(("BACKGROUND", (0, row_index), (-1, row_index), fill))
    table.setStyle(TableStyle(commands))
    return table


def scaled_image(path, width_mm, max_height_mm=None):
    path = Path(path)
    with PILImage.open(path) as image:
        pixel_w, pixel_h = image.size
    width = width_mm * mm
    height = width * pixel_h / pixel_w
    if max_height_mm is not None and height > max_height_mm * mm:
        height = max_height_mm * mm
        width = height * pixel_w / pixel_h
    return Image(str(path), width=width, height=height)


def figure(path, width_mm, caption, max_height_mm=None):
    image = scaled_image(path, width_mm, max_height_mm)
    table = Table([[image], [P(caption, "CaptionX")]], colWidths=[image.drawWidth + 6 * mm], hAlign="CENTER")
    table.setStyle(TableStyle([
        ("BOX", (0, 0), (0, 0), 0.6, LINE),
        ("BACKGROUND", (0, 0), (0, 0), colors.white),
        ("LEFTPADDING", (0, 0), (0, 0), 3 * mm),
        ("RIGHTPADDING", (0, 0), (0, 0), 3 * mm),
        ("TOPPADDING", (0, 0), (0, 0), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (0, 0), 3 * mm),
        ("TOPPADDING", (0, 1), (0, 1), 2 * mm),
        ("BOTTOMPADDING", (0, 1), (0, 1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def two_figures(left, right, left_width=78, right_width=78):
    table = Table([[left, right]], colWidths=[left_width * mm, right_width * mm], hAlign="CENTER")
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 3 * mm),
        ("LEFTPADDING", (1, 0), (1, 0), 3 * mm),
        ("RIGHTPADDING", (1, 0), (1, 0), 0),
    ]))
    return table


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    if doc.page == 1:
        canvas.setFillColor(colors.HexColor("#EAF5B5"))
        canvas.circle(PAGE_W - 18 * mm, PAGE_H - 15 * mm, 50 * mm, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor("#F7E2D0"))
        canvas.circle(-7 * mm, 15 * mm, 31 * mm, stroke=0, fill=1)
    else:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(22 * mm, PAGE_H - 18 * mm, PAGE_W - 22 * mm, PAGE_H - 18 * mm)
        canvas.setFont("Helvetica-Bold", 7.2)
        canvas.setFillColor(INK)
        canvas.drawString(22 * mm, PAGE_H - 14 * mm, "GOALSAVE  SC6113 INDIVIDUAL ASSIGNMENT")
        canvas.setFont("Courier", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(22 * mm, 12 * mm, f"{STUDENT_NAME}  {STUDENT_ID}")
        canvas.drawRightString(PAGE_W - 22 * mm, 12 * mm, f"{doc.page:02d} / 08")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4,
    leftMargin=22 * mm, rightMargin=22 * mm,
    topMargin=25 * mm, bottomMargin=20 * mm,
    title="GoalSave SC6113 Individual Assignment Report",
    author=STUDENT_NAME,
    subject="Financial decentralized application on Ethereum Sepolia",
)

story = []

# Page 1
story += [
    Spacer(1, 12 * mm),
    P("SC6113  BLOCKCHAIN APPLICATIONS", "Kicker"),
    P("GoalSave Individual Assignment Report", "TitleX"),
    P("Goal based savings DApp on Ethereum Sepolia", "Subtitle"),
    Spacer(1, 2 * mm),
    figure(SHOTS / "01-render-home.png", 151, "Live Render application connected to MetaMask on Sepolia", 82),
    Spacer(1, 7 * mm),
    data_table([
        ["Student", "Module", "Submission"],
        [f"{STUDENT_NAME}<br/>{STUDENT_ID}", "SC6113", "Individual Assignment"],
        ["Project", "Network", "Date"],
        ["GoalSave", "Ethereum Sepolia<br/>Chain ID 11155111", "18 October 2026"],
    ], [58 * mm, 50 * mm, 55 * mm]),
    Spacer(1, 7 * mm),
    P("GoalSave implements a complete DApp lifecycle: a Solidity contract stores savings goals and controls ETH withdrawals; MetaMask signs every state changing action; Flask serves configuration and validation; and the public Render interface reads contract state and events from Sepolia."),
    P("<b>Key result</b>  The deployed application completed a live create, deposit, target reached, and withdrawal demonstration. Etherscan recorded the contract returning 0.002 Sepolia ETH to the connected wallet."),
    PageBreak(),
]

# Page 2
story += section_title("01", "Introduction and scope", "Financial problem and project objectives", "GoalSave addresses a simple financial problem: a person can set a savings target, but a private spreadsheet or banking note does not provide a shared and independently verifiable history. The DApp records the goal rules, deposits, and final outcome on Sepolia.")
story += [
    P("Problem statement", "H2X"),
    P("A conventional savings note can be edited without leaving an audit trail. It also gives contributors no direct way to verify the current balance or confirm that the owner followed the stated withdrawal rule. GoalSave uses an Ethereum smart contract as the source of truth for ownership, target amount, deadline, balance, and status."),
    P("Objectives", "H2X"),
] + bullets([
    "Allow one wallet to create multiple named savings goals with a target and future deadline.",
    "Accept real Sepolia ETH deposits and calculate progress from contract state.",
    "Permit normal withdrawal only after the target is reached or the deadline passes.",
    "Provide a separately labelled emergency close path and a permanent event trail.",
    "Give clear wallet, network, transaction, validation, and error feedback in the web interface.",
]) + [
    Spacer(1, 3 * mm), P("Technologies used", "H2X"),
    data_table([
        ["Layer", "Technology", "Role in GoalSave"],
        ["Smart contract", "Solidity 0.8.30", "Goal state, ETH accounting, access control, events"],
        ["Blockchain", "Ethereum Sepolia", "Public testnet execution and transaction evidence"],
        ["Wallet", "MetaMask", "Account connection, network switching, transaction signing"],
        ["Frontend", "HTML, CSS, JavaScript, Ethers.js", "Responsive dashboard and contract interaction"],
        ["Backend", "Python Flask", "Hosting, ABI/config API, input validation, health check"],
        ["Hosting", "Render", "Public Gunicorn web service"],
        ["Version control", "GitHub", "Source code and deployment configuration"],
        ["Testing", "Node test runner, Ganache, unittest", "Contract and Flask verification"],
    ], [34 * mm, 45 * mm, 84 * mm], small=True),
    Spacer(1, 5 * mm), P("Assignment fit", "H2X"),
    P("The project is a digital savings and deposit system, one of the financial application areas identified in the individual assignment brief. It includes the required Solidity, ABI, Flask, HTML, CSS, JavaScript, GitHub, Render, transaction history, validation, and screenshots."),
    PageBreak(),
]

# Page 3
story += section_title("02", "System architecture", "Wallet first design with a thin backend", "The blockchain is the source of truth. Flask serves the web application and performs supporting validation, while MetaMask keeps the private key and all transaction approvals under the user's control.")
architecture = Table([
    [P("BROWSER", "TableHeadX"), P("METAMASK", "TableHeadX"), P("SEPOLIA", "TableHeadX")],
    [P("HTML and CSS interface<br/>Ethers.js contract client<br/>Goal and event rendering", "TableCellX"), P("Account selection<br/>Sepolia network approval<br/>Transaction signature", "TableCellX"), P("GoalSave contract<br/>ETH custody<br/>Immutable event log", "TableCellX")],
    [P("FLASK ON RENDER", "TableHeadX"), P("JSON ENDPOINTS", "TableHeadX"), P("PUBLIC EXPLORER", "TableHeadX")],
    [P("Template and static hosting<br/>Gunicorn process<br/>Health monitoring", "TableCellX"), P("ABI and chain config<br/>Goal validation<br/>Deposit validation", "TableCellX"), P("Sepolia Etherscan<br/>Deployment receipt<br/>Action receipts", "TableCellX")],
], colWidths=[54.3 * mm] * 3)
architecture.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NIGHT), ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#344233")),
    ("BACKGROUND", (0, 1), (-1, 1), CARD), ("BACKGROUND", (0, 3), (-1, 3), PALE_GRAY),
    ("GRID", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
]))
story += [architecture, Spacer(1, 7 * mm), P("Transaction flow", "H2X")] + bullets([
    "The page retrieves the ABI, contract address, chain ID, deployment block, and explorer base URL from the Flask config endpoint.",
    "The user connects MetaMask. The application verifies chain ID 11155111 before enabling state changing actions.",
    "Flask validates goal and deposit form data before JavaScript builds the contract call.",
    "MetaMask presents the transaction. The user approves it without exposing the private key to Flask or Render.",
    "After confirmation, the page reloads goal state and contract events from the deployment block.",
    "Each activity row links to Sepolia Etherscan for independent verification.",
]) + [
    Spacer(1, 3 * mm), P("Backend responsibilities", "H2X"),
    data_table([
        ["Endpoint", "Purpose", "Security behavior"],
        ["/health", "Render service monitoring", "Returns status only"],
        ["/api/config", "ABI and public chain configuration", "No private key or secret is returned"],
        ["/api/validate/goal", "Name, target, and deadline checks", "Rejects blank, zero, excessive, or past values"],
        ["/api/validate/deposit", "ETH decimal validation", "Rejects zero and more than 18 decimals"],
        ["/api/transaction/<hash>", "Optional receipt lookup", "Validates the hash and handles missing RPC safely"],
    ], [44 * mm, 58 * mm, 61 * mm], small=True),
    Spacer(1, 5 * mm),
    P("No database is required because ownership, amounts, status, and history already exist on-chain. Avoiding a second writable store prevents conflicts between a local database and the smart contract."),
    PageBreak(),
]

# Page 4
story += section_title("03", "Smart contract design", "Savings rules enforced in Solidity", "GoalSave.sol is a single contract with no external imports. It uses actual msg.value deposits, explicit lifecycle states, custom errors, and event records. The optimized deployed bytecode is 4,040 bytes.")
story += [
    data_table([
        ["Function", "Who or value", "Effect"],
        ["createGoal", "Any wallet, no ETH", "Validates name, target, deadline; stores a new goal ID"],
        ["deposit", "Any wallet, msg.value > 0", "Adds the received ETH to one active goal"],
        ["withdraw", "Goal owner only", "Unlocks after target or deadline; closes as Withdrawn"],
        ["emergencyWithdraw", "Goal owner only", "Returns the current balance; closes as EmergencyClosed"],
        ["getGoal", "Read only", "Returns the stored goal structure"],
        ["getGoalIds", "Read only", "Returns all goal IDs created by an owner"],
    ], [40 * mm, 50 * mm, 73 * mm]),
    Spacer(1, 7 * mm), P("Lifecycle", "H2X"),
    data_table([
        ["State", "Entry condition", "Available next actions"],
        ["Active", "Goal created", "Deposit, unlocked withdrawal, or emergency close"],
        ["Withdrawn", "Normal withdrawal succeeds", "Read only terminal state"],
        ["EmergencyClosed", "Early close succeeds", "Read only terminal state"],
    ], [42 * mm, 60 * mm, 61 * mm]),
    Spacer(1, 7 * mm), P("Security and correctness decisions", "H2X"),
] + bullets([
    "Authorization compares msg.sender with the stored owner on both withdrawal paths.",
    "The contract changes savedAmount and status before transferring ETH, following checks effects interactions.",
    "A re-entrancy guard prevents a second payout from entering during an external transfer.",
    "Direct receive and fallback transfers revert, so every accepted ETH deposit is linked to a goal ID.",
    "Normal withdrawal requires savedAmount to reach targetAmount or block.timestamp to reach the deadline.",
    "Normal withdrawal and emergency close emit different events, preserving their meaning in the history.",
]) + [
    Spacer(1, 4 * mm), P("ETH accounting", "H2X"),
    P("The deposit function records msg.value, which is the amount the contract actually receives. It does not trust a separate amount supplied by the browser. This prevents the interface value from disagreeing with the on-chain balance."),
    P("The browser disables Withdraw while the goal is locked, but the Solidity condition remains the authoritative control if a caller bypasses the interface."),
    PageBreak(),
]

# Page 5
story += section_title("04", "Application design", "Interface and backend implementation", "The interface keeps the connected wallet and Sepolia network visible, then presents savings progress and the event trail in one page. Every state changing action provides pending, confirmed, or error feedback.")
mobile_figure = figure(SHOTS / "00-local-mobile.png", 32, "Responsive mobile layout", 65)
ui_table = data_table([
    ["Interface area", "Implementation"],
    ["Header", "Wallet connection, shortened account, Sepolia status"],
    ["Dashboard", "Total saved, active goals, ready goals, wallet balance"],
    ["Goal cards", "Name, balance, target, progress, deadline, lifecycle status"],
    ["Actions", "Create, deposit, conditional withdraw, emergency close"],
    ["Activity", "Contract events with amounts and Etherscan transaction links"],
    ["Feedback", "Validation messages, rejected signature, wrong network, RPC and contract errors"],
], [42 * mm, 78 * mm], small=True)
application_layout = Table([[ui_table, mobile_figure]], colWidths=[123 * mm, 40 * mm], hAlign="LEFT")
application_layout.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0),
    ("RIGHTPADDING", (0, 0), (0, 0), 3 * mm), ("LEFTPADDING", (1, 0), (1, 0), 3 * mm),
    ("RIGHTPADDING", (1, 0), (1, 0), 0),
]))
story += [
    application_layout, Spacer(1, 4 * mm), P("Implementation files", "H2X"),
    data_table([
        ["Required item", "Submitted file", "Purpose"],
        ["Solidity", "contracts/GoalSave.sol", "Contract rules and events"],
        ["ABI", "abi/GoalSave.json", "JavaScript contract interface"],
        ["Python Flask", "app.py", "Web service, validation, public config"],
        ["HTML", "templates/index.html", "Page structure and forms"],
        ["CSS", "static/styles.css", "Responsive visual design"],
        ["JavaScript", "static/app.js", "MetaMask, Ethers.js, UI state"],
        ["Render", "render.yaml and Procfile", "Deployment and Gunicorn startup"],
        ["Deployment", "deployment.json", "Sepolia address, block, transaction hash"],
    ], [35 * mm, 55 * mm, 73 * mm], small=True),
    Spacer(1, 3 * mm), P("Error handling", "H2X"),
] + bullets([
    "The form rejects blank names, non-positive targets, expired deadlines, zero deposits, and excess decimal precision.",
    "The page detects missing MetaMask, incorrect networks, cancelled signatures, insufficient funds, and contract reverts. Render receives only public configuration; the seed phrase and private key never enter the repository or backend.",
]) + [PageBreak()]

# Page 6
story += section_title("05", "Testing and results", "Automated checks and live Sepolia transactions", "The final code passed eight smart contract tests and six Flask tests. JavaScript syntax validation also passed. The live demonstration then verified the complete user flow against the deployed Sepolia contract.")
story += [
    data_table([
        ["Layer", "Result", "Coverage"],
        ["Smart contract", "8 of 8 passed", "Creation, deposits, invalid calls, authorization, locks, both withdrawal paths, direct transfer rejection"],
        ["Flask", "6 of 6 passed", "Home, health, config, form validation, transaction hash and RPC fallback"],
        ["JavaScript", "Syntax check passed", "static/app.js parsed successfully"],
        ["Live Render", "Operational", "/health returned ok and /api/config returned the deployed Sepolia configuration"],
    ], [35 * mm, 37 * mm, 91 * mm], small=True),
    Spacer(1, 7 * mm),
    two_figures(figure(SHOTS / "03-create-goal.png", 72, "Goal number 1 created with a 0.002 ETH target", 58), figure(SHOTS / "05-deposit-success.png", 72, "First 0.001 ETH deposit recorded at 50 percent", 58)),
    Spacer(1, 6 * mm), P("Observed manual results", "H2X"),
    data_table([
        ["Step", "Expected behavior", "Observed result"],
        ["Connect wallet", "MetaMask account on Sepolia", "Wallet and Sepolia indicator shown"],
        ["Create goal", "New goal and GoalCreated event", "Goal 1 confirmed with target 0.002 ETH"],
        ["First deposit", "Balance becomes 0.001 ETH", "Progress became 50 percent and event appeared"],
        ["Early withdrawal", "Normal withdrawal unavailable", "Withdraw button remained disabled at 50 percent"],
        ["Second deposit", "Target reached", "Balance became 0.002 ETH and Withdraw enabled"],
        ["Withdraw", "Owner receives full saved amount", "Status became Withdrawn and balance became 0"],
    ], [32 * mm, 64 * mm, 67 * mm], small=True),
    Spacer(1, 5 * mm),
    P("Invalid input and unauthorized transaction paths were verified by automated tests. The final report does not claim separate browser screenshots for scenarios that were not manually captured."),
    PageBreak(),
]

# Page 7
story += section_title("06", "End to end evidence", "Target reached and withdrawal confirmed", "The second deposit raised the saved amount to the 0.002 ETH target. GoalSave then enabled normal withdrawal, returned the full balance, and recorded the terminal state and event on-chain.")
story += [
    two_figures(figure(SHOTS / "06-target-reached.png", 50, "Target reached at 100 percent and Withdraw enabled", 54), figure(SHOTS / "08-withdraw-success.png", 88, "Goal status changed to Withdrawn and the activity log recorded 0.002 ETH", 54), left_width=59, right_width=104),
    Spacer(1, 4 * mm),
    figure(SHOTS / "09-etherscan-withdrawal.png", 88, "Sepolia Etherscan receipt showing Success and the 0.002 ETH transfer from GoalSave to the wallet", 60),
    Spacer(1, 3 * mm),
    data_table([
        ["Withdrawal evidence", "Value"],
        ["Transaction", WITHDRAWAL_TX],
        ["Block", "11941002"],
        ["Recipient wallet", WALLET_ADDRESS],
        ["Amount returned", "0.002 Sepolia ETH"],
        ["Status", "Success"],
    ], [45 * mm, 118 * mm], small=True),
    PageBreak(),
]

# Page 8
story += section_title("07", "Deployment and evaluation", "Public submission record and evaluation", "The same source repository supplies the contract, ABI, Flask application, frontend files, tests, Render blueprint, and deployment record. The web service and contract are separate deployments linked through public configuration.")
deployment_figure = figure(SHOTS / "00-etherscan-deployment.png", 52, "Contract creation on Sepolia block 11939866", 38)
deployment_table = data_table([
    ["Record", "Final value"],
    ["Student", f"{STUDENT_NAME}  {STUDENT_ID}"],
    ["GitHub", GITHUB_URL],
    ["Render", RENDER_URL],
    ["Contract", CONTRACT_ADDRESS],
    ["Deployment block", DEPLOYMENT_BLOCK],
    ["Deployment transaction", DEPLOYMENT_TX],
], [30 * mm, 72 * mm], small=True)
deployment_layout = Table([[deployment_table, deployment_figure]], colWidths=[105 * mm, 58 * mm], hAlign="LEFT")
deployment_layout.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0),
    ("RIGHTPADDING", (0, 0), (0, 0), 3 * mm), ("LEFTPADDING", (1, 0), (1, 0), 3 * mm),
    ("RIGHTPADDING", (1, 0), (1, 0), 0),
]))
story += [
    deployment_layout, Spacer(1, 4 * mm),
    P("Challenges encountered", "H2X"),
    P("Deployment required the Remix artifact, Sepolia address and block, Render variables, Flask configuration, and browser ABI to stay consistent. I stored the public values in deployment.json and exposed them through Flask. The interface also disables normal withdrawal while a goal is locked, while Solidity repeats the rule for callers that bypass the page."),
    P("Limitations", "H2X"),
    P("GoalSave is an unaudited testnet application. It supports native ETH only, relies on MetaMask and a Sepolia RPC, and scans events from the deployment block. A production history would require indexed event storage."),
    P("Future improvements", "H2X"),
    P("Future work would verify source code on Etherscan, add indexed history, support ERC 20 goals, improve contributor labels, and include accessibility and independent security testing."),
    P("Conclusion", "H2X"),
    P("GoalSave satisfies the SC6113 individual assignment requirements with an original financial use case and a complete deployed stack. Solidity enforces ownership and withdrawal rules, Flask provides validation and public configuration, and Sepolia records the full flow from goal creation through withdrawal."),
    Spacer(1, 2 * mm), P("References", "H2X"),
    P("[1] SC6113 Individual Assignment brief supplied by the module teaching team.<br/>[2] Solidity documentation  https://docs.soliditylang.org/<br/>[3] MetaMask Wallet documentation  https://docs.metamask.io/wallet/<br/>[4] Sepolia Etherscan contract record  https://sepolia.etherscan.io/address/" + CONTRACT_ADDRESS, "SmallX"),
]

doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
shutil.copy2(OUTPUT, REPO_COPY)
print(OUTPUT)
print(REPO_COPY)
