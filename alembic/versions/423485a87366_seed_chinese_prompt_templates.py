"""seed chinese prompt templates

Revision ID: 423485a87366
Revises: fda9c9923183
Create Date: 2026-08-17 10:57:14.835093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = '423485a87366'
down_revision: Union[str, None] = 'fda9c9923183'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 中文示例模板库：覆盖客服/抽取/摘要/改写/意图/分析 6 类常用业务场景。
# 模板内容带 {user_input} 等占位符，评测时由测试单元的 variables 注入样本。
DEFAULT_CLASS_NAME = "默认分类"
SAMPLE_AUTHOR = "系统预置"
TEMPLATE_TAG = "通用运营"

TEMPLATES = [
    {
        "name": "示例：客服话术优化",
        "description": "客服回复优化：先诊断再改写，提升完整性与亲和力",
        "content": (
            "你是一名资深客服专家。用户的原始回复不够专业或完整，"
            "请先诊断问题（语气、结构、信息完整度），再用亲切专业的口吻改写。\n"
            "用户原话：{user_input}\n"
            "输出格式：\n1. 问题诊断\n2. 优化后的回复"
        ),
    },
    {
        "name": "示例：信息抽取",
        "description": "从非结构化文本抽取实体字段，输出严格 JSON",
        "content": (
            "从以下文本中抽取实体信息，只输出 JSON，不要任何解释。\n"
            "字段：姓名、公司、职位、城市、邮箱、电话。\n"
            "文本：{user_input}"
        ),
    },
    {
        "name": "示例：长文摘要",
        "description": "将长文压缩为结构化摘要，保留关键信息",
        "content": (
            "你是资深编辑。请将以下文章压缩为结构化摘要："
            "一句话主旨（30字内）+ 三个关键要点（每点20字内）。\n"
            "文章：{user_input}"
        ),
    },
    {
        "name": "示例：文案改写",
        "description": "保留原意的营销文案改写，给出 3 个风格版本",
        "content": (
            "你是资深文案。请保留原意改写以下营销文案，"
            "输出 3 个风格版本：正式、活泼、极简，每个版本一行。\n"
            "原文：{user_input}"
        ),
    },
    {
        "name": "示例：意图分类",
        "description": "客服消息意图分类，JSON 输出意图与置信度",
        "content": (
            "你是客服意图识别引擎。将以下用户消息分类为："
            "咨询、投诉、退款、物流、其他。\n"
            "只输出 JSON：{\"intent\": \"类别\", \"confidence\": 0-1, \"reason\": \"一句话理由\"}\n"
            "消息：{user_input}"
        ),
    },
    {
        "name": "示例：数据分析",
        "description": "把自然语言数据问题转成可执行的取数逻辑",
        "content": (
            "你是数据分析师。用户需要一份数据报表，请拆解为："
            "1. 需要哪些字段 2. 筛选条件 3. 聚合方式 4. 输出表格。\n"
            "需求：{user_input}"
        ),
    },
]


def _get_or_create_class(connection: sa.engine.Connection) -> int:
    class_id = connection.execute(
        sa.text("SELECT id FROM prompts_class WHERE name = :name"),
        {"name": DEFAULT_CLASS_NAME},
    ).scalar_one_or_none()
    if class_id is not None:
        return class_id
    connection.execute(
        sa.text("INSERT INTO prompts_class (name) VALUES (:name)"),
        {"name": DEFAULT_CLASS_NAME},
    )
    return connection.execute(
        sa.text("SELECT id FROM prompts_class WHERE name = :name"),
        {"name": DEFAULT_CLASS_NAME},
    ).scalar_one()


def _get_tag_id(connection: sa.engine.Connection) -> int | None:
    return connection.execute(
        sa.text("SELECT id FROM prompt_tags WHERE name = :name"),
        {"name": TEMPLATE_TAG},
    ).scalar_one_or_none()


def _insert_template(connection: sa.engine.Connection, template: dict, class_id: int) -> None:
    prompt_id = connection.execute(
        sa.text(
            "INSERT INTO prompts (class_id, name, description, author) "
            "VALUES (:class_id, :name, :description, :author) RETURNING id"
        ),
        {
            "class_id": class_id,
            "name": template["name"],
            "description": template["description"],
            "author": SAMPLE_AUTHOR,
        },
    ).scalar_one()

    version_id = connection.execute(
        sa.text(
            "INSERT INTO prompts_versions (prompt_id, version, content) "
            "VALUES (:prompt_id, :version, :content) RETURNING id"
        ),
        {"prompt_id": prompt_id, "version": "v1.0.0", "content": template["content"]},
    ).scalar_one()

    connection.execute(
        sa.text("UPDATE prompts SET current_version_id = :vid WHERE id = :pid"),
        {"vid": version_id, "pid": prompt_id},
    )

    tag_id = _get_tag_id(connection)
    if tag_id is not None:
        connection.execute(
            sa.text("INSERT INTO prompt_tag_links (prompt_id, tag_id) VALUES (:pid, :tid)"),
            {"pid": prompt_id, "tid": tag_id},
        )


def upgrade() -> None:
    """Seed 6 Chinese prompt templates for demo & evaluation."""

    connection = op.get_bind()
    class_id = _get_or_create_class(connection)

    for template in TEMPLATES:
        exists = connection.execute(
            sa.text("SELECT 1 FROM prompts WHERE class_id = :cid AND name = :name"),
            {"cid": class_id, "name": template["name"]},
        ).scalar_one_or_none()
        if exists:
            continue
        _insert_template(connection, template, class_id)


def downgrade() -> None:
    """Remove seeded templates (by name, scoped to default class)."""

    connection = op.get_bind()
    class_id = connection.execute(
        sa.text("SELECT id FROM prompts_class WHERE name = :name"),
        {"name": DEFAULT_CLASS_NAME},
    ).scalar_one_or_none()
    if class_id is None:
        return

    for template in TEMPLATES:
        prompt_id = connection.execute(
            sa.text("SELECT id FROM prompts WHERE class_id = :cid AND name = :name"),
            {"cid": class_id, "name": template["name"]},
        ).scalar_one_or_none()
        if prompt_id is None:
            continue
        connection.execute(
            sa.text("DELETE FROM prompt_tag_links WHERE prompt_id = :pid"), {"pid": prompt_id}
        )
        connection.execute(
            sa.text("DELETE FROM prompts_versions WHERE prompt_id = :pid"), {"pid": prompt_id}
        )
        connection.execute(
            sa.text("DELETE FROM prompts WHERE id = :pid"), {"pid": prompt_id}
        )
