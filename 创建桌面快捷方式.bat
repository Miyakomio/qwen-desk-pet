@echo off
setlocal
cd /d "%~dp0"
set "TARGET=%CD%\start_pet.bat"
set "WORKDIR=%CD%"
set "SHORTCUT=%USERPROFILE%\Desktop\InoriPet.lnk"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%WORKDIR%'; $s.IconLocation='shell32.dll,21'; $s.Description='Inori-chan Desktop Pet'; $s.Save()"
echo Created desktop shortcut: %SHORTCUT%
pause
