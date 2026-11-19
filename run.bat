@echo off
rem Opens the car store website. The site itself runs hidden in the background.
rem   run.bat         open the website
rem   run.bat admin   open the admin panel
rem   run.bat stop    stop the background site
cd /d "%~dp0"
if /i "%~1"=="admin" (start "" ".venv\Scripts\pythonw.exe" launcher.pyw --admin & exit /b)
if /i "%~1"=="stop"  (start "" ".venv\Scripts\pythonw.exe" launcher.pyw --stop  & exit /b)
start "" ".venv\Scripts\pythonw.exe" launcher.pyw
