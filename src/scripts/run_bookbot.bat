@echo off
cd /d "%~dp0"
cd ..\..
.\venv\Scripts\python.exe -m streamlit run src/ui/app.py
pause
