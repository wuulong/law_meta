#!/bin/bash

# 初始化計數器變數
execution_count=0


# 無限迴圈
while true; do
    # 每次迴圈將計數器加 1
    # (( ... )) 是 Bash 中進行算術運算的語法
    ((execution_count++))

    # 顯示當前時間和執行次數
    # date 命令用於獲取當前時間
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 第 ${execution_count} 次執行..."

    # 在這裡寫下你想要重複執行的命令或邏輯
    # 範例：
    ./auto_law_processing.sh
    # /path/to/your_executable

    # 加入延遲，避免無限快速執行
    sleep 60 # 暫停 60 秒
done
