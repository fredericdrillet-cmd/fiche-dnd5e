@echo off
setlocal EnableExtensions
rem ==================================================================
rem  Compilation de dist\Fiche_Personnage_DnD5E.exe (double-clic)
rem  - cherche Python : PATH, lanceur py, puis Anaconda / Miniconda
rem  - installe PyInstaller et PyQt6 si besoin, teste, compile, verifie
rem ==================================================================
cd /d "%~dp0"

set "PYEXE="
rem 1. Anaconda / Miniconda (active l'environnement : indispensable pour pip)
for %%D in ("%USERPROFILE%\anaconda3" "%USERPROFILE%\miniconda3" "%LOCALAPPDATA%\anaconda3" "%LOCALAPPDATA%\miniconda3" "%ProgramData%\anaconda3" "%ProgramData%\miniconda3" "%USERPROFILE%\Anaconda3" "C:\anaconda3" "C:\Anaconda3" "K:\anaconda3" "K:\Anaconda3") do (
    if not defined PYEXE if exist "%%~D\python.exe" (
        if exist "%%~D\Scripts\activate.bat" call "%%~D\Scripts\activate.bat" "%%~D"
        set "PYEXE=%%~D\python.exe"
    )
)
rem 2. Python dans le PATH
if not defined PYEXE (
    where python >nul 2>nul && set "PYEXE=python"
)
rem 3. Lanceur py de python.org
if not defined PYEXE (
    where py >nul 2>nul && set "PYEXE=py -3"
)
if not defined PYEXE (
    echo.
    echo Python est introuvable.
    echo  - Ouvrez "Anaconda Prompt" depuis le menu Demarrer,
    echo  - tapez :  cd /d "%~dp0"
    echo  - puis   :  python build_executable.py --installer
    echo.
    pause
    exit /b 1
)

echo Python utilise : %PYEXE%
%PYEXE% build_executable.py --installer %*
set "CODE=%ERRORLEVEL%"
echo.
if "%CODE%"=="0" (
    echo Termine : dist\Fiche_Personnage_DnD5E.exe
) else (
    echo La compilation a echoue [code %CODE%] : voir dist\journal_build.txt
)
pause
exit /b %CODE%
