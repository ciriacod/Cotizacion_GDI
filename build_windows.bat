@echo off
setlocal
cd /d "%~dp0"
echo ==============================================
echo   JP Cotiza - Generador de ejecutable Windows
echo ==============================================
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Instala Python 3.11 o superior y habilita Python Launcher.
  pause
  exit /b 1
)
py -3 -m venv .venv_build
call .venv_build\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto error
pip install -r requirements.txt
if errorlevel 1 goto error
pyinstaller --noconfirm --clean --onefile --windowed --name JP_Cotiza --collect-all mysql.connector --collect-all reportlab --add-data "database\sql;database\sql" main.py
if errorlevel 1 goto error
echo.
echo EJECUTABLE GENERADO: dist\JP_Cotiza.exe
echo Copia el archivo EXE a la PC destino. La primera ejecucion solicitara conexion MySQL.
pause
exit /b 0
:error
echo.
echo ERROR: No se pudo generar el ejecutable. Revisa el mensaje anterior.
pause
exit /b 1
