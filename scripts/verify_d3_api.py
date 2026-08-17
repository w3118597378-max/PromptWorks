"""D3 验收脚本：Prompt 管理 API 全链路验证（按原项目真实 API 语义）。

版本机制（原项目设计）:
  - 创建 Prompt 时带 version+content -> 自动生成第一个版本
  - 更新内容 = PUT /prompts/{id} 带 version+content -> 新建版本并自动切换为当前
  - 切换版本 = PUT /prompts/{id} 带 activate_version_id
  - 同名版本重复创建 -> 400

用法: .venv/Scripts/python.exe scripts/verify_d3_api.py
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000/api/v1"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # 禁系统代理


def request(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with OPENER.open(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "ignore")
        try:
            return exc.code, json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return exc.code, {"detail": raw}


P, F = [], []


def chk(name: str, cond: bool, extra: str = "") -> None:
    (P if cond else F).append(name)
    print(f"{'PASS' if cond else 'FAIL'} {name} {extra}")


def main() -> None:
    import time

    stamp = str(int(time.time()))[-6:]  # 唯一后缀避免重名残留
    class_name = f"信息抽取-{stamp}"
    prompt_name = f"地址抽取-{stamp}"
    tag_name = f"结构化-{stamp}"

    # ---- 分类 CRUD（注意：无 GET 单条端点，列表验证） ----
    code, data = request("POST", "/prompt-classes/", {"name": class_name, "description": "抽取结构化信息"})
    chk("class create", code == 201, f"(got {code}: {data.get('detail', '')})")
    class_id = data.get("id")
    code, data = request("PATCH", f"/prompt-classes/{class_id}", {"description": "改过的描述"})
    chk("class patch", code == 200 and data.get("description") == "改过的描述")
    code, data = request("GET", "/prompt-classes/")
    names = [c["name"] for c in data] if isinstance(data, list) else []
    chk("class in list", code == 200 and class_name in names)

    # ---- Prompt 创建（带 v1 版本） ----
    code, data = request(
        "POST", "/prompts/",
        {"name": prompt_name, "class_id": class_id, "author": "demo",
         "version": "v1", "content": "从文本中抽取地址，输出JSON。"},
    )
    chk("prompt create v1", code == 201, f"(got {code}: {data.get('detail', '')})")
    prompt_id = data.get("id")
    chk("current_version = v1", data["current_version"]["version"] == "v1")

    # ---- 版本迭代：PUT 带 version+content 新建 v2 并自动切换 ----
    code, data = request("PUT", f"/prompts/{prompt_id}",
                         {"version": "v2", "content": "从文本中抽取地址和联系人，输出JSON。"})
    chk("update creates v2", code == 200, f"(got {code}: {data.get('detail', '')})")
    chk("current_version auto-switched", data["current_version"]["version"] == "v2",
        f"(current={data['current_version']['version']})")
    versions = data.get("versions", [])
    chk("2 versions total", len(versions) == 2, f"(got {len(versions)})")
    v1_id = next(v["id"] for v in versions if v["version"] == "v1")

    # ---- 切换版本：activate_version_id ----
    code, data = request("PUT", f"/prompts/{prompt_id}", {"activate_version_id": v1_id})
    chk("activate v1", code == 200 and data["current_version"]["version"] == "v1",
        f"(got {code}, current={data.get('current_version', {}).get('version')})")

    # ---- 重复版本拒绝 ----
    code, data = request("PUT", f"/prompts/{prompt_id}",
                         {"version": "v1", "content": "重复版本内容"})
    chk("dup version rejected", code == 400, f"(got {code}: {data.get('detail', '')})")

    # ---- 标签 ----
    code, data = request("POST", "/prompt-tags/", {"name": tag_name, "color": "#409EFF"})
    chk("tag create", code == 201, f"(got {code})")
    tag_id = data.get("id")
    code, data = request("PUT", f"/prompts/{prompt_id}", {"tag_ids": [tag_id]})
    chk("prompt add tag", code == 200, f"(got {code})")
    code, data = request("GET", f"/prompts/{prompt_id}")
    chk("tag attached", len(data.get("tags", [])) == 1)

    # ---- 删除 ----
    code, _ = request("DELETE", f"/prompts/{prompt_id}")
    chk("prompt delete", code in (200, 204), f"(got {code})")
    code, _ = request("GET", f"/prompts/{prompt_id}")
    chk("prompt 404 after delete", code == 404, f"(got {code})")
    request("DELETE", f"/prompt-classes/{class_id}")
    request("DELETE", f"/prompt-tags/{tag_id}")

    print(f"\n=== {len(P)} passed, {len(F)} failed ===")
    raise SystemExit(1 if F else 0)


if __name__ == "__main__":
    main()
