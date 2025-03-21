"""frequency_mode column for user table added

Revision ID: 3951933a1a3f
Revises: e78c7684d0d1
Create Date: 2025-03-03 15:56:23.129274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3951933a1a3f'
down_revision: Union[str, None] = 'e78c7684d0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('settings_user_frequency',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('interval_seconds', sa.Integer(), nullable=False),
    sa.Column('times_per_day', sa.Integer(), nullable=False),
    sa.Column('specific_times', sa.Integer(), nullable=True),
    sa.Column('send_at_nighttime', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('settings_user_frequency')
    # ### end Alembic commands ###
