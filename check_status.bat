@echo off
echo CHECKING GIT STATUS
git status -uno
echo -------------------
echo CHECKING LAST COMMIT
git log -1
echo -------------------
