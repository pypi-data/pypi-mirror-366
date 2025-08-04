"""
tool2openai - Библиотека для работы с OpenAI API
"""

# Импортируем основные функции и классы из вашего файла
from .tool2openai import (
    OpenAIClient,
    Config,
)

__version__ = "0.1.5"
__author__ = "Nehcy"

# Опционально: определяем, что будет доступно при импорте *
__all__ = [
    "OpenAIClient",
    "Config",
]