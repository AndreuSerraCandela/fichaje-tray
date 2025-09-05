@echo off
echo Cerrando FichajeTray antes de la instalacion...
echo.

REM Intentar cerrar FichajeTray si está ejecutándose
tasklist /FI "IMAGENAME eq FichajeTray.exe" 2>NUL | find /I /N "FichajeTray.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo FichajeTray esta ejecutandose. Cerrandolo...
    taskkill /F /IM FichajeTray.exe /T
    timeout /t 3 /nobreak >NUL
    echo FichajeTray cerrado.
) else (
    echo FichajeTray no esta ejecutandose.
)

echo.
echo Ahora puedes ejecutar el instalador sin problemas.
echo Presiona cualquier tecla para continuar...
pause >NUL
