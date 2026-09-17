#!/bin/bash

# 連想配列に配列を詰められないしsetもないししんどすぎる。

# REPO="../databases"
REPO="./tmp"

branches=($(git -C ${REPO} branch --list | sed 's/^[* ]*//'))
# echo ${branches[@]} #debug

declare -A commit_graph

# add HEAD and branches
# commit_stk=($(git -C ${REPO} rev-parse "HEAD" ${branches[@]}))
commit_stk=($(git -C ${REPO} rev-parse ${branches[@]}))
echo ${#commit_stk[@]} #debug
echo ${commit_stk[@]} #debug

while true; do
    current_commit="${commit_stk[-1]}"
    echo "${current_commit}"
    # next_commit=$(git -C ${REPO} rev-parse ${current_commit}^ 2>/dev/null)
    if [ $? -ne 0 ]; then
        break
    fi
    current_commit="${next_commit}"
done

# b3e0b13ad85a2d96e4916be3f92d0c721bbd5aa0
# 59c23a960f3abd3e83593e4607cc9b86c089bd6d
# 2372ecf345c9537fdcd440a1509545d297b7fea6
# a9c76251254b1ab5eb24d674a717912f8d74d708
# 841ada7c23f9a8295b704e5b9f2b8e9e54964f09
# 51bd11b4457b5ac74723d61fe02d5d9da85592dd
# 73de99a0e5299a458eff69a28f0c6c01001f90c4

