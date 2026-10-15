"""Build the book from core sources and separately configured reference PDFs."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from config import ROOT, BUILD, OUT, validate_inputs


def run(command, env, log_name):
    log = BUILD / log_name
    with log.open("w", encoding="utf-8") as stream:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        tail = "\n".join(log.read_text(encoding="utf-8", errors="replace").splitlines()[-30:])
        raise RuntimeError(f"步骤失败，日志：{log}\n{tail}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, help="PDF 路径配置，默认 sources.local.json 或示例配置")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="检查所有原 PDF 的版本、页码及裁切坐标")
    mode.add_argument("--review-only", action="store_true", help="只构建知识回顾 PDF，无需参考 PDF")
    mode.add_argument("--verify-only", action="store_true", help="校验 build 目录中已构建的完整 PDF")
    args = parser.parse_args()
    if args.sources:
        os.environ["PDF_SOURCES_CONFIG"] = str(args.sources.expanduser().resolve())
    BUILD.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("XDG_CACHE_HOME", str(BUILD / "cache"))
    env.setdefault("TEXMFVAR", str(BUILD / "texmf-var"))
    env.setdefault("TEXMFCONFIG", str(BUILD / "texmf-config"))
    env["PYTHONUNBUFFERED"] = "1"
    if args.verify_only:
        print("校验已有 PDF…", flush=True)
        run([sys.executable, str(ROOT / "verify_pdf.py")], env, "verify.log")
        print((BUILD / "final_validation.json").read_text(encoding="utf-8"))
        return
    if not args.review_only:
        print("检查题目索引和外部 PDF…", flush=True)
        print(json.dumps(validate_inputs(), ensure_ascii=False), flush=True)
    if args.check:
        return
    if not shutil.which("xelatex"):
        raise RuntimeError("未找到 xelatex；请按 README 安装 TeX Live 和中文字体")
    print("排版知识回顾…", flush=True)
    run([sys.executable, str(ROOT / "build_review.py")], env, "review-source.log")
    for number in (1, 2):
        run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(BUILD), str(BUILD / "review.tex")],
            env, f"review-pass-{number}.log")
    if args.review_only:
        print(f"知识回顾已生成：{BUILD / 'review.pdf'}")
        return
    print("生成页眉字体并拼版题目与解析…", flush=True)
    run([sys.executable, str(ROOT / "subset_header_font.py")], env, "font.log")
    run([sys.executable, str(ROOT / "compose_book.py")], env, "compose.log")
    print("检查全部问答链接、目录与页面渲染…", flush=True)
    run([sys.executable, str(ROOT / "verify_pdf.py")], env, "verify.log")
    print((BUILD / "final_validation.json").read_text(encoding="utf-8"))
    print(f"构建完成：{OUT}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
