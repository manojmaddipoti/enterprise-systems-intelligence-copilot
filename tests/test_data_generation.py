from pathlib import Path

import pandas as pd


def test_seed_outputs_exist() -> None:
    expected = [
        "RAW_ORACLE_SUPPLIERS.csv",
        "RAW_COUPA_SUPPLIERS.csv",
        "RAW_ORACLE_AP_INVOICES.csv",
        "RAW_COUPA_APPROVALS.csv",
        "APP_USERS.csv",
    ]
    for filename in expected:
        assert (Path("data/raw") / filename).exists()


def test_supplier_data_is_synthetic_and_laptop_friendly() -> None:
    suppliers = pd.read_csv("data/raw/RAW_ORACLE_SUPPLIERS.csv")
    assert len(suppliers) == 470
    assert suppliers["supplier_name"].nunique() > 400
    assert suppliers["tax_id"].astype(str).str.contains("-").any()
