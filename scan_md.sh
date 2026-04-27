#!/bin/bash
# 扫描指定目录下所有包含中文的 *.md 文件，与 docs 目录下的 md 文件比对，
# 只显示未在 docs 目录下匹配到的文件（按"上级目录名/文件名"匹配）
# Usage: ./scan_md.sh [directory]
# Default: current directory

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="${SCRIPT_DIR}/../"

SCAN_DIR="${1:-.}"
MAX_DEPTH=5
DOCS_MAX_DEPTH=10
# 匹配中文字符范围 (CJK Unified Ideographs)
CN_PATTERN='[\x{4e00}-\x{9fff}]'

if [ ! -d "$SCAN_DIR" ]; then
    echo "Error: Directory '$SCAN_DIR' does not exist"
    exit 1
fi

if [ ! -d "$DOCS_DIR" ]; then
    echo "Error: Docs directory '$DOCS_DIR' does not exist"
    exit 1
fi

# 收集扫描目录下含中文的 md 文件（含符号链接）
SCAN_LIST=$(mktemp)
find "$SCAN_DIR" -maxdepth "$MAX_DEPTH" \( -name "*.md" -type f -o -name "*.md" -type l \) -exec grep -Pl "$CN_PATTERN" {} \; | sort > "$SCAN_LIST"

# 收集 docs 目录下所有 md 的 "上级目录名/文件名"（含符号链接），用于匹配比对
# 对于符号链接，额外解析真实路径的 "上级目录名/文件名" 也加入匹配集合
DOCS_KEYS=$(mktemp)
while IFS= read -r docpath; do
    # 文件自身的 key
    echo "$docpath" | awk -F/ '{print $(NF-1) "/" $NF}'
    # 如果是符号链接，追加解析真实路径的 key
    if [ -L "$docpath" ]; then
        realpath "$docpath" | awk -F/ '{print $(NF-1) "/" $NF}'
    fi
done < <(find "$DOCS_DIR" -maxdepth "$DOCS_MAX_DEPTH" \( -name "*.md" -type f -o -name "*.md" -type l \)) | sort -u > "$DOCS_KEYS"

echo "Scanning *.md with Chinese content in: $(cd "$SCAN_DIR" && pwd) (max depth: $MAX_DEPTH)"
echo "Docs directory: $(cd "$DOCS_DIR" && pwd)"
echo "----------------------------------------"

# 按"上级目录名/文件名"比对，显示未在 docs 中匹配到的文件
UNMATCHED=0
while IFS= read -r filepath; do
    key=$(echo "$filepath" | awk -F/ '{print $(NF-1) "/" $NF}')
    if ! grep -qxF "$key" "$DOCS_KEYS"; then
        realpath "$filepath"
        ((UNMATCHED++))
    fi
done < "$SCAN_LIST"

echo "----------------------------------------"
echo "Total: $UNMATCHED unmatched files (out of $(wc -l < "$SCAN_LIST") scanned)"

rm -f "$SCAN_LIST" "$DOCS_KEYS"
