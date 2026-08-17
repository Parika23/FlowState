"""Convert flow_state to integer

Revision ID: cda793271a4f
Revises: 6a490d588ca9
Create Date: 2026-08-01 00:10:38.866605

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cda793271a4f"
down_revision = "6a490d588ca9"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table("daily_logs") as batch_op:

        batch_op.drop_column("flow_state")

        batch_op.add_column(
            sa.Column(
                "flow_state",
                sa.Integer(),
                nullable=False,
                server_default="0"
            )
        )


def downgrade():

    with op.batch_alter_table("daily_logs") as batch_op:

        batch_op.drop_column("flow_state")

        batch_op.add_column(
            sa.Column(
                "flow_state",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false()
            )
        )