from loguru import logger
from rich.logging import RichHandler

# <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> |

logger.remove()
logger.add(RichHandler(), level="INFO", format="<level>{message}</level>")
