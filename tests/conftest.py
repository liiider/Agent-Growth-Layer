import pytest

from server.config import get_settings


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    database_path = tmp_path / "agent_growth_layer.db"
    monkeypatch.setenv("AGL_DATABASE_URL", f"sqlite:///{database_path}")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
