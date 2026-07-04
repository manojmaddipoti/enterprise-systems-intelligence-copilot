from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

RAW_DIR = Path("data/raw")
POLICY_DIR = Path("data/policies")
SEED = 20260704

BUSINESS_UNITS = [
    "Corporate Services",
    "Engineering",
    "Finance Operations",
    "Healthcare Operations",
    "IT",
    "Manufacturing",
    "Retail Operations",
    "Supply Chain",
]
REGIONS = ["AMER", "EMEA", "APAC", "LATAM"]
TERMS = ["NET 15", "NET 30", "NET 45", "NET 60"]
TIERS = ["Strategic", "Preferred", "Approved", "Watchlist"]
COMMODITIES = [
    "Software",
    "Professional Services",
    "Facilities",
    "Medical Supplies",
    "Hardware",
    "Logistics",
    "Marketing",
    "Office Supplies",
    "Cloud Services",
    "Maintenance",
]
EXCEPTION_TYPES = [
    "NO_RECEIPT",
    "AMOUNT_VARIANCE",
    "MISSING_APPROVAL",
    "NO_PO_MATCH",
    "SUPPLIER_MISMATCH",
]


def _write_csv(name: str, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(RAW_DIR / f"{name}.csv", index=False)


def _date(days_back: int) -> datetime:
    return datetime.now(UTC) - timedelta(days=days_back)


def _money(low: int, high: int) -> float:
    return round(random.uniform(low, high), 2)


def _tax_id(index: int) -> str:
    return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}-{index:04d}"


def _bank_account() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(12))


def _slightly_dirty_name(name: str, index: int) -> str:
    if index % 9 == 0:
        return name.replace(",", "").replace(" LLC", " Ltd")
    if index % 13 == 0:
        return f"{name} Services"
    if index % 17 == 0:
        return name.upper()
    return name


def generate() -> None:
    random.seed(SEED)
    fake = Faker()
    Faker.seed(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    POLICY_DIR.mkdir(parents=True, exist_ok=True)

    users = []
    for idx in range(1, 251):
        role = random.choices(
            ["APP_ANALYST", "APP_MANAGER", "APP_ADMIN", "APP_AUDITOR"],
            weights=[70, 20, 5, 5],
        )[0]
        users.append(
            {
                "user_id": f"USR-{idx:04d}",
                "full_name": fake.name(),
                "role": role,
                "business_unit": random.choice(BUSINESS_UNITS),
                "personal_email": fake.email(),
                "personal_phone": fake.phone_number(),
            }
        )

    suppliers = []
    oracle_suppliers = []
    oracle_sites = []
    coupa_suppliers = []
    for idx in range(1, 501):
        name = fake.company()
        business_unit = random.choice(BUSINESS_UNITS)
        supplier = {
            "enterprise_supplier_id": f"ENT-SUP-{idx:04d}",
            "base_name": name,
            "region": random.choice(REGIONS),
            "supplier_tier": random.choice(TIERS),
            "payment_terms": random.choice(TERMS),
            "business_unit": business_unit,
            "tax_id": _tax_id(idx),
            "bank_account_number": _bank_account(),
        }
        suppliers.append(supplier)
        if idx <= 470:
            oracle_id = f"ORA-SUP-{idx:04d}"
            oracle_suppliers.append(
                {
                    "oracle_supplier_id": oracle_id,
                    "enterprise_supplier_id": supplier["enterprise_supplier_id"],
                    "supplier_name": name,
                    "region": supplier["region"],
                    "supplier_tier": supplier["supplier_tier"],
                    "payment_terms": supplier["payment_terms"],
                    "business_unit": business_unit,
                    "tax_id": "" if idx % 23 == 0 else supplier["tax_id"],
                    "bank_account_number": supplier["bank_account_number"],
                    "status": "ACTIVE" if idx % 19 else "INACTIVE",
                }
            )
            for site_idx in range(1, 3 if idx <= 330 else 2):
                oracle_sites.append(
                    {
                        "supplier_site_id": f"ORA-SITE-{idx:04d}-{site_idx}",
                        "oracle_supplier_id": oracle_id,
                        "site_name": f"{random.choice(['HQ', 'Remit', 'Purchasing'])} {site_idx}",
                        "country": fake.country_code(),
                        "payment_terms": random.choice(TERMS) if idx % 11 == 0 else supplier["payment_terms"],
                    }
                )
        if idx >= 21:
            coupa_suppliers.append(
                {
                    "coupa_supplier_id": f"COU-SUP-{idx:04d}",
                    "enterprise_supplier_id": supplier["enterprise_supplier_id"],
                    "supplier_name": _slightly_dirty_name(name, idx),
                    "region": supplier["region"],
                    "commodity": random.choice(COMMODITIES),
                    "payment_terms": random.choice(TERMS) if idx % 10 == 0 else supplier["payment_terms"],
                    "tax_id": "" if idx % 29 == 0 else supplier["tax_id"],
                    "status": "ACTIVE",
                }
            )

    commodities = [
        {"commodity_id": f"COM-{idx:03d}", "commodity_name": name, "category": name}
        for idx, name in enumerate(COMMODITIES * 5, start=1)
    ][:50]

    reqs = []
    req_lines = []
    coupa_pos = []
    coupa_po_lines = []
    oracle_pos = []
    oracle_po_lines = []
    oracle_distributions = []
    receipts = []
    coupa_receipts = []
    invoices = []
    invoice_lines = []
    coupa_invoices = []
    payments = []
    approvals = []

    for idx in range(1, 8001):
        supplier = random.choice(suppliers)
        created_at = _date(random.randint(10, 360))
        amount = _money(250, 75000)
        req_id = f"REQ-{idx:05d}"
        reqs.append(
            {
                "requisition_id": req_id,
                "coupa_supplier_id": f"COU-SUP-{int(supplier['enterprise_supplier_id'][-4:]):04d}",
                "requester_id": random.choice(users)["user_id"],
                "business_unit": supplier["business_unit"],
                "commodity": random.choice(COMMODITIES),
                "amount": amount,
                "status": "APPROVED" if idx % 17 else "PENDING",
                "created_at": created_at.isoformat(),
            }
        )
        for line_idx in range(1, 3):
            req_lines.append(
                {
                    "requisition_line_id": f"{req_id}-L{line_idx}",
                    "requisition_id": req_id,
                    "description": fake.bs(),
                    "quantity": random.randint(1, 10),
                    "line_amount": round(amount / 2, 2),
                }
            )

    for idx in range(1, 10001):
        supplier = random.choice(suppliers)
        supplier_num = int(supplier["enterprise_supplier_id"][-4:])
        created_at = _date(random.randint(5, 330))
        approved_at = created_at + timedelta(days=random.randint(0, 18))
        amount = _money(500, 120000)
        po_number = f"PO-{idx:06d}"
        coupa_supplier_id = f"COU-SUP-{supplier_num:04d}"
        oracle_supplier_id = f"ORA-SUP-{supplier_num:04d}"
        status = "APPROVED" if idx % 14 else "PENDING"
        coupa_pos.append(
            {
                "coupa_po_id": f"COU-PO-{idx:06d}",
                "po_number": po_number,
                "coupa_supplier_id": coupa_supplier_id,
                "business_unit": supplier["business_unit"],
                "commodity": random.choice(COMMODITIES),
                "po_amount": amount,
                "status": status,
                "created_at": created_at.isoformat(),
                "approved_at": approved_at.isoformat(),
            }
        )
        for line_idx in range(1, random.randint(2, 4)):
            line_amount = round(amount / 3, 2)
            coupa_po_lines.append(
                {
                    "coupa_po_line_id": f"COU-PO-L-{idx:06d}-{line_idx}",
                    "coupa_po_id": f"COU-PO-{idx:06d}",
                    "po_number": po_number,
                    "line_number": line_idx,
                    "description": fake.catch_phrase(),
                    "line_amount": line_amount,
                }
            )
            if supplier_num <= 470 and idx % 31 != 0:
                oracle_po_lines.append(
                    {
                        "oracle_po_line_id": f"ORA-PO-L-{idx:06d}-{line_idx}",
                        "oracle_po_id": f"ORA-PO-{idx:06d}",
                        "po_number": po_number,
                        "line_number": line_idx,
                        "description": fake.catch_phrase(),
                        "line_amount": line_amount,
                    }
                )
                oracle_distributions.append(
                    {
                        "po_distribution_id": f"PO-DIST-{idx:06d}-{line_idx}",
                        "oracle_po_line_id": f"ORA-PO-L-{idx:06d}-{line_idx}",
                        "gl_code": f"{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                        "business_unit": supplier["business_unit"],
                        "amount": line_amount,
                    }
                )
        if supplier_num <= 470 and idx % 31 != 0:
            oracle_pos.append(
                {
                    "oracle_po_id": f"ORA-PO-{idx:06d}",
                    "po_number": po_number,
                    "oracle_supplier_id": oracle_supplier_id,
                    "business_unit": supplier["business_unit"],
                    "po_amount": amount,
                    "status": status,
                    "created_at": created_at.isoformat(),
                    "approved_at": approved_at.isoformat(),
                }
            )

        approval_chain_id = f"APR-CHAIN-{idx:06d}"
        levels = random.randint(1, 4)
        for level in range(1, levels + 1):
            owner = random.choice(users)
            assigned = created_at + timedelta(hours=level * random.randint(4, 24))
            completed = assigned + timedelta(hours=random.randint(1, 96))
            approvals.append(
                {
                    "approval_event_id": f"APR-{idx:06d}-{level}",
                    "approval_chain_id": approval_chain_id,
                    "document_id": po_number,
                    "business_unit": supplier["business_unit"],
                    "approver_role": "Manager" if level < 3 else "Director",
                    "approver_name": owner["full_name"],
                    "approval_level": level,
                    "status": "PENDING" if idx % 41 == 0 and level == levels else "APPROVED",
                    "assigned_at": assigned.isoformat(),
                    "completed_at": "" if idx % 41 == 0 and level == levels else completed.isoformat(),
                    "amount": amount,
                }
            )

        if idx <= 12000:
            receipt_date = approved_at + timedelta(days=random.randint(1, 45))
            receipts.append(
                {
                    "receipt_id": f"ORA-REC-{idx:06d}",
                    "receipt_number": f"REC-{idx:06d}",
                    "po_number": po_number,
                    "received_amount": round(amount * random.uniform(0.85, 1.0), 2),
                    "received_at": receipt_date.isoformat(),
                    "business_unit": supplier["business_unit"],
                }
            )
            coupa_receipts.append(
                {
                    "coupa_receipt_id": f"COU-REC-{idx:06d}",
                    "receipt_number": f"REC-{idx:06d}",
                    "po_number": po_number,
                    "received_amount": round(amount * random.uniform(0.85, 1.0), 2),
                    "received_at": receipt_date.isoformat(),
                }
            )

    for idx in range(1, 15001):
        supplier = random.choice(suppliers)
        supplier_num = int(supplier["enterprise_supplier_id"][-4:])
        po_idx = random.randint(1, 10000)
        po_number = "" if idx % 17 == 0 else f"PO-{po_idx:06d}"
        has_receipt = bool(po_number) and idx % 11 != 0
        amount = _money(500, 125000)
        exception_type = ""
        if idx <= 2000 or idx % 19 == 0:
            exception_type = random.choice(EXCEPTION_TYPES)
        status = "BLOCKED" if exception_type else random.choice(["OPEN", "APPROVED", "PAID"])
        created_at = _date(random.randint(1, 210))
        due_at = created_at + timedelta(days=random.choice([15, 30, 45, 60]))
        invoice_id = f"INV-{idx:05d}"
        invoice = {
            "invoice_id": invoice_id,
            "invoice_number": f"INV-{10000 + idx}",
            "oracle_supplier_id": f"ORA-SUP-{supplier_num:04d}",
            "supplier_name": supplier["base_name"],
            "business_unit": supplier["business_unit"],
            "po_number": po_number,
            "receipt_number": f"REC-{po_idx:06d}" if has_receipt else "",
            "invoice_amount": amount,
            "open_amount": 0 if status == "PAID" else round(amount * random.uniform(0.3, 1.0), 2),
            "status": status,
            "exception_type": exception_type,
            "exception_reason": _exception_reason(exception_type),
            "approval_status": "PENDING" if exception_type == "MISSING_APPROVAL" else "APPROVED",
            "owner": random.choice(users)["full_name"],
            "created_at": created_at.isoformat(),
            "due_at": due_at.isoformat(),
        }
        invoices.append(invoice)
        coupa_invoices.append(
            {
                "coupa_invoice_id": f"COU-{invoice_id}",
                "invoice_number": invoice["invoice_number"],
                "coupa_supplier_id": f"COU-SUP-{supplier_num:04d}",
                "supplier_name": _slightly_dirty_name(supplier["base_name"], supplier_num),
                "po_number": po_number,
                "invoice_amount": amount,
                "status": status,
                "created_at": created_at.isoformat(),
            }
        )
        for line_idx in range(1, random.randint(2, 4)):
            invoice_lines.append(
                {
                    "invoice_line_id": f"INV-L-{idx:05d}-{line_idx}",
                    "invoice_id": invoice_id,
                    "line_number": line_idx,
                    "description": fake.bs(),
                    "line_amount": round(amount / 3, 2),
                    "gl_code": f"{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                }
            )
        if idx <= 8000 and status == "PAID":
            payments.append(
                {
                    "payment_id": f"PAY-{idx:05d}",
                    "invoice_id": invoice_id,
                    "payment_amount": amount,
                    "payment_date": (created_at + timedelta(days=random.randint(7, 45))).isoformat(),
                    "payment_status": "CLEARED",
                }
            )

    _write_csv("APP_USERS", users)
    _write_csv("RAW_ORACLE_SUPPLIERS", oracle_suppliers)
    _write_csv("RAW_ORACLE_SUPPLIER_SITES", oracle_sites)
    _write_csv("RAW_ORACLE_PO_HEADERS", oracle_pos)
    _write_csv("RAW_ORACLE_PO_LINES", oracle_po_lines)
    _write_csv("RAW_ORACLE_PO_DISTRIBUTIONS", oracle_distributions)
    _write_csv("RAW_ORACLE_RECEIPTS", receipts)
    _write_csv("RAW_ORACLE_AP_INVOICES", invoices)
    _write_csv("RAW_ORACLE_AP_INVOICE_LINES", invoice_lines)
    _write_csv("RAW_ORACLE_AP_PAYMENTS", payments)
    _write_csv(
        "RAW_ORACLE_GL_CODE_COMBINATIONS",
        [
            {
                "gl_code": f"{idx:03d}-{random.randint(1000, 9999)}",
                "cost_center": random.choice(BUSINESS_UNITS),
                "natural_account": random.choice(["Software", "Services", "Supplies", "Freight"]),
            }
            for idx in range(100, 500)
        ],
    )
    _write_csv("RAW_COUPA_SUPPLIERS", coupa_suppliers)
    _write_csv("RAW_COUPA_REQUISITIONS", reqs)
    _write_csv("RAW_COUPA_REQUISITION_LINES", req_lines)
    _write_csv("RAW_COUPA_PURCHASE_ORDERS", coupa_pos)
    _write_csv("RAW_COUPA_PURCHASE_ORDER_LINES", coupa_po_lines)
    _write_csv("RAW_COUPA_RECEIPTS", coupa_receipts)
    _write_csv("RAW_COUPA_INVOICES", coupa_invoices)
    _write_csv("RAW_COUPA_APPROVALS", approvals)
    _write_csv("RAW_COUPA_USERS", users)
    _write_csv("RAW_COUPA_COMMODITIES", commodities)
    _write_policies()
    print(f"Generated synthetic data in {RAW_DIR} with seed {SEED}.")


def _exception_reason(exception_type: str) -> str:
    return {
        "NO_RECEIPT": "Invoice is blocked because receipt confirmation is missing.",
        "AMOUNT_VARIANCE": "Invoice exceeds purchase order or receipt tolerance.",
        "MISSING_APPROVAL": "Required approval level has not completed.",
        "NO_PO_MATCH": "Invoice does not reference a valid purchase order.",
        "SUPPLIER_MISMATCH": "Supplier identity differs between procurement and payables records.",
        "": "",
    }[exception_type]


def _write_policies() -> None:
    policies = {
        "procurement_policy.md": """# Synthetic Procurement Policy

Purchases must use an approved supplier, valid business unit, and appropriate commodity category. Software and professional services above 75,000 require manager and director approval. Emergency purchases must be documented before payment.
""",
        "supplier_onboarding_policy.md": """# Synthetic Supplier Onboarding Policy

New suppliers require business justification, tax identifier validation, sanctions screening, payment terms review, and bank account verification before activation.
""",
        "invoice_matching_policy.md": """# Synthetic Invoice Matching Policy

Three-way matching is required when a purchase order, receipt, and supplier invoice are all expected for goods or services. Invoices without receipt confirmation, with amount variance above tolerance, or without required approval must remain blocked until resolved.
""",
        "approval_matrix.md": """# Synthetic Approval Matrix

Purchases up to 10,000 require requester manager approval. Purchases from 10,001 to 75,000 require manager and finance approval. Purchases above 75,000 require director approval. Software purchases above 100,000 require executive review.
""",
        "payment_terms_policy.md": """# Synthetic Payment Terms Policy

Standard payment terms are NET 30. Strategic suppliers may use NET 15 with approval. Payment terms inconsistencies between procurement and payables systems must be reviewed before invoice release.
""",
    }
    for filename, content in policies.items():
        (POLICY_DIR / filename).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    generate()
