"""
Утилиты для обработки текста
"""
import re


def normalize_text(text: str) -> str:
    """
    Нормализация текста для поиска
    - Приведение к нижнему регистру
    - Удаление лишних пробелов
    - Удаление markdown разметки (базовое)
    """
    if not text:
        return ""
    
    # Удаление markdown разметки (базовое)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Ссылки [текст](url)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # Жирный **текст**
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)  # Курсив *текст*
    text = re.sub(r'`([^`]+)`', r'\1', text)  # Код `текст`
    text = re.sub(r'#+\s*', '', text)  # Заголовки
    
    # Приведение к нижнему регистру и удаление лишних пробелов
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text


def generate_slug(name: str) -> str:
    """
    Генерация slug из названия тега
    - Транслитерация кириллицы в латиницу
    - Замена пробелов на дефисы
    - Удаление специальных символов
    """
    # Базовая транслитерация (можно расширить)
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    
    name_lower = name.lower()
    slug = ""
    
    for char in name_lower:
        if char in translit_map:
            slug += translit_map[char]
        elif char.isalnum():
            slug += char
        elif char in [' ', '-', '_']:
            slug += '-'
    
    # Удаление множественных дефисов
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    # Ограничение длины
    if len(slug) > 50:
        slug = slug[:50].rstrip('-')
    
    return slug or "tag"

