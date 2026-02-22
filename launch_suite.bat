@echo off

:: Open PowerShell instead of CMD, bypass execution policies, and keep it open
start powershell.exe -ExecutionPolicy Bypass -NoExit -File "C:\Users\Samue\Documents\projects\github\Extract-Scripts-mp4\launch_suite.ps1"

:: Close this CMD window immediately
exit
