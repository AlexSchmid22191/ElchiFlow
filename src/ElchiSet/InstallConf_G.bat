@echo off
:: --- Set target folder ---
set "targetDir=%APPDATA%\ElchWorks\ElchiGas"

:: --- Create folder if it doesn't exist ---
if not exist "%targetDir%" (
    mkdir "%targetDir%"
)

:: --- Define config file path ---
set "configFile=%targetDir%\config.yaml"

:: --- Create the config file with default contents ---
(
echo # Configuration for ElchiGas
echo device:
echo   type: Ventolino
echo   port: COMXY
echo 1:
echo   1: 0.0
echo   2: 0.0
echo   3: 0.0
echo   4: 0.0
echo 2:
echo   1: 20.5
echo   2: 35.0
echo   3: 55.5
echo   4: 75.0

) > "%configFile%"

echo Config file created at "%configFile%"
exit /b 0