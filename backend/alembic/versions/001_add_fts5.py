"""Add FTS5 full-text search

Revision ID: 001_add_fts5
Revises:
Create Date: 2026-02-03 12:00:00.000000

"""


from alembic import op

# revision identifiers, used by Alembic.
revision = "001_add_fts5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание FTS5 таблицы
    op.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS prompts_fts USING fts5(
            prompt_id UNINDEXED,
            text,
            normalized_text,
            tags,
            content='prompts',
            content_rowid='id'
        )
    """)

    # Триггер для INSERT
    op.execute("""
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

    # Триггер для UPDATE
    op.execute("""
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

    # Триггер для DELETE (мягкое удаление)
    op.execute("""
        CREATE TRIGGER IF NOT EXISTS prompts_fts_delete AFTER UPDATE OF deleted_at ON prompts BEGIN
            DELETE FROM prompts_fts WHERE rowid = old.id;
        END
    """)

    # Триггер для обновления тегов при добавлении
    op.execute("""
        CREATE TRIGGER IF NOT EXISTS prompts_fts_tags_update AFTER INSERT ON prompt_tags BEGIN
            UPDATE prompts_fts SET
                tags = (SELECT GROUP_CONCAT(t.name, ' ') 
                       FROM tags t 
                       JOIN prompt_tags pt ON t.id = pt.tag_id 
                       WHERE pt.prompt_id = new.prompt_id)
            WHERE prompt_id = new.prompt_id;
        END
    """)

    # Триггер для обновления тегов при удалении
    op.execute("""
        CREATE TRIGGER IF NOT EXISTS prompts_fts_tags_delete AFTER DELETE ON prompt_tags BEGIN
            UPDATE prompts_fts SET
                tags = (SELECT GROUP_CONCAT(t.name, ' ') 
                       FROM tags t 
                       JOIN prompt_tags pt ON t.id = pt.tag_id 
                       WHERE pt.prompt_id = old.prompt_id)
            WHERE prompt_id = old.prompt_id;
        END
    """)

    # Заполнение FTS5 существующими данными
    op.execute("""
        INSERT INTO prompts_fts(rowid, prompt_id, text, normalized_text, tags)
        SELECT 
            p.id,
            p.id,
            p.text,
            p.normalized_text,
            COALESCE((SELECT GROUP_CONCAT(t.name, ' ') 
                      FROM tags t 
                      JOIN prompt_tags pt ON t.id = pt.tag_id 
                      WHERE pt.prompt_id = p.id), '')
        FROM prompts p
        WHERE p.deleted_at IS NULL
    """)


def downgrade() -> None:
    # Удаление триггеров
    op.execute("DROP TRIGGER IF EXISTS prompts_fts_insert")
    op.execute("DROP TRIGGER IF EXISTS prompts_fts_update")
    op.execute("DROP TRIGGER IF EXISTS prompts_fts_delete")
    op.execute("DROP TRIGGER IF EXISTS prompts_fts_tags_update")
    op.execute("DROP TRIGGER IF EXISTS prompts_fts_tags_delete")

    # Удаление FTS5 таблицы
    op.execute("DROP TABLE IF EXISTS prompts_fts")
