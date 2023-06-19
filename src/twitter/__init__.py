from atexit import register
import logging
import click
from rich.logging import RichHandler


LOGGER_NAME = "reddit"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[click])],
)
logger = logging.getLogger(LOGGER_NAME)


logging.getLogger("clickhouse_connect").setLevel(logging.ERROR)
logging.getLogger("clickhouse_connect").setLevel(logging.ERROR)
logging.getLogger("numexpr").setLevel(logging.ERROR)
# logging.getLogger("chromadb").setLevel(logging.ERROR)


@register
def bye():
    print("Bye!")
