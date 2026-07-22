@echo off
echo ===================================================
echo     Pushing code to GitHub for Support Analysis    
echo ===================================================
echo.
echo Make sure you have created an empty repository on GitHub named "Support-Analysis-System"
echo and you have Git installed.
echo.
pause

git add .
git commit -m "Enhance UI with animations, glassmorphism, and logos"
git remote add origin https://github.com/jchiran010/Support-Analysis-System.git
git branch -M main
git push -u origin main

echo.
echo ===================================================
echo     Push attempt complete. Check any errors above.
echo ===================================================
pause
