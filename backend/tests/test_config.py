import pytest

from app.core.app_config import Settings


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("mysql://u:p@host:3306/railway", "mysql+pymysql://u:p@host:3306/railway?charset=utf8mb4"),
        ("mysql+pymysql://u:p@h/db?charset=utf8mb4", "mysql+pymysql://u:p@h/db?charset=utf8mb4"),
        ("mysql://u:p@h/db?ssl=true", "mysql+pymysql://u:p@h/db?ssl=true&charset=utf8mb4"),
    ],
)
def test_database_url_normalized(raw: str, expected: str) -> None:
    assert Settings(database_url=raw).database_url == expected
