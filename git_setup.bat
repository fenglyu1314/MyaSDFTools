@echo off
cd /d "G:\MyaProject\mya_sdf_Tools"
echo "=== Git Status ==="
git status
echo.
echo "=== Adding remote origin ==="
git remote add origin https://github.com/fenglyu1314/MyaSDFTools.git
echo.
echo "=== Adding all files ==="
git add .
echo.
echo "=== Committing changes ==="
git commit -m "Initial commit: SDF Tools for anime face rendering"
echo.
echo "=== Pushing to GitHub ==="
git push -u origin main
echo.
echo "=== Done ==="
pause
