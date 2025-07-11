Set-Location "G:\MyaProject\mya_sdf_Tools"

Write-Host "=== Git Status ===" -ForegroundColor Green
git status

Write-Host "`n=== Adding all files ===" -ForegroundColor Green
git add .

Write-Host "`n=== Committing changes ===" -ForegroundColor Green
git commit -m "Initial commit: SDF Tools for anime face rendering"

Write-Host "`n=== Pushing main branch to GitHub ===" -ForegroundColor Green
git push -u origin main

Write-Host "`n=== Pushing develop branch to GitHub ===" -ForegroundColor Green
git push -u origin develop

Write-Host "`n=== Final status ===" -ForegroundColor Green
git status
git branch -a

Write-Host "`n=== Done ===" -ForegroundColor Green
