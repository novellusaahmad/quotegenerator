"""add placeholder_map to loan_notes

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2024-07-24 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('loan_notes', sa.Column('placeholder_map', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('loan_notes', 'placeholder_map')
