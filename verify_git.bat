@echo off
echo === BRANCH ===
git branch --show-current
echo === STATUS ===
git status -uno
echo === LOG ===
git log -1
