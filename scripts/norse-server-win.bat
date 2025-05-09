@echo off
setlocal EnableDelayedExpansion
REM Server configurations
IF NOT DEFINED NORSE_SERVER_HOST (
    set HOST=127.0.0.1
) ELSE (
    set HOST=%NORSE_SERVER_HOST%
)

IF NOT DEFINED NORSE_SERVER_PORT (
    set PORT=11428
) ELSE (
    set PORT=%NORSE_SERVER_PORT%
)

REM Compute arguments
:parse_args
if "%~1"=="" goto end_parse_args
if "%~1"=="-h" (
    set "HOST=%2"
    shift
) else if "%~1"=="-p" (
    set "PORT=%2"
    shift
) else if "%~1"=="start" (
    set "COMMAND=start"
) else if "%~1"=="help" (
    set "COMMAND=help"
)

shift
goto parse_args

:end_parse_args

echo HOST=%HOST%
echo PORT=%PORT%


if "%COMMAND%"=="start" (
    goto start
) else if "%COMMAND%"=="help" (
    goto usage
) else (
    echo Invalid command! Use: start, help
)

REM Function: start
:start
echo Starting server on %HOST%:%PORT%
waitress-serve --host=%HOST% --port=%PORT% norse_server:app
goto :eof

REM Function: usage
:usage
echo Usage: norse-server-win start^| help [-h ^<HOST^>][-p ^<PORT^>]
echo.
echo Commands:
echo    start      Starts the Python server with waitress on the specified host and port
echo    help       Displays this help message
goto :eof

endlocal
