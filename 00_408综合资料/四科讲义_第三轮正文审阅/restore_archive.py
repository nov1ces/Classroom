#!/usr/bin/env python3
"""Reassemble the original review ZIP and verify every part and the result."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import zipfile


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(data)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description='校验三个分卷并还原完整 ZIP；不解压或修改正文。')
    parser.add_argument('--output', type=Path, help='可选：指定完整 ZIP 的输出路径')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    manifest = json.loads((folder / 'archive_parts.json').read_text(encoding='utf-8'))
    target = manifest['archive']
    output = args.output if args.output is not None else folder / target['name']
    if output.exists():
        if output.stat().st_size == target['bytes'] and fingerprint(output) == target['sha256']:
            print('完整 ZIP 已存在且 SHA-256 正确：' + str(output))
            return
        raise ValueError('输出文件已存在且与原包不符，请另选 --output 路径：' + str(output))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    digest = hashlib.sha256()
    total = 0
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix='.408-restore-', delete=False) as writer:
            temporary = Path(writer.name)
            for part in manifest['parts']:
                path = folder / part['name']
                part_digest = hashlib.sha256()
                size = 0
                with path.open('rb') as reader:
                    for data in iter(lambda: reader.read(1024 * 1024), b''):
                        part_digest.update(data)
                        digest.update(data)
                        writer.write(data)
                        size += len(data)
                if size != part['bytes'] or part_digest.hexdigest() != part['sha256']:
                    raise ValueError('分卷大小或 SHA-256 不符：' + part['name'])
                total += size
                print('分卷校验通过：' + part['name'])
        if total != target['bytes'] or digest.hexdigest() != target['sha256']:
            raise ValueError('合并结果与原完整包的大小或 SHA-256 不符')
        with zipfile.ZipFile(temporary) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise ValueError('ZIP CRC 校验失败：' + bad)
            count = len(archive.infolist())
        temporary.replace(output)
        temporary = None
        print('还原完成：' + str(output))
        print('SHA-256：' + target['sha256'])
        print('ZIP CRC 通过，共 ' + str(count) + ' 个文件。')
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print('还原失败：' + str(error), file=sys.stderr)
        sys.exit(1)
