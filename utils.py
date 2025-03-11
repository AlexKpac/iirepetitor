import re
from typing import Tuple


def get_file_id(data: str) -> Tuple[str, bool]:
    """Извлекает file_id из ответа DeepSeek."""
    match = re.search(r'([a-f0-9-]{36})', data)
    return (match.group(0), True) if match else (data, False)