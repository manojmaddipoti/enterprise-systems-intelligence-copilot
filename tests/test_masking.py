from agents.tools import mask_record


def test_sensitive_fields_are_masked_for_analyst() -> None:
    masked = mask_record(
        {
            "tax_id": "12-3456789-1234",
            "bank_account_number": "123456789012",
            "personal_email": "person@example.com",
            "personal_phone": "555-867-5309",
        },
        "APP_ANALYST",
    )
    assert masked["tax_id"] == "***-**-1234"
    assert masked["bank_account_number"] == "********9012"
    assert masked["personal_email"] == "p***@example.com"
    assert masked["personal_phone"] == "(***) ***-5309"


def test_admin_can_view_sensitive_fields() -> None:
    record = {"bank_account_number": "123456789012"}
    assert mask_record(record, "APP_ADMIN")["bank_account_number"] == "123456789012"
