"""add_image_url_to_prompts

Revision ID: d33fd0df882b
Revises: 001_add_fts5
Create Date: 2026-02-03 21:57:35.488957

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "d33fd0df882b"
down_revision = "001_add_fts5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавление поля image_url в таблицу prompts
    op.add_column("prompts", sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Удаление поля image_url из таблицы prompts
    op.drop_column("prompts", "image_url")
