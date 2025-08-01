#!/usr/bin/env bash

# 执行任务
runTask="colordove_auto start"
count=`ps -ef | grep "$runTask" | grep -v "grep" | wc -l`
if [[ $count -le 0 ]]; then
    echo $runTask
    $runTask > /dev/null 2>&1 &
fi