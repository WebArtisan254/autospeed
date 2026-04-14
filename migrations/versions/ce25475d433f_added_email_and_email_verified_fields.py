"""Added email and email_verified fields

Revision ID: ce25475d433f
Revises: ce5e729b0602
Create Date: 2026-04-14 14:20:48.838726

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce25475d433f'
down_revision = 'ce5e729b0602'
branch_labels = None
depends_on = None


def upgrade():
    # 1) add as nullable so existing rows can be copied
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("email_verified", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("session_valid_after", sa.DateTime(), nullable=True))

    # 2) backfill existing rows (safe early-dev defaults)
    op.execute("UPDATE users SET email_verified = 0 WHERE email_verified IS NULL")
    op.execute("UPDATE users SET session_valid_after = CURRENT_TIMESTAMP WHERE session_valid_after IS NULL")
    op.execute("UPDATE users SET email = username || '@example.invalid' WHERE email IS NULL")

    # 3) enforce NOT NULL and add unique constraint
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("email", existing_type=sa.String(length=255), nullable=False)
        batch_op.alter_column("email_verified", existing_type=sa.Boolean(), nullable=False)
        batch_op.alter_column("session_valid_after", existing_type=sa.DateTime(), nullable=False)
        batch_op.create_unique_constraint("uq_users_email", ["email"])


    # ### end Alembic commands ###

def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("uq_users_email", type_="unique")
        batch_op.drop_column("session_valid_after")
        batch_op.drop_column("email_verified")
        batch_op.drop_column("email")



    # ### end Alembic commands ###
