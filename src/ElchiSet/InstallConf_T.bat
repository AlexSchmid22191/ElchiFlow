@echo off
:: --- Set target folder ---
set "targetDir=%APPDATA%\ElchWorks\ElchiTrigger"

:: --- Create folder if it doesn't exist ---
if not exist "%targetDir%" (
    mkdir "%targetDir%"
)

:: --- Define config file path ---
set "configFile=%targetDir%\config.yaml"

:: --- Create the config file with default contents ---
(
echo # Configuration for ElchiTrigger
echo device:
echo   type: Omni Trigger
echo   port: COMXY
echo 1:
echo   1: 0
echo   2: 0
echo   3: 0
echo   4: 0
echo 2:
echo   1: 1
echo   2: 1
echo   3: 1
echo   4: 1

) > "%configFile%"

echo Config file created at "%configFile%"
exit /b 0