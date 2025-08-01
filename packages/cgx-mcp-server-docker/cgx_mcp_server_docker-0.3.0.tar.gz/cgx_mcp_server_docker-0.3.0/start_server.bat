@echo off
REM MCP Docker Server Startup Script for Windows
REM Usage: start_server.bat [stdio|streamable-http] [port]

set TRANSPORT=%1
set PORT=%2

if "%TRANSPORT%"=="" set TRANSPORT=stdio
if "%PORT%"=="" set PORT=8080

echo Starting MCP Docker Server with transport: %TRANSPORT%

if "%TRANSPORT%"=="stdio" (
    python run_server.py --transport stdio
) else if "%TRANSPORT%"=="streamable-http" (
    echo Server will be available at http://localhost:%PORT%
    python run_server.py --transport streamable-http --host 0.0.0.0 --port %PORT%
) else if "%TRANSPORT%"=="http" (
    echo Server will be available at http://localhost:%PORT%
    python run_server.py --transport http --host 0.0.0.0 --port %PORT%
) else (
    echo Invalid transport. Use stdio, streamable-http, or http
    exit /b 1
)
