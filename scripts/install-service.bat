@echo off
REM =============================================================================
REM Land Intelligence System - Windows Service Installation Script (Batch Wrapper)
REM =============================================================================
REM This is a convenience wrapper for users who prefer Command Prompt over PowerShell.
REM It provides a simpler interface but delegates to the PowerShell script for
REM all actual operations.
REM
REM Prerequisites:
REM - PowerShell 5.1+ must be installed
REM - NSSM must be installed at C:\Program Files\NSSM\nssm.exe (or specify path)
REM - Python virtual environment must be created
REM - .env configuration file must exist
REM =============================================================================

setlocal enabledelayedexpansion

REM Default values
set "PROJECT_PATH=C:\Projects\land-intelligence-backend"
set "SERVICE_NAME=LandIntelligenceAPI"
set "NSSM_PATH=C:\Program Files\NSSM\nssm.exe"
set "SERVICE_PORT=8000"

echo.
echo ============================================================
echo Land Intelligence System - Service Management (Batch Wrapper)
echo ============================================================
echo.

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :show_usage
if /i "%~1"=="-install" goto :do_install
if /i "%~1"=="-uninstall" goto :do_uninstall
if /i "%~1"=="-start" goto :do_start
if /i "%~1"=="-stop" goto :do_stop
if /i "%~1"=="-restart" goto :do_restart
if /i "%~1"=="-status" goto :do_status
if /i "%~1"=="-project-path" (set "PROJECT_PATH=%~2" & shift & shift & goto :parse_args)
if /i "%~1"=="-service-name" (set "SERVICE_NAME=%~2" & shift & shift & goto :parse_args)
if /i "%~1"=="-nssm-path" (set "NSSM_PATH=%~2" & shift & shift & goto :parse_args)
if /i "%~1"=="-port" (set "SERVICE_PORT=%~2" & shift & shift & goto :parse_args)
if /i "%~1"=="-help" goto :show_usage
if /i "%~1"=="/?" goto :show_usage

REM If we get here, unknown argument
echo Unknown argument: %~1
goto :show_usage

:show_usage
echo Usage: %~nx0 ^<-action^> [options]
echo.
echo Available actions (required):
echo   -install              Install the Land Intelligence API service
echo   -uninstall            Remove the service
echo   -start                Start the service
echo   -stop                 Stop the service
echo   -restart              Restart the service
echo   -status               Show service status
echo.
echo Optional parameters:
echo   -project-path PATH    Path to project directory (default: %PROJECT_PATH%)
echo   -service-name NAME    Service name (default: %SERVICE_NAME%)
echo   -nssm-path PATH        Path to NSSM executable (default: %NSSM_PATH%)
echo   -port NUMBER           API port (default: %SERVICE_PORT%)
echo   -help                 Show this help message
echo.
echo Examples:
echo   %~nx0 -install
echo   %~nx0 -status
echo   %~nx0 -start -port 8000
echo.
exit /b 0

:do_install
echo Installing service via PowerShell...
powershell -ExecutionPolicy Bypass -File "%~dp0install-service.ps1" -Install -ProjectPath "%PROJECT_PATH%" -ServiceName "%SERVICE_NAME%" -NssmPath "%NSSM_PATH%" -ServicePort %SERVICE_PORT%
exit /b !ERRORLEVEL!

:do_uninstall
echo Uninstalling service via PowerShell...
powershell -ExecutionPolicy Bypass -File "%~dp0install-service.ps1" -Uninstall -ProjectPath "%PROJECT_PATH%" -ServiceName "%SERVICE_NAME%" -NssmPath "%NSSM_PATH%"
exit /b !ERRORLEVEL!

:do_start
echo Starting service via PowerShell...
powershell -ExecutionPolicy Bypass -File "%~dp0install-service.ps1" -Start -ProjectPath "%PROJECT_PATH%" -ServiceName "%SERVICE_NAME%" -NssmPath "%NSSM_PATH%" -ServicePort %SERVICE_PORT%
exit /b !ERRORLEVEL!

:do_stop
echo Stopping service via PowerShell...
powershell -ExecutionPolicy Bypass -File "%~dp0install-service.ps1" -Stop -ProjectPath "%PROJECT_PATH%" -ServiceName "%SERVICE_NAME%" -NssmPath "%NSSM_PATH%"
exit /b !ERRORLEVEL!

:do_restart
echo Restarting service via PowerShell...
powershell -ExecutionPolicy Bypass -File "%~dp0install-service.ps1" -Restart -ProjectPath "%PROJECT_PATH%" -ServiceName "%SERVICE_NAME%" -NssmPath "%NSSM_PATH%"
exit /b !ERRORLEVEL!

:do_status
echo Checking service status via PowerShell...
powershell -ExecutionPolicy Bypass -File "%~dp0install-service.ps1" -Status -ProjectPath "%PROJECT_PATH%" -ServiceName "%SERVICE_NAME%" -NssmPath "%NSSM_PATH%" -ServicePort %SERVICE_PORT%
exit /b !ERRORLEVEL!