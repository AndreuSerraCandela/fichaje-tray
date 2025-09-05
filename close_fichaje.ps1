Write-Host "Cerrando FichajeTray antes de la instalación..." -ForegroundColor Green
Write-Host ""

# Verificar si FichajeTray está ejecutándose
$processes = Get-Process -Name "FichajeTray" -ErrorAction SilentlyContinue

if ($processes) {
    Write-Host "FichajeTray está ejecutándose. Cerrando..." -ForegroundColor Yellow
    
    try {
        # Intentar cerrar de forma amigable primero
        $processes | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        
        # Verificar si se cerró
        $remaining = Get-Process -Name "FichajeTray" -ErrorAction SilentlyContinue
        if ($remaining) {
            Write-Host "Cerrando procesos restantes..." -ForegroundColor Red
            $remaining | Stop-Process -Force
        }
        
        Write-Host "FichajeTray cerrado exitosamente." -ForegroundColor Green
    }
    catch {
        Write-Host "Error al cerrar FichajeTray: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "FichajeTray no está ejecutándose." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Ahora puedes ejecutar el instalador sin problemas." -ForegroundColor Green
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
