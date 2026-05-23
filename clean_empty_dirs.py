#!/usr/bin/env python3
"""清理空目录工具 - 扫描指定目录，删除只包含空目录或忽略项的目录树"""

import argparse
import shutil
import sys
from pathlib import Path

IGNORE_FILES = {'.DS_Store'}


def is_empty_directory(dir_path, ignore_names=None):
    if not dir_path.is_dir() or dir_path.is_symlink():
        return False

    if ignore_names is None:
        ignore_names = set()

    try:
        items = list(dir_path.iterdir())
    except PermissionError:
        return False

    for item in items:
        if item.is_symlink():
            return False
        if item.is_file():
            if item.name not in IGNORE_FILES:
                return False
        if item.is_dir():
            if item.name in ignore_names:
                continue
            if not is_empty_directory(item, ignore_names):
                return False

    return True


def clean_empty_directories(root_path, max_depth=None, ignore_names=None):
    root_path = Path(root_path).resolve()

    if not root_path.is_dir():
        print(f"错误: {root_path} 不是有效目录")
        return 0

    if ignore_names is None:
        ignore_names = set()

    deleted_count = 0

    all_dirs = []
    stack = [(root_path, 0)]
    while stack:
        path, depth = stack.pop()
        if max_depth is not None and depth > max_depth:
            continue
        try:
            for item in path.iterdir():
                if item.is_dir() and not item.is_symlink():
                    if item.name in ignore_names:
                        continue
                    all_dirs.append(item)
                    stack.append((item, depth + 1))
        except PermissionError:
            pass

    all_dirs.sort(key=lambda x: len(x.parts), reverse=True)

    for dir_path in all_dirs:
        if dir_path.exists() and is_empty_directory(dir_path, ignore_names):
            try:
                shutil.rmtree(dir_path)
                print(f"已删除空目录: {dir_path}")
                deleted_count += 1
            except OSError as e:
                print(f"无法删除 {dir_path}: {e}")

    if is_empty_directory(root_path, ignore_names) and root_path != Path.cwd():
        try:
            shutil.rmtree(root_path)
            print(f"已删除空目录: {root_path}")
            deleted_count += 1
        except OSError as e:
            print(f"无法删除 {root_path}: {e}")

    return deleted_count


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='扫描目录，删除只包含空目录或忽略项的目录树'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='要扫描的目录（默认: 当前目录）',
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=None,
        help='最大扫描深度（层数）',
    )
    parser.add_argument(
        '--ignore', '-i',
        default='',
        help='忽略的目录名称，多个用逗号分隔（例: .git,.workbuddy）',
    )
    return parser.parse_args(args)


def main():
    args = parse_args()

    target_dir = Path(args.directory).resolve()
    max_depth = args.depth
    ignore_names = set(args.ignore.split(',')) if args.ignore else set()

    print(f"扫描目录: {target_dir}")
    if max_depth is not None:
        print(f"最大扫描深度: {max_depth} 层")
    if ignore_names:
        print(f"忽略目录名称: {', '.join(sorted(ignore_names))}")
    print("-" * 50)

    deleted = clean_empty_directories(target_dir, max_depth, ignore_names)

    print("-" * 50)
    print(f"清理完成，共删除 {deleted} 个空目录")


if __name__ == "__main__":
    main()
