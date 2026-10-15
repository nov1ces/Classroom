"""Portable paths and the frozen placement index for the second edition."""

import hashlib
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = Path(os.environ.get("PDF_BUILD_DIR", ROOT / "build")).expanduser().resolve()
OUT = BUILD / "408_薄弱点精读与练习册_第二版.pdf"
EXPECTED_COUNTS = {"old": 457, "big": 34, "relax": 80}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_items():
    return read_json(ROOT / "data" / "items.json")


def load_sources():
    local = ROOT / "sources.local.json"
    default = local if local.exists() else ROOT / "sources.example.json"
    config = Path(os.environ.get("PDF_SOURCES_CONFIG", default)).expanduser().resolve()
    bindings = read_json(config)
    definitions = read_json(ROOT / "data" / "sources.json")
    result = {}
    for source_id, metadata in definitions.items():
        if source_id not in bindings or not isinstance(bindings[source_id], str):
            raise ValueError(f"{config}: 缺少文件路径 {source_id}")
        path = Path(bindings[source_id]).expanduser()
        if not path.is_absolute():
            path = config.parent / path
        result[source_id] = {**metadata, "path": str(path.resolve())}
    return result


def load_manifest():
    sources = load_sources()
    manifest = read_items()
    for items in manifest.values():
        for item in items:
            for side in ("question", "answer"):
                item[side + "_path"] = sources[item[side + "_source"]]["path"]
    return manifest


def validate_inputs():
    """Reject mismatched editions before using their page and crop coordinates."""
    import fitz
    from topics import TOPICS

    items = read_items()
    counts = {key: len(value) for key, value in items.items()}
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"题目索引数量不符: {counts}")
    all_items = [item for group in items.values() for item in group]
    if len({item["id"] for item in all_items}) != sum(counts.values()):
        raise ValueError("题目索引存在重复 ID")
    topics = {topic["code"] for topic in TOPICS}
    if any(item["topic"] not in topics for item in items["old"]):
        raise ValueError("旧题引用了不存在的知识主题")
    sources = load_sources()
    documents = {}
    problems = []
    try:
        for source_id, metadata in sources.items():
            path = Path(metadata["path"])
            if not path.is_file():
                problems.append(f"{source_id}: 缺少 {path}")
                continue
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            if digest != metadata["sha256"]:
                problems.append(f"{source_id}: SHA-256 不符，请使用索引对应的原版 PDF")
                continue
            document = fitz.open(path)
            documents[source_id] = document
            if len(document) != metadata["pages"]:
                problems.append(f"{source_id}: 页数应为 {metadata['pages']}，实际为 {len(document)}")
        for item in all_items:
            for side in ("question", "answer"):
                source_id = item[side + "_source"]
                if source_id not in sources:
                    problems.append(f"{item['id']}: 未知来源 {source_id}")
                    continue
                if source_id not in documents:
                    continue
                document = documents[source_id]
                crops = item[side + "_crops"]
                if not crops:
                    problems.append(f"{item['id']} {side}: 缺少裁切区域")
                for crop in crops:
                    page = crop["page"]
                    bbox = crop["bbox"]
                    if not isinstance(page, int) or not 1 <= page <= len(document):
                        problems.append(f"{item['id']} {side}: 页码越界 {page}")
                        continue
                    if len(bbox) != 4 or not all(math.isfinite(v) for v in bbox):
                        problems.append(f"{item['id']} {side}: 无效坐标 {bbox}")
                        continue
                    rect = fitz.Rect(bbox)
                    bounds = document[page - 1].rect + (-1, -1, 1, 1)
                    if rect.is_empty or not bounds.contains(rect):
                        problems.append(f"{item['id']} {side}: 裁切区域越界 {bbox}")
        if problems:
            raise ValueError("输入检查失败：\n" + "\n".join(problems))
    finally:
        for document in documents.values():
            document.close()
    return {"sources": len(sources), "counts": counts, "topics": len(TOPICS)}
