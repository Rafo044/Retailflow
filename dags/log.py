import logging
from functools import wraps
from pathlib import Path

filename = ""
current_dir = Path(__file__).resolve().parent
log_dir = current_dir.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "data_quality_checks.log"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=log_file,
    filemode="a"
)

# Decorator
def log_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import builtins
        original_print = builtins.print
        builtins.print = lambda *p, **k: logging.info(" ".join(map(str, p)))

        try:
            return func(*args, **kwargs)
        finally:
            builtins.print = original_print
    return wrapper
