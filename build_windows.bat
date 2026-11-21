@echo off
setlocal
cd /d "%~dp0"
echo ==============================================
echo       COTIZEP - Generador EXE para Windows
echo ==============================================

where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Instala Python 3.12 y habilita Python Launcher.
  pause
  exit /b 1
)

if not exist ".venv_build\Scripts\python.exe" (
  py -3.12 -m venv .venv_build
  if errorlevel 1 goto error
)

call .venv_build\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto error
python -m pip install -r requirements.txt
if errorlevel 1 goto error
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name COTIZEP ^
  --collect-all mysql.connector ^
  --collect-all reportlab ^
  --add-data "database\sql;database\sql" ^
  main.py
if errorlevel 1 goto error

echo.
echo EJECUTABLE GENERADO: dist\COTIZEP.exe
echo Nota: MySQL Server 8.0+ debe estar instalado o accesible en la red.
pause
exit /b 0

:error
echo.
echo ERROR: No se pudo generar el ejecutable. Revisa el mensaje anterior.
pause
exit /b 1
