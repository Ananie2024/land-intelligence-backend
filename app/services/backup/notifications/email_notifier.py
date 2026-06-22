import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    def send(self, recipient: str, subject: str, body: str) -> None:
        logger.info("Simulating email to %s: %s", recipient, subject)
