"""评测报告生成服务（改造点：方案 2.4 - 评测报告导出）。

将测试任务的 AI 评分汇总渲染为自包含的中文 HTML 报告，
用户可在浏览器中直接"打印为 PDF"保存，形成可交付的评测证据。

设计：
- 纯 HTML + 内联 CSS，无外部资源，任何浏览器可打开/打印
- 数据来自 build_task_score_summary() 的输出（与 ai-scores 端点一致）
- 分级配色：>=85 绿 / 70-84 黄 / <70 红，一眼看短板
"""

from __future__ import annotations

import html
from datetime import UTC, datetime
from typing import Any


def _score_class(score: float | None) -> str:
    if score is None:
        return "na"
    if score >= 85.0:
        return "high"
    if score >= 70.0:
        return "mid"
    return "low"


def _fmt(value: Any, digits: int = 1) -> str:
    if value is None:
        return "--"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def _esc(text: Any) -> str:
    return html.escape(str(text) if text is not None else "")


def _now_str() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


def build_report_html(task: dict, summary: dict) -> str:
    """由任务信息 + 评分汇总生成报告 HTML。"""

    status_info = summary.get("status") or {}
    scores: list[dict] = summary.get("scores") or []
    unit_summaries: dict[str, dict] = summary.get("unit_summaries") or {}

    # ---- 单元汇总表 ----
    unit_rows: list[str] = []
    for unit_id_str, unit in sorted(
        unit_summaries.items(), key=lambda kv: (kv[1].get("avg_score") or 0), reverse=True
    ):
        dims: dict[str, dict] = unit.get("dimension_stats") or {}
        dim_cells = "".join(
            f'<td><span class="badge {_score_class(d["avg"])}">{_fmt(d["avg"])}</span></td>'
            for d in dims.values()
        )
        stddev = unit.get("stddev")
        stable = "稳定" if stddev is not None and float(stddev) < 5.0 else "波动"
        unit_rows.append(
            "<tr>"
            f"<td>{_esc(unit.get('unit_id'))}</td>"
            f"<td>{_esc(unit.get('unit_name'))}</td>"
            f"<td class='num'>{int(unit.get('count', 0))}</td>"
            f"<td><span class='badge {_score_class(unit.get('avg_score'))}'>{_fmt(unit.get('avg_score'))}</span></td>"
            f"{dim_cells}"
            f"<td class='num'>{_fmt(stddev)}</td>"
            f"<td>{stable}</td>"
            "</tr>"
        )

    # ---- 明细行（scores 可能是 ORM 对象或 dict，统一 getattr 访问） ----
    detail_rows: list[str] = []
    for s in scores:
        dims: dict[str, float] = getattr(s, "dimension_scores", None) or s.get("dimension_scores") or {}
        run_index = getattr(s, "run_index", None) if not isinstance(s, dict) else s.get("run_index")
        unit_id = getattr(s, "unit_id", None) if not isinstance(s, dict) else s.get("unit_id")
        model_name = (
            getattr(s, "model_name", None) or getattr(s, "evaluator_model_name", None)
            if not isinstance(s, dict)
            else s.get("model_name") or s.get("evaluator_model_name")
        )
        overall = getattr(s, "overall_score", None) if not isinstance(s, dict) else s.get("overall_score")
        reason = getattr(s, "reason", None) if not isinstance(s, dict) else s.get("reason")
        dim_cells = "".join(
            f'<td><span class="badge {_score_class(v)}">{_fmt(v)}</span></td>' for v in dims.values()
        )
        detail_rows.append(
            "<tr>"
            f"<td class='num'>{_esc(run_index)}</td>"
            f"<td class='num'>{_esc(unit_id)}</td>"
            f"<td>{_esc(model_name)}</td>"
            f"<td><span class='badge {_score_class(overall)}'>{_fmt(overall)}</span></td>"
            f"{dim_cells}"
            f"<td class='reason'>{_esc(reason)}</td>"
            "</tr>"
        )

    overview_badge = _score_class(status_info.get("percentage"))
    completed = int(status_info.get("completed") or 0)
    total = int(status_info.get("total") or 0)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>PromptWorks 评测报告 - {_esc(task.get('name'))}</title>
<style>
  body {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; color: #303133; margin: 32px; }}
  h1 {{ font-size: 20px; border-bottom: 2px solid #409eef; padding-bottom: 8px; }}
  h2 {{ font-size: 15px; color: #409eef; margin-top: 28px; }}
  .meta {{ color: #909399; font-size: 12px; margin-bottom: 24px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 12px; margin-top: 8px; }}
  th, td {{ border: 1px solid #e4e7ed; padding: 6px 8px; text-align: left; }}
  th {{ background: #f5f7fa; font-weight: 600; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.reason {{ max-width: 380px; line-height: 1.5; }}
  .badge {{ display: inline-block; min-width: 34px; text-align: center; padding: 2px 6px;
            border-radius: 4px; font-weight: 600; font-size: 12px; }}
  .high {{ background: #67c23a; color: #fff; }}
  .mid {{ background: #e6a23c; color: #fff; }}
  .low  {{ background: #f56c6c; color: #fff; }}
  .na   {{ background: #c0c4cc; color: #fff; }}
  .summary-box {{ display: flex; gap: 16px; margin: 12px 0; }}
  .kpi {{ border: 1px solid #e4e7ed; border-radius: 6px; padding: 10px 16px; min-width: 120px; }}
  .kpi .label {{ color: #909399; font-size: 11px; }}
  .kpi .value {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
  .kpi .value.high {{ color: #67c23a; }} .kpi .value.mid {{ color: #e6a23c; }} .kpi .value.low {{ color: #f56c6c; }}
  .foot {{ margin-top: 32px; color: #909399; font-size: 11px; border-top: 1px solid #e4e7ed; padding-top: 12px; }}
  @media print {{ body {{ margin: 8px; }} h2 {{ page-break-before: auto; }} }}
</style>
</head>
<body>
<h1>PromptWorks 评测报告</h1>
<div class="meta">
  任务：{_esc(task.get('name'))} ｜ 状态：{_esc(status_info.get('status'))}
  ｜ 生成时间：{_now_str()}
</div>

<div class="summary-box">
  <div class="kpi"><div class="label">评分完成度</div>
    <div class="value {overview_badge}">{completed}/{total}</div></div>
  <div class="kpi"><div class="label">评测语言</div>
    <div class="value" style="font-size:16px;line-height:32px;">{_esc(status_info.get('language'))}</div></div>
  <div class="kpi"><div class="label">评估模型</div>
    <div class="value" style="font-size:13px;line-height:32px;max-width:200px;overflow:hidden;text-overflow:ellipsis;">{_esc(_first_eval_model(scores))}</div></div>
</div>

<h2>一、单元汇总（按平均分排序）</h2>
<table>
  <thead><tr>
    <th>单元 ID</th><th>单元名称</th><th class="num">样本数</th>
    <th>平均分</th><th>准确性</th><th>完整性</th><th>清晰度</th><th>稳定性</th>
    <th class="num">标准差</th><th>稳定性判定</th>
  </tr></thead>
  <tbody>{''.join(unit_rows) or '<tr><td colspan="10">暂无评分数据</td></tr>'}</tbody>
</table>

<h2>二、评分明细</h2>
<table>
  <thead><tr>
    <th class="num">轮次</th><th class="num">单元</th><th>模型</th>
    <th>总分</th><th>准确性</th><th>完整性</th><th>清晰度</th><th>稳定性</th>
    <th>评分理由</th>
  </tr></thead>
  <tbody>{''.join(detail_rows) or '<tr><td colspan="9">暂无评分明细</td></tr>'}</tbody>
</table>

<div class="foot">
  本报告由 PromptWorks 自动生成 ｜ 评分维度：准确性 / 完整性 / 清晰度 / 稳定性 ｜
  等级：≥85 优秀（绿） 70-84 良好（黄） &lt;70 待改进（红）
</div>
</body>
</html>"""


def _first_eval_model(scores: list[dict]) -> str:
    for s in scores:
        value = getattr(s, "evaluator_model_name", None) if not isinstance(s, dict) else s.get("evaluator_model_name")
        if value:
            return value
    return "--"


__all__ = ["build_report_html"]