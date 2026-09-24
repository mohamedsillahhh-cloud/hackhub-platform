"""Add revocable sessions and database invariants.

Revision ID: d24f93a91230
Revises: b742d814514c
Create Date: 2026-09-23
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "d24f93a91230"
down_revision: Union[str, None] = "b742d814514c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column(
                "password_reset_version",
                sa.Integer(),
                server_default="0",
                nullable=False,
            )
        )
        batch.add_column(sa.Column("telegram_chat_id", sa.String(length=100), nullable=True))

    if "auth_sessions" not in sa.inspect(op.get_bind()).get_table_names():
        op.create_table(
            "auth_sessions",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("user_id", sa.Uuid(), nullable=False),
            sa.Column("refresh_token_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
        op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
        op.create_index("ix_auth_sessions_revoked_at", "auth_sessions", ["revoked_at"])

    with op.batch_alter_table("events") as batch:
        batch.create_check_constraint("ck_events_date_range", "end_date > start_date")
        batch.create_check_constraint("ck_events_min_team_size", "min_team_size >= 1")
        batch.create_check_constraint("ck_events_team_size_range", "max_team_size >= min_team_size")
    with op.batch_alter_table("teams") as batch:
        batch.create_unique_constraint("uq_teams_event_name", ["event_id", "name"])
    with op.batch_alter_table("team_members") as batch:
        batch.create_unique_constraint("uq_team_members_team_user", ["team_id", "user_id"])
    with op.batch_alter_table("challenge_categories") as batch:
        batch.create_unique_constraint("uq_challenge_categories_event_name", ["event_id", "name"])
    with op.batch_alter_table("criteria") as batch:
        batch.create_unique_constraint("uq_criteria_category_name", ["challenge_category_id", "name"])
        batch.create_check_constraint("ck_criteria_max_score_positive", "max_score > 0")
        batch.create_check_constraint("ck_criteria_weight_positive", "weight > 0")
    with op.batch_alter_table("projects") as batch:
        batch.create_unique_constraint("uq_projects_team", ["team_id"])
    with op.batch_alter_table("project_technologies") as batch:
        batch.create_unique_constraint("uq_project_technologies_project_name", ["project_id", "name"])
    with op.batch_alter_table("evaluations") as batch:
        batch.create_unique_constraint("uq_evaluations_project_judge", ["project_id", "judge_id"])
    with op.batch_alter_table("evaluation_scores") as batch:
        batch.create_unique_constraint(
            "uq_evaluation_scores_evaluation_criterion",
            ["evaluation_id", "criterion_id"],
        )
        batch.create_check_constraint("ck_evaluation_scores_nonnegative", "score >= 0")
    with op.batch_alter_table("certificates") as batch:
        batch.create_unique_constraint("uq_certificates_user_event_type", ["user_id", "event_id", "type"])


def downgrade() -> None:
    with op.batch_alter_table("certificates") as batch:
        batch.drop_constraint("uq_certificates_user_event_type", type_="unique")
    with op.batch_alter_table("evaluation_scores") as batch:
        batch.drop_constraint("ck_evaluation_scores_nonnegative", type_="check")
        batch.drop_constraint("uq_evaluation_scores_evaluation_criterion", type_="unique")
    with op.batch_alter_table("evaluations") as batch:
        batch.drop_constraint("uq_evaluations_project_judge", type_="unique")
    with op.batch_alter_table("project_technologies") as batch:
        batch.drop_constraint("uq_project_technologies_project_name", type_="unique")
    with op.batch_alter_table("projects") as batch:
        batch.drop_constraint("uq_projects_team", type_="unique")
    with op.batch_alter_table("criteria") as batch:
        batch.drop_constraint("ck_criteria_weight_positive", type_="check")
        batch.drop_constraint("ck_criteria_max_score_positive", type_="check")
        batch.drop_constraint("uq_criteria_category_name", type_="unique")
    with op.batch_alter_table("challenge_categories") as batch:
        batch.drop_constraint("uq_challenge_categories_event_name", type_="unique")
    with op.batch_alter_table("team_members") as batch:
        batch.drop_constraint("uq_team_members_team_user", type_="unique")
    with op.batch_alter_table("teams") as batch:
        batch.drop_constraint("uq_teams_event_name", type_="unique")
    with op.batch_alter_table("events") as batch:
        batch.drop_constraint("ck_events_team_size_range", type_="check")
        batch.drop_constraint("ck_events_min_team_size", type_="check")
        batch.drop_constraint("ck_events_date_range", type_="check")

    op.drop_index("ix_auth_sessions_revoked_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("telegram_chat_id")
        batch.drop_column("password_reset_version")
