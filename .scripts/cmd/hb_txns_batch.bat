@echo off
setlocal

cd /d "C:\Users\taylo\VSCode_yayfalafels\financial-statements"
call "env\Scripts\activate.bat"
hb batch run --file C:\Users\taylo\shell_scripts\hb_batch_txns\txns.json 
set "EXIT_CODE=%ERRORLEVEL%"
pause
exit /b %EXIT_CODE%
