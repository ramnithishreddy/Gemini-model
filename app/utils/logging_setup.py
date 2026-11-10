import logging
import sys

from app.utils.correlation import get_correlation_id


class CorrelationFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.correlation_id = get_correlation_id() or "-"
        return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())

    if any(getattr(h, "_correlation", False) for h in root.handlers):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        CorrelationFormatter(
            "%(asctime)s [%(levelname)s] [cid=%(correlation_id)s] %(name)s - %(message)s"
        )
    )
    handler._correlation = True  # type: ignore[attr-defined]
    root.addHandler(handler)

    for noisy in ("httpx", "httpcore", "urllib3", "google.auth"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
