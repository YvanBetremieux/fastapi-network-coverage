"""Add a table that match all 3 models

Revision ID: 65aac47342a1
Revises: 560ee29cbb84
Create Date: 2023-01-29 17:41:23.406730

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65aac47342a1'
down_revision = '560ee29cbb84'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('network_coverage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city', sa.Integer(), nullable=True),
    sa.Column('operator', sa.Integer(), nullable=True),
    sa.Column('network', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['city'], ['city.id'], ),
    sa.ForeignKeyConstraint(['network'], ['network.id'], ),
    sa.ForeignKeyConstraint(['operator'], ['operator.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('city', 'operator', 'network')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('network_coverage')
    # ### end Alembic commands ###
