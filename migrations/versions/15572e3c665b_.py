"""empty message

Revision ID: 15572e3c665b
Revises: 28968696ccec
Create Date: 2024-03-26 21:34:29.351041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15572e3c665b'
down_revision = '28968696ccec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_answers')
    with op.batch_alter_table('answers', schema=None) as batch_op:
        batch_op.alter_column('text',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)
        batch_op.drop_column('position')

    with op.batch_alter_table('user_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('test_result', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_data', schema=None) as batch_op:
        batch_op.drop_column('test_result')

    with op.batch_alter_table('answers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('position', sa.INTEGER(), nullable=True))
        batch_op.alter_column('text',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)

    op.create_table('_alembic_tmp_answers',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('question_id', sa.INTEGER(), nullable=True),
    sa.Column('text', sa.VARCHAR(length=200), nullable=True),
    sa.Column('is_correct', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###