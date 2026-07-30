from app.core.config import Settings


def test_cors_origins_are_parsed_from_comma_separated_setting() -> None:
    settings = Settings(cors_origins="https://app.example.com, https://admin.example.com")

    assert settings.allowed_cors_origins == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


def test_empty_cors_origins_are_ignored() -> None:
    settings = Settings(cors_origins="http://localhost:3000, ,")

    assert settings.allowed_cors_origins == ["http://localhost:3000"]
