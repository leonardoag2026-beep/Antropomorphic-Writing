#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ -z "$LLM_API_KEY" ]; then
    echo "❌ Define LLM_API_KEY primeiro:"
    echo "   export LLM_API_KEY=\"sk-...\""
    exit 1
fi

if [ $# -ge 1 ]; then
    INPUT="$*"
elif [ ! -t 0 ]; then
    INPUT=$(cat)
else
    echo "Uso: $0 \"texto para humanizar\""
    echo "   ou: echo \"texto\" | $0"
    exit 1
fi

export LLM_BASE_URL="${LLM_BASE_URL:-https://opencode.ai/zen/go/v1}"
export LLM_MODEL="${LLM_MODEL:-deepseek-v4-flash}"

.venv/bin/python -m src.standard.pipeline \
    --input <(echo "$INPUT") \
    --verbose
