from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# Edit these values after deployment, then run:
#   python docs/report_source.py
STUDENT_NAME = "[STUDENT NAME]"
STUDENT_ID = "[STUDENT ID]"
GITHUB_URL = "https://github.com/hehu6/GoalSave-SC6113-Individual-Assignment"
RENDER_URL = "[ADD URL]"
CONTRACT_ADDRESS = "0x80c18baaf6102a26f5fedd337ef33ff1576c69fd"

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "GoalSave_SC6113_Report.pdf"
HERO = ROOT / "docs" / "screenshots" / "00-local-hero.png"
MOBILE = ROOT / "docs" / "screenshots" / "00-local-mobile.png"

PAGE_W, PAGE_H = A4
INK = colors.HexColor("#111510")
MUTED = colors.HexColor("#62675E")
PAPER = colors.HexColor("#F5F3EC")
CARD = colors.HexColor("#FFFDF7")
LINE = colors.HexColor("#D9D7CC")
LIME = colors.HexColor("#C9F23D")
GREEN = colors.HexColor("#729009")
NIGHT = colors.HexColor("#182018")
ORANGE = colors.HexColor("#F3A266")


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverKicker", fontName="Courier-Bold", fontSize=8.5, leading=11,
    textColor=GREEN, spaceAfter=11, tracking=1.2,
))
styles.add(ParagraphStyle(
    name="CoverTitle", fontName="Helvetica-Bold", fontSize=39, leading=41,
    textColor=INK, spaceAfter=15,
))
styles.add(ParagraphStyle(
    name="CoverSub", fontName="Helvetica", fontSize=13.5, leading=20,
    textColor=MUTED, spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="H1x", fontName="Helvetica-Bold", fontSize=23, leading=27,
    textColor=INK, spaceAfter=13,
))
styles.add(ParagraphStyle(
    name="H2x", fontName="Helvetica-Bold", fontSize=13.5, leading=17,
    textColor=INK, spaceBefore=6, spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="Bodyx", fontName="Helvetica", fontSize=9.2, leading=14,
    textColor=colors.HexColor("#343830"), spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="Smallx", fontName="Helvetica", fontSize=7.8, leading=11,
    textColor=MUTED, spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="Mono", fontName="Courier", fontSize=7.7, leading=11,
    textColor=colors.HexColor("#283025"), spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="Callout", fontName="Helvetica-Bold", fontSize=9.2, leading=13,
    textColor=INK, spaceAfter=0,
))
styles.add(ParagraphStyle(
    name="TableHead", fontName="Helvetica-Bold", fontSize=7.4, leading=9,
    textColor=colors.white,
))
styles.add(ParagraphStyle(
    name="TableCell", fontName="Helvetica", fontSize=7.2, leading=10,
    textColor=INK,
))
styles.add(ParagraphStyle(
    name="TableCellSmall", fontName="Helvetica", fontSize=6.7, leading=8.7,
    textColor=INK,
))
styles.add(ParagraphStyle(
    name="CenterSmall", fontName="Helvetica", fontSize=7.4, leading=10,
    alignment=TA_CENTER, textColor=MUTED,
))


def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullets(items):
    return [P(f"<font color='#729009'><b>-</b></font>&nbsp;&nbsp;{item}") for item in items]


def callout(title, body, color=LIME):
    data = [[P(title, "Callout"), P(body, "Smallx")]]
    table = Table(data, colWidths=[42 * mm, 121 * mm], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), color),
        ("BACKGROUND", (1, 0), (1, 0), CARD),
        ("BOX", (0, 0), (-1, -1), .6, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def data_table(rows, widths, small=False):
    head = [P(str(cell), "TableHead") for cell in rows[0]]
    body_style = "TableCellSmall" if small else "TableCell"
    body = [[P(str(cell), body_style) for cell in row] for row in rows[1:]]
    table = Table([head] + body, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NIGHT),
        ("BACKGROUND", (0, 1), (-1, -1), CARD),
        ("GRID", (0, 0), (-1, -1), .45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ]))
    return table


def page_title(number, kicker, title, intro=None):
    items = [P(f"{number} / {kicker.upper()}", "CoverKicker"), P(title, "H1x")]
    if intro:
        items.append(P(intro))
    items.append(Spacer(1, 3 * mm))
    return items


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    if doc.page == 1:
        canvas.setFillColor(colors.HexColor("#EAF5B5"))
        canvas.circle(PAGE_W - 20 * mm, PAGE_H - 16 * mm, 52 * mm, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor("#F8DEC9"))
        canvas.circle(-7 * mm, 20 * mm, 37 * mm, stroke=0, fill=1)
    else:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(.5)
        canvas.line(22 * mm, PAGE_H - 18 * mm, PAGE_W - 22 * mm, PAGE_H - 18 * mm)
        canvas.setFont("Helvetica-Bold", 7.3)
        canvas.setFillColor(INK)
        canvas.drawString(22 * mm, PAGE_H - 14 * mm, "GOALSAVE / SC6113 INDIVIDUAL ASSIGNMENT")
        canvas.setFont("Courier", 7)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - 22 * mm, 12 * mm, f"{doc.page:02d} / 08")
        canvas.drawString(22 * mm, 12 * mm, "DRAFT - replace highlighted account-dependent evidence")
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4,
    leftMargin=22 * mm, rightMargin=22 * mm,
    topMargin=25 * mm, bottomMargin=20 * mm,
    title="GoalSave - SC6113 Individual Assignment",
    author="[Student Name]",
)

story = []

# Page 1 - Cover
story += [
    Spacer(1, 27 * mm),
    P("SC6113 / BLOCKCHAIN APPLICATIONS", "CoverKicker"),
    P("GoalSave", "CoverTitle"),
    P("A transparent, goal-based savings DApp on Ethereum Sepolia", "CoverSub"),
    Spacer(1, 5 * mm),
    callout("SUBMISSION STATUS", "Code and local tests complete. Replace the highlighted identity, URL, contract-address, and Sepolia screenshot fields before submission.", ORANGE),
    Spacer(1, 19 * mm),
    data_table([
        ["Student", "Module", "Submission"],
        [f"{STUDENT_NAME}\n{STUDENT_ID}", "SC6113", "Individual Assignment"],
        ["GitHub", "Render", "Sepolia contract"],
        [GITHUB_URL, RENDER_URL, CONTRACT_ADDRESS],
    ], [54 * mm, 54 * mm, 55 * mm]),
    Spacer(1, 19 * mm),
    P("PROJECT POSITIONING", "CoverKicker"),
    P("GoalSave follows the taught Flask + MetaMask + Solidity workflow while implementing an original financial use case, real ETH accounting, authorization, event history, automated testing, and deployment-ready configuration.", "CoverSub"),
    Spacer(1, 7 * mm),
    HRFlowable(width="100%", thickness=1, color=INK),
    Spacer(1, 5 * mm),
    P("Prepared: 18 October 2026  |  Network: Sepolia (chain ID 11155111)  |  Educational use only", "Smallx"),
    PageBreak(),
]

# Page 2 - Baseline and originality
story += page_title("01", "Course baseline", "What came from class - and what is original",
    "The lecturer did not rely only on slides; the public examples and the progression of student repositories show a practical, copy-and-adapt teaching workflow. The correct baseline is therefore the stack and interaction pattern, not the submission completeness of one classroom repository.")
story += [
    P("Evidence from the lecturer and Congxiang repository", "H2x"),
    data_table([
        ["Evidence", "Observed content", "Interpretation"],
        ["Lecturer SC6113 Gist (5 Aug 2026)", "paynow contract stores payer, payee, and amount; transaction() reads them.", "A first state-write/state-read exercise. It does not transfer ETH."],
        ["Congxiang - 16 Sep", "Flask pages and Web3 transfer UI using weixin/check_transaction.", "Strongly resembles a guided classroom increment."],
        ["Congxiang - 23 Sep", "Deposit page using deposit_money/deposit_view.", "Second guided interaction pattern."],
        ["Congxiang - 30 Sep / 7 Oct", "Contract folder, then SQLite history added to a ChatGPT example.", "A class exercise trail, not a polished final deliverable."],
    ], [37 * mm, 67 * mm, 59 * mm], small=True),
    Spacer(1, 5 * mm),
    callout("CONCLUSION", "It is plausible that Congxiang's project follows the lecturer's live coding. However, it lacks a matched final contract/ABI set, systematic tests, deployment evidence, and a complete report, so submitting it unchanged would not safely satisfy the individual rubric."),
    Spacer(1, 6 * mm),
    P("How GoalSave stays within the taught scope", "H2x"),
] + bullets([
    "Same approachable stack: one Solidity contract, MetaMask, Ethers.js, Flask, HTML, CSS, JavaScript, GitHub, and Render.",
    "Different business logic: personal savings targets instead of PayNow record storage, crowdfunding, or freelance escrow.",
    "One contract is appropriate for the individual assignment; group-project expectations such as three interacting contracts and multiple organizational roles are intentionally excluded.",
    "No source file from a classmate repository is included. The lecturer's public Gist is cited as a learning reference only.",
]) + [PageBreak()]

# Page 3 - Problem and objectives
story += page_title("02", "Problem and objectives", "A savings commitment users can verify",
    "People often track savings goals in spreadsheets or banking notes. Those records are easy to change and do not give contributors a shared, independently verifiable history. GoalSave uses a smart contract to make the goal rules and transaction trail explicit.")
story += [
    P("Objectives", "H2x"),
] + bullets([
    "Let a wallet create multiple named goals with a target amount and future deadline.",
    "Accept real Sepolia ETH deposits and update progress from on-chain state.",
    "Allow normal withdrawal only after reaching the target or passing the deadline.",
    "Provide an explicit emergency close path without hiding it in normal history.",
    "Show transaction feedback, goal status, and Etherscan links in a responsive interface.",
    "Validate input and handle wrong network, missing wallet, rejected transactions, and RPC failures.",
])
story += [
    Spacer(1, 3 * mm),
    P("Requirements coverage", "H2x"),
    data_table([
        ["Assignment requirement", "GoalSave implementation", "Evidence"],
        ["Original financial DApp", "Goal-based test-ETH savings with target/deadline rules", "GoalSave.sol; UI"],
        ["Solidity + ABI", "Compiled 0.8.30 contract; generated standalone ABI", "contracts/; abi/"],
        ["MetaMask transactions", "BrowserProvider signs create, deposit, and withdrawal calls", "static/app.js"],
        ["Flask backend", "Pages, config/ABI API, validation, optional receipt lookup", "app.py"],
        ["HTML/CSS/JS", "Responsive dashboard and event history", "templates/; static/"],
        ["Status/history", "Events queried from deployment block; Etherscan deep links", "5 event types"],
        ["Validation/errors", "Backend, browser, and contract checks", "14 automated tests"],
        ["Render readiness", "Blueprint, Gunicorn, health endpoint", "render.yaml; Procfile"],
    ], [49 * mm, 78 * mm, 36 * mm], small=True),
    Spacer(1, 6 * mm),
    callout("SUCCESS CRITERION", "A student can demonstrate create -> deposit -> locked withdrawal -> target reached -> successful withdrawal, with every successful state change visible both in the DApp and on Sepolia Etherscan."),
    PageBreak(),
]

# Page 4 - Architecture
story += page_title("03", "System design", "Wallet-first architecture with a thin backend",
    "The blockchain is the source of truth. Flask serves the interface and performs supporting validation, while MetaMask keeps transaction signing under the user's control.")

arch = Table([
    [P("BROWSER", "TableHead"), P("METAMASK", "TableHead"), P("SEPOLIA", "TableHead")],
    [P("HTML/CSS dashboard<br/>Ethers.js contract client<br/>Event history", "TableCell"),
     P("Account selection<br/>Network switch<br/>Transaction signature", "TableCell"),
     P("GoalSave contract<br/>ETH custody<br/>Immutable event log", "TableCell")],
    [P("FLASK / RENDER", "TableHead"), P("JSON ENDPOINTS", "TableHead"), P("OPTIONAL RPC", "TableHead")],
    [P("Template/static hosting<br/>Gunicorn health check", "TableCell"),
     P("ABI/config<br/>Goal/deposit validation", "TableCell"),
     P("Receipt status lookup<br/>No private key stored", "TableCell")],
], colWidths=[54.3 * mm] * 3)
arch.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NIGHT),
    ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#334033")),
    ("BACKGROUND", (0, 1), (-1, 1), CARD),
    ("BACKGROUND", (0, 3), (-1, 3), CARD),
    ("GRID", (0, 0), (-1, -1), .6, LINE),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 9),
    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ("TOPPADDING", (0, 0), (-1, -1), 9),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
]))
story += [arch, Spacer(1, 7 * mm), P("Primary transaction flow", "H2x")]
story += bullets([
    "The page downloads the ABI and chain configuration from /api/config.",
    "The user connects MetaMask; the app verifies Sepolia chain ID 11155111.",
    "Flask validates form input before the browser constructs a contract call.",
    "MetaMask displays the exact transaction and the user signs it.",
    "After confirmation, the UI reloads contract state and queries events from the deployment block.",
    "The user can open the same transaction on Sepolia Etherscan for independent verification.",
])
story += [Spacer(1, 4 * mm), P("Why no database?", "H2x"), P("A database is optional in the individual brief. Goal ownership, saved amounts, status, and action history already exist on-chain. Avoiding a second writable data store prevents inconsistencies between SQLite and the contract. The backend remains meaningful through input validation, secure configuration delivery, health monitoring, and optional receipt verification."), PageBreak()]

# Page 5 - Contract design
story += page_title("04", "Smart contract", "Rules enforced in Solidity",
    "GoalSave.sol is a self-contained contract with no external imports. The compiled deployed bytecode is 4,040 bytes with the optimizer enabled and the Paris EVM target, which remains comfortably below the EIP-170 limit.")
story += [
    data_table([
        ["Function", "Authorization / value", "Effect"],
        ["createGoal", "Any wallet; no ETH", "Validates name, target, and future deadline; assigns goal ID."],
        ["deposit", "Any wallet; msg.value > 0", "Adds ETH to one active goal; emits contributor and balance."],
        ["withdraw", "Goal owner only", "Unlocks after target or deadline; closes as Withdrawn."],
        ["emergencyWithdraw", "Goal owner only", "Returns current savings; closes as EmergencyClosed."],
        ["getGoal / getGoalIds", "Read-only", "Supports dashboard state without gas."],
    ], [40 * mm, 52 * mm, 71 * mm]),
    Spacer(1, 6 * mm),
    P("Security decisions", "H2x"),
] + bullets([
    "Authorization: both withdrawal paths compare msg.sender with the stored owner.",
    "Checks-effects-interactions: savedAmount and status change before the external ETH call.",
    "Re-entrancy guard: a second withdrawal cannot enter while a payout is executing.",
    "Accounting integrity: direct receive/fallback transfers revert, so ETH cannot bypass a goal ID.",
    "Custom errors: smaller bytecode and clearer failure categories than repeated strings.",
    "Event separation: normal withdrawal and emergency close are distinguishable in the audit trail.",
])
story += [
    Spacer(1, 3 * mm),
    callout("IMPORTANT DESIGN CHOICE", "The contract uses msg.value as the deposited amount. This is safer than trusting a user-supplied amount parameter, which may not match the ETH actually sent."),
    Spacer(1, 6 * mm),
    P("Goal lifecycle", "H2x"),
    data_table([
        ["State", "Entry", "Allowed next actions"],
        ["Active", "Goal created", "Deposit; normal withdraw if unlocked; emergency close"],
        ["Withdrawn", "Normal withdrawal confirmed", "Read-only; no further deposits or withdrawals"],
        ["EmergencyClosed", "Early close confirmed", "Read-only; no further deposits or withdrawals"],
    ], [41 * mm, 61 * mm, 61 * mm]),
    PageBreak(),
]

# Page 6 - Application
story += page_title("05", "Application implementation", "A complete DApp, not only a contract",
    "The interface is designed as a small financial dashboard rather than a classroom form. It keeps wallet/network state visible and gives users clear pending, confirmed, and error feedback.")

hero = Image(str(HERO), width=109 * mm, height=68.1 * mm)
mobile = Image(str(MOBILE), width=35.1 * mm, height=76 * mm)
shots = Table([
    [hero, mobile],
    [P("Desktop local preview", "CenterSmall"), P("Mobile local preview", "CenterSmall")],
], colWidths=[119 * mm, 44 * mm], hAlign="LEFT")
shots.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOX", (0, 0), (0, 0), .6, LINE),
    ("BOX", (1, 0), (1, 0), .6, LINE),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story += [shots, Spacer(1, 5 * mm), P("Implementation highlights", "H2x")]
story += bullets([
    "Dashboard totals are calculated from contract state rather than hard-coded examples.",
    "Goal cards show saved amount, target, progress, deadline, status, and context-aware actions.",
    "Five event filters produce an on-chain activity table with Etherscan links.",
    "The JavaScript handles missing MetaMask, network switching, cancelled signatures, insufficient funds, and contract errors.",
    "Responsive breakpoints support laptop and mobile widths; reduced-motion preferences are respected.",
    "The Flask API normalizes decimals, limits names by UTF-8 bytes, validates deadlines, and rejects malformed transaction hashes.",
])
story += [callout("SCREENSHOT STATUS", "These are local interface previews, not deployment evidence. Replace or supplement them with screenshots showing the real Render URL, connected MetaMask account, confirmed goal, and Sepolia transaction before submission.", ORANGE), PageBreak()]

# Page 7 - Testing
story += page_title("06", "Testing", "Fourteen automated checks passed locally",
    "The contract was compiled with solc 0.8.30 and tested on an isolated in-memory Ganache chain. Flask routes and validation were tested with the Flask test client. No test needed a real private key or test ETH.")
story += [
    callout("LOCAL RESULT", "8 / 8 smart-contract tests passed  |  6 / 6 Flask tests passed  |  JavaScript syntax check passed", LIME),
    Spacer(1, 6 * mm),
    data_table([
        ["ID", "Automated scenario", "Expected and observed result"],
        ["C01", "Create and index goal", "Stored owner/name/target; owner ID list returned - PASS"],
        ["C02", "Third-party contribution", "Goal savedAmount increased by msg.value - PASS"],
        ["C03", "Zero/missing-goal deposit", "Both invalid calls reverted - PASS"],
        ["C04", "Early normal withdrawal", "Reverted before target and deadline - PASS"],
        ["C05", "Target reached withdrawal", "Funds released; state became Withdrawn - PASS"],
        ["C06", "Non-owner withdrawal", "Authorization check reverted - PASS"],
        ["C07", "Emergency close", "Funds returned; distinct terminal state recorded - PASS"],
        ["C08", "Direct ETH transfer", "Receive/fallback rejected unattributed ETH - PASS"],
        ["B01-B02", "Home, health, and config", "HTTP 200; ABI and Sepolia chain returned - PASS"],
        ["B03-B05", "Goal/deposit validation", "Valid normalized; invalid values returned HTTP 400 - PASS"],
        ["B06", "Receipt endpoint", "Hash validated; missing RPC handled gracefully - PASS"],
    ], [19 * mm, 61 * mm, 83 * mm], small=True),
    Spacer(1, 6 * mm),
    P("Required manual Sepolia checks", "H2x"),
    data_table([
        ["Check", "Status before submission"],
        ["Render URL opens and /health returns ok", "TO BE COMPLETED BY STUDENT"],
        ["MetaMask switches to Sepolia and connects", "TO BE COMPLETED BY STUDENT"],
        ["Create/deposit transactions confirmed", "TO BE COMPLETED BY STUDENT"],
        ["Invalid input and locked withdrawal demonstrated", "TO BE COMPLETED BY STUDENT"],
        ["Target reached and normal withdrawal confirmed", "TO BE COMPLETED BY STUDENT"],
        ["Etherscan receipts and post-refresh persistence captured", "TO BE COMPLETED BY STUDENT"],
    ], [94 * mm, 69 * mm], small=True),
    Spacer(1, 4 * mm),
    P("The full reproducible test plan and required screenshot filenames are provided in docs/TEST_PLAN.md.", "Smallx"),
    PageBreak(),
]

# Page 8 - Deployment and conclusion
story += page_title("07", "Deployment and evaluation", "What remains account-dependent",
    "The project includes every source-code and configuration item needed for submission. The final public links and chain evidence cannot be truthfully produced without the student's MetaMask, Sepolia test ETH, GitHub account, and Render account.")
story += [
    P("Final deployment sequence", "H2x"),
    data_table([
        ["Step", "Action", "Record in submission"],
        ["1", "Compile GoalSave.sol in Remix 0.8.30; deploy via MetaMask on Sepolia.", "Address, tx hash, block, screenshot"],
        ["2", "Enter address/block in deployment.json; push project to own GitHub repository.", "GitHub URL and commit"],
        ["3", "Create Render Blueprint; set CONTRACT_ADDRESS, DEPLOYMENT_BLOCK, CHAIN_ID.", "Render URL and /health screenshot"],
        ["4", "Run the manual demonstration using small Sepolia ETH values.", "Create/deposit/withdraw receipts"],
        ["5", "Replace all bracketed fields and TO BE COMPLETED rows in the final report.", "Final 5-8 page PDF"],
    ], [14 * mm, 101 * mm, 48 * mm], small=True),
    Spacer(1, 6 * mm),
    P("Evaluation", "H2x"),
    P("GoalSave meets the individual assignment scope with a single original financial contract and a complete web stack. Its strongest features are correct ETH accounting, clear withdrawal authorization, event-driven history, three-layer validation, responsive transaction feedback, and automated negative testing. The principal limitation is that it is an educational testnet project, not an audited savings product. MetaMask RPC performance and faucet availability may also affect demonstrations."),
    P("Conclusion", "H2x"),
    P("The project advances beyond the lecturer's basic state-storage example without exceeding the course's practical stack. It is sufficiently small to explain during assessment, yet complete enough to demonstrate the full DApp lifecycle from Solidity and ABI through Flask, browser interaction, Sepolia evidence, GitHub, and Render."),
    Spacer(1, 4 * mm),
    callout("FINAL CHECK", "Do not submit this draft until name/ID, GitHub URL, Render URL, contract address, deployment transaction, and real Sepolia screenshots have been added and every placeholder removed.", ORANGE),
    Spacer(1, 6 * mm),
    P("References", "H2x"),
    P("[1] T. T. Teoh, '6113 AY2026 Aug - transferMoney.sol,' GitHub Gist, 5 Aug 2026. https://gist.github.com/teohteiktoe/84327003ab22a8829a681b84e4b3ad19", "Smallx"),
    P("[2] Ethereum Foundation, 'Solidity documentation: Security considerations.' https://docs.soliditylang.org/", "Smallx"),
    P("[3] MetaMask, 'Provider API.' https://docs.metamask.io/wallet/reference/provider-api/", "Smallx"),
    P("[4] Render, 'Deploy a Flask app.' https://render.com/docs/deploy-flask", "Smallx"),
    P("[5] SC6113 Individual Assignment brief supplied by the module teaching team.", "Smallx"),
]

doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
print(OUTPUT)
