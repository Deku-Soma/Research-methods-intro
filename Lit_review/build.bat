@echo off
echo Building main.tex using latexmk...
latexmk -pdf -interaction=nonstopmode -shell-escape main.tex
if %ERRORLEVEL% equ 0 (
    echo Build successful!
) else (
    echo Build failed with error level %ERRORLEVEL%
)
pause
