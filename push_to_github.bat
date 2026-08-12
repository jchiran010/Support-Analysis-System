@echo off
echo ===================================================
echo     Pushing code to GitHub for Support Analysis    
echo ===================================================
echo.
echo Checking Git remote configuration...
git remote | findstr "^origin$" >nul
if %errorlevel% neq 0 (
    echo Adding origin remote...
    git remote add origin https://github.com/jchiran010/Support-Analysis-System.git
) else (
    echo Setting origin remote URL...
    git remote set-url origin https://github.com/jchiran010/Support-Analysis-System.git
)

echo.
echo Staging all changes...
git add .

echo.
echo Committing changes...
git commit -m "Feature: modularize backend structure, add models, routes, services, templates, and install VS Code extensions"

echo.
echo Pushing to GitHub main branch...
git branch -M main
git push -u origin main

echo.
echo ===================================================
echo     Push attempt complete. Check any errors above.
echo ===================================================
pause
