"""
Модуль для работы с SQLite FTS5 полнотекстовым поиском
"""

from typing import List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.models.prompt import Prompt
from app.models.tag import Tag

logger = get_logger(__name__)


def init_fts5_table(db: Session) -> None:
    """
    Инициализация FTS5 таблицы для полнотекстового поиска

    Создает виртуальную таблицу FTS5 и триггеры для синхронизации
    """
    # Создание FTS5 таблицы
    db.execute(
        text("""
        CREATE VIRTUAL TABLE IF NOT EXISTS prompts_fts USING fts5(
            prompt_id UNINDEXED,
            text,
            normalized_text,
            tags,
            content='prompts',
            content_rowid='id'
        )
    """)
    )

    # Триггер для INSERT
    db.execute(
        text("""
        CREATE TRIGGER IF NOT EXISTS prompts_fts_insert AFTER INSERT ON prompts BEGIN
            INSERT INTO prompts_fts(rowid, prompt_id, text, normalized_text, tags)
            VALUES (
                new.id,
                new.id,
                new.text,
                new.normalized_text,
                (SELECT GROUP_CONCAT(t.name, ' ') 
                 FROM tags t 
                 JOIN prompt_tags pt ON t.id = pt.tag_id 
                 WHERE pt.prompt_id = new.id)
            );
        END
    """)
    )

    # Триггер для UPDATE
    db.execute(
        text("""
        CREATE TRIGGER IF NOT EXISTS prompts_fts_update AFTER UPDATE ON prompts BEGIN
            UPDATE prompts_fts SET
                text = new.text,
                normalized_text = new.normalized_text,
                tags = (SELECT GROUP_CONCAT(t.name, ' ') 
                       FROM tags t 
                       JOIN prompt_tags pt ON t.id = pt.tag_id 
                       WHERE pt.prompt_id = new.id)
            WHERE rowid = new.id;
        END
    """)
    )

    # Триггер для DELETE (мягкое удаление)
    db.execute(
        text("""
        CREATE TRIGGER IF NOT EXISTS prompts_fts_delete AFTER UPDATE OF deleted_at ON prompts BEGIN
            DELETE FROM prompts_fts WHERE rowid = old.id;
        END
    """)
    )

    # Триггер для обновления тегов
    db.execute(
        text("""
        CREATE TRIGGER IF NOT EXISTS prompts_fts_tags_update AFTER INSERT ON prompt_tags BEGIN
            UPDATE prompts_fts SET
                tags = (SELECT GROUP_CONCAT(t.name, ' ') 
                       FROM tags t 
                       JOIN prompt_tags pt ON t.id = pt.tag_id 
                       WHERE pt.prompt_id = new.prompt_id)
            WHERE prompt_id = new.prompt_id;
        END
    """)
    )

    db.execute(
        text("""
        CREATE TRIGGER IF NOT EXISTS prompts_fts_tags_delete AFTER DELETE ON prompt_tags BEGIN
            UPDATE prompts_fts SET
                tags = (SELECT GROUP_CONCAT(t.name, ' ') 
                       FROM tags t 
                       JOIN prompt_tags pt ON t.id = pt.tag_id 
                       WHERE pt.prompt_id = old.prompt_id)
            WHERE prompt_id = old.prompt_id;
        END
    """)
    )

    db.commit()
    logger.info("FTS5 таблица и триггеры созданы")


def search_fts5(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 50,
    tag_ids: Optional[List[int]] = None,
    pinned_only: Optional[bool] = None,
) -> Tuple[List[Prompt], int]:
    """
    Поиск промптов с использованием FTS5

    Args:
        db: Сессия БД
        query: Поисковый запрос
        skip: Пропустить результатов
        limit: Максимум результатов
        tag_ids: Фильтр по тегам
        pinned_only: Только закрепленные

    Returns:
        Tuple: (список промптов, общее количество)
    """
    # Экранирование специальных символов FTS5
    # FTS5 использует специальный синтаксис, нужно экранировать
    escaped_query = query.replace('"', '""').replace("'", "''")

    # Построение базового запроса FTS5
    fts_query = f'"{escaped_query}"* OR {escaped_query}*'

    # Базовый SQL для поиска
    base_sql = """
        SELECT DISTINCT p.*, 
               bm25(prompts_fts) as rank_score,
               CASE 
                   WHEN prompts_fts.tags MATCH :tag_match THEN 100
                   WHEN prompts_fts.text MATCH :text_match THEN 50
                   ELSE 10
               END as match_score
        FROM prompts_fts
        JOIN prompts p ON prompts_fts.prompt_id = p.id
        WHERE prompts_fts MATCH :query
          AND p.deleted_at IS NULL
    """

    # Параметры запроса
    params = {"query": fts_query, "tag_match": f'"{escaped_query}"', "text_match": f'"{escaped_query}"'}

    # Добавление фильтров
    if pinned_only is not None:
        base_sql += " AND p.is_pinned = :pinned"
        params["pinned"] = pinned_only

    # Фильтр по тегам
    if tag_ids:
        tag_ids_str = ",".join(map(str, tag_ids))
        base_sql += f" AND p.id IN (SELECT prompt_id FROM prompt_tags WHERE tag_id IN ({tag_ids_str}))"

    # Сортировка: сначала по match_score (точное совпадение тега > текста > частичное),
    # затем по rank_score (BM25), затем по дате
    base_sql += """
        ORDER BY match_score DESC, rank_score ASC, p.created_at DESC
    """

    # Подсчет общего количества
    count_sql = """
        SELECT COUNT(DISTINCT p.id)
        FROM prompts_fts
        JOIN prompts p ON prompts_fts.prompt_id = p.id
        WHERE prompts_fts MATCH :query
          AND p.deleted_at IS NULL
    """

    if pinned_only is not None:
        count_sql += " AND p.is_pinned = :pinned"

    if tag_ids:
        tag_ids_str = ",".join(map(str, tag_ids))
        count_sql += f" AND p.id IN (SELECT prompt_id FROM prompt_tags WHERE tag_id IN ({tag_ids_str}))"

    try:
        # Выполнение запроса подсчета
        count_result = db.execute(text(count_sql), params)
        total = count_result.scalar() or 0

        # Выполнение основного запроса с пагинацией
        search_sql = base_sql + " LIMIT :limit OFFSET :skip"
        params["limit"] = limit
        params["skip"] = skip

        result = db.execute(text(search_sql), params)
        rows = result.fetchall()

        # Получение ID промптов
        prompt_ids = [row[0] for row in rows]  # Первый столбец - id

        if not prompt_ids:
            return [], total

        # Загрузка промптов с тегами
        prompts = db.query(Prompt).filter(Prompt.id.in_(prompt_ids), Prompt.deleted_at.is_(None)).all()

        # Сортировка по порядку из FTS5 результата
        prompt_dict = {p.id: p for p in prompts}
        sorted_prompts = [prompt_dict[pid] for pid in prompt_ids if pid in prompt_dict]

        return sorted_prompts, total

    except Exception as e:
        logger.error(f"Ошибка FTS5 поиска: {e}", extra={"error": str(e), "query": query})
        # Fallback на обычный поиск
        return [], 0


def search_fallback(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 50,
    tag_ids: Optional[List[int]] = None,
    pinned_only: Optional[bool] = None,
) -> Tuple[List[Prompt], int]:
    """
    Резервный вариант поиска с использованием LIKE

    Используется если FTS5 недоступен или произошла ошибка
    """
    from app.utils.text import normalize_text

    normalized_query = normalize_text(query)

    # Базовый запрос
    q = db.query(Prompt).filter(Prompt.deleted_at.is_(None))

    # Поиск по тексту или normalized_text
    search_filter = Prompt.text.contains(query) | Prompt.normalized_text.contains(normalized_query)

    # Поиск по тегам
    if tag_ids:
        q = q.join(Prompt.tags).filter(Tag.id.in_(tag_ids))

    # Фильтр по закрепленным
    if pinned_only is not None:
        q = q.filter(Prompt.is_pinned == pinned_only)

    # Применение поискового фильтра
    q = q.filter(search_filter)

    # Подсчет
    total = q.count()

    # Сортировка: сначала закрепленные, потом по релевантности (начинается с запроса)
    # Простая эвристика: промпты, где текст начинается с запроса, выше
    q = q.order_by(
        Prompt.is_pinned.desc(),
        Prompt.text.startswith(query).desc(),
        Prompt.normalized_text.startswith(normalized_query).desc(),
        Prompt.created_at.desc(),
    )

    # Пагинация
    prompts = q.offset(skip).limit(limit).all()

    return prompts, total
