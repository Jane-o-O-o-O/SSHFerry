from unittest.mock import MagicMock

from src.engines.sftp_engine import SftpEngine
from src.shared.models import SiteConfig


def _site() -> SiteConfig:
    return SiteConfig(
        name="demo",
        host="example.com",
        port=22,
        username="alice",
        auth_method="password",
        password="secret",
        remote_root="/remote",
    )


def test_disconnect_without_successful_connect_does_not_log():
    logger = MagicMock()
    engine = SftpEngine(_site(), logger=logger)

    engine.disconnect()

    logger.info.assert_not_called()
