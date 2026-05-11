"""
app/data/policies.py

Simulated policy/FAQ data for the Banking AI-Agents system.
In a production system this would be backed by a database or vector store;
here we use a plain Python dictionary keyed by intent label.
"""

from typing import Dict

# ---------------------------------------------------------------------------
# Structure: intent_label -> {"title": str, "body": str}
# ---------------------------------------------------------------------------

POLICIES: Dict[str, Dict[str, str]] = {
    # ── Account & Card ──────────────────────────────────────────────────────
    "card_not_received": {
        "title": "Replacement / New Card Delivery Policy",
        "body": (
            "New and replacement debit/credit cards are dispatched within 5-7 business days "
            "after the request is processed. Customers may track shipment via the mobile app "
            "under 'My Cards → Track Delivery'. If the card has not arrived within 10 business "
            "days, a replacement can be issued free of charge by contacting customer support "
            "or visiting the nearest branch. Customers should verify their registered mailing "
            "address before requesting a replacement."
        ),
    },
    "card_blocked": {
        "title": "Unblocking a Blocked Debit / Credit Card",
        "body": (
            "Cards are automatically blocked after three consecutive incorrect PIN attempts, "
            "after suspected fraudulent activity, or upon the customer's explicit request. "
            "To unblock, the customer must authenticate via the mobile app (Biometric or OTP) "
            "or visit a branch with a valid government-issued ID. Temporary card suspension "
            "can also be managed in-app under 'My Cards → Card Controls'. If the block was "
            "triggered by fraud detection, a specialist review is required before re-enabling."
        ),
    },
    "account_blocked": {
        "title": "Account Suspension and Reactivation Policy",
        "body": (
            "An account may be suspended due to regulatory compliance checks, suspected fraud, "
            "multiple failed login attempts, or court orders. The customer will receive an SMS "
            "and email notification stating the reason. To reactivate, the customer should call "
            "the 24/7 helpline (1800-XXX-XXXX) or visit a branch with a valid ID and recent "
            "utility bill. Accounts frozen due to court orders require legal documentation for "
            "reactivation and cannot be resolved over the phone."
        ),
    },
    "lost_or_stolen_card": {
        "title": "Lost or Stolen Card Reporting Policy",
        "body": (
            "Customers should report a lost or stolen card immediately by calling the 24/7 "
            "emergency line (1800-XXX-0000) or via the mobile app ('My Cards → Report Lost/Stolen'). "
            "The card will be blocked instantly. A replacement card will be issued and delivered "
            "within 5-7 business days. Emergency cash advance (up to the daily limit) may be "
            "arranged at a branch with proof of identity. Zero-liability protection applies to "
            "unauthorised transactions reported within 24 hours of discovery."
        ),
    },

    # ── Transfers & Payments ─────────────────────────────────────────────────
    "transfer_failure": {
        "title": "Failed / Pending Transfer Resolution Policy",
        "body": (
            "A transfer may fail due to incorrect beneficiary details, insufficient funds, "
            "daily transfer limits, or a temporary system outage. Deducted funds are "
            "automatically reversed within 1-3 business days if the transfer fails. Customers "
            "can check transfer status in the app under 'Transactions → Transfer History'. "
            "For transfers pending more than 3 business days, submit a dispute through the "
            "app or call customer support with the transaction reference number."
        ),
    },
    "wrong_transfer": {
        "title": "Erroneous / Wrong-Account Transfer Policy",
        "body": (
            "If funds were sent to the wrong account, the customer should immediately contact "
            "support with the transaction reference number, amount, and date. The bank will "
            "initiate a 'Transaction Recall' request with the receiving bank within 24 hours. "
            "Recovery depends on the cooperation of the receiving bank and whether funds are "
            "still available. The process may take 5-15 business days. If the recipient "
            "refuses to return the funds, a formal dispute must be filed and may involve "
            "legal proceedings."
        ),
    },
    "bill_payment_issue": {
        "title": "Bill Payment Failure / Duplicate Payment Policy",
        "body": (
            "Failed bill payments are reversed automatically within 1-2 business days. "
            "Duplicate payments are identified by our system and refunded within 3 business "
            "days; customers will receive a confirmation SMS. To manually report a duplicate, "
            "go to 'Transactions → Bill Payments → Report Issue' in the app and provide the "
            "biller reference number. For payments not reflecting on the biller side, allow "
            "up to 2 business days for clearing before raising a dispute."
        ),
    },

    # ── Loans & Credit ───────────────────────────────────────────────────────
    "loan_inquiry": {
        "title": "Personal / Home Loan Inquiry Policy",
        "body": (
            "Customers can apply for personal loans (up to 10× monthly salary), home loans, "
            "or auto loans online, via the app, or at a branch. Eligibility checks are instant; "
            "full approval typically takes 2-5 business days. Required documents: valid ID, "
            "last 3 months' payslips or tax returns, and bank statements. Interest rates are "
            "fixed or floating; the applicable rate is shown in the pre-approval letter. "
            "Early repayment is allowed with a 1% prepayment fee."
        ),
    },
    "loan_repayment_issue": {
        "title": "Loan Repayment Failure / Overdue Policy",
        "body": (
            "If an EMI (monthly installment) fails due to insufficient balance, the system "
            "retries after 3 business days. A late-payment fee of 2% of the overdue amount "
            "applies after a 5-day grace period. Customers facing financial difficulty should "
            "contact the Loan Restructuring team at least 5 days before the due date to "
            "explore options such as payment deferral, restructuring, or moratorium. "
            "Failure to pay for 3 consecutive months triggers a Non-Performing Asset (NPA) "
            "classification affecting the customer's credit score."
        ),
    },

    # ── Deposits & Savings ───────────────────────────────────────────────────
    "deposit_issue": {
        "title": "Cash / Cheque Deposit Not Credited Policy",
        "body": (
            "Cash deposits at ATMs and branches are credited within the same business day if "
            "made before 4 PM. After-hours deposits are processed the next business day. "
            "Cheque deposits are subject to a 2-3 business day clearing period. If the amount "
            "is not credited within the expected timeframe, customers should retain the "
            "deposit slip and contact support with the slip number and deposit details. "
            "Disputed ATM deposits require a machine audit and may take up to 7 business days."
        ),
    },
    "interest_rate_inquiry": {
        "title": "Savings / Fixed Deposit Interest Rate Information",
        "body": (
            "Current interest rates for savings accounts range from 2.5% to 4.5% p.a. "
            "depending on account type. Fixed Deposit (FD) rates range from 5.0% to 7.5% "
            "for tenures of 7 days to 10 years. Senior citizens receive an additional 0.25% "
            "p.a. on FDs. Rates are subject to change as per RBI / central bank guidelines. "
            "The latest rates are always available in the app under 'Products → Interest Rates'. "
            "Premature FD withdrawal incurs a 0.5% penalty on the applicable rate."
        ),
    },

    # ── Online / Digital Banking ─────────────────────────────────────────────
    "login_issue": {
        "title": "Internet / Mobile Banking Login Problem Policy",
        "body": (
            "Common login issues include forgotten passwords, expired OTPs, and device/browser "
            "incompatibility. To reset a password, use 'Forgot Password' on the login page; "
            "an OTP will be sent to the registered mobile number. If the account is locked "
            "after 5 failed attempts, it auto-unlocks after 30 minutes or can be unlocked "
            "immediately by calling the helpline. Customers are advised to keep their app "
            "updated and clear the browser cache if issues persist. 2FA is mandatory for "
            "all fund-transfer operations."
        ),
    },
    "fraud_report": {
        "title": "Fraud and Unauthorised Transaction Reporting Policy",
        "body": (
            "If a customer notices an unauthorised transaction, they should immediately: "
            "(1) Block the card via the app or helpline. "
            "(2) Report the transaction through 'Transactions → Report Fraud' in the app "
            "or call the 24/7 fraud hotline (1800-XXX-1111). "
            "(3) File a complaint with local law enforcement and share the FIR number with us. "
            "The bank will initiate a chargeback within 3 business days and provisionally "
            "credit the disputed amount pending investigation. Zero-liability applies if the "
            "fraud was not due to customer negligence."
        ),
    },
    "otp_issue": {
        "title": "OTP Not Received / Expired OTP Policy",
        "body": (
            "OTPs are valid for 5 minutes and sent to the registered mobile number. "
            "If not received: (1) Check for network coverage. (2) Ensure the registered "
            "number is active and not on DND for transactional messages. (3) Use 'Resend OTP' "
            "after 60 seconds. If the problem persists, request an OTP via email as a fallback "
            "(for supported operations). Update the registered mobile number at any branch "
            "with a valid ID. For urgent transactions, visit a branch for assisted service."
        ),
    },

    # ── General ──────────────────────────────────────────────────────────────
    "kyc_update": {
        "title": "KYC Document Update Policy",
        "body": (
            "Customers must periodically update KYC (Know Your Customer) documents as per "
            "regulatory requirements. Accepted ID proofs: Passport, National ID, Driver's License. "
            "Address proofs: utility bill, bank statement (not more than 3 months old), lease "
            "agreement. Documents can be uploaded via the app ('Profile → KYC Update') or "
            "submitted at a branch. Digital KYC (Video KYC) is available for eligible customers. "
            "Failure to complete KYC may result in temporary account restrictions."
        ),
    },
    "refund_request": {
        "title": "Refund Processing Policy",
        "body": (
            "Refunds for failed transactions, duplicate charges, or merchant disputes are "
            "processed within 5-7 business days after verification. Merchant refunds depend "
            "on the merchant's refund policy and typically take 7-14 business days. Customers "
            "can track refund status in the app under 'Transactions → Refund Tracker'. "
            "If a refund is overdue, raise a dispute through the app with the original "
            "transaction reference and a brief description of the issue."
        ),
    },
    "general_inquiry": {
        "title": "General Customer Inquiry",
        "body": (
            "For general inquiries, customers can reach support via: "
            "(1) In-app chat (24/7 AI-assisted, human handoff available). "
            "(2) Phone: 1800-XXX-XXXX (24/7, toll-free). "
            "(3) Email: support@ourbank.com (response within 1 business day). "
            "(4) Branch visit during working hours (Mon–Sat, 9 AM–5 PM). "
            "Self-service options are available in the app for account statements, "
            "mini-statements, interest certificates, and tax documents."
        ),
    },
}


def get_policy(intent: str) -> Dict[str, str]:
    """
    Retrieve the policy entry for a given intent.
    Falls back to 'general_inquiry' if the intent is not found.
    """
    return POLICIES.get(intent, POLICIES["general_inquiry"])


def list_supported_intents() -> list[str]:
    """Return all intent labels that have an explicit policy entry."""
    return list(POLICIES.keys())
