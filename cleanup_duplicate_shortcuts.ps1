param(
    [switch]$DryRun = $false
)

# Desktop duplicate shortcuts cleanup script
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "    DUPLICATE SHORTCUTS CLEANUP SCRIPT        " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN] MODE - No files will be deleted" -ForegroundColor Yellow
    Write-Host ""
}

$desktopPath = [Environment]::GetFolderPath("Desktop")

# List of shortcuts that have _1 duplicates
$duplicateShortcuts = @(
    "Cisco Jabber_1.lnk",
    "EA_1.lnk", 
    "Firefox_1.lnk",
    "Google Chrome_1.lnk",
    "Microsoft Edge_1.lnk", 
    "NVIDIA App_1.lnk",
    "Steam_1.lnk",
    "Stream Deck_1.lnk",
    "TeamViewer_1.lnk",
    "TrackIR_1.lnk",
    "Wireshark_1.lnk"
)

$totalDeleted = 0
$deletedShortcuts = @()

Write-Host "[CLEANUP] Removing duplicate shortcuts (keeping original names)..." -ForegroundColor Magenta
Write-Host ""

foreach ($shortcutName in $duplicateShortcuts) {
    # Find the duplicate shortcut
    $duplicateShortcut = Get-ChildItem -Path $desktopPath -Recurse -Filter $shortcutName -ErrorAction SilentlyContinue
    
    if ($duplicateShortcut) {
        $originalName = $shortcutName -replace '_1\.lnk$', '.lnk'
        $originalShortcut = Get-ChildItem -Path $desktopPath -Recurse -Filter $originalName -ErrorAction SilentlyContinue
        
        if ($originalShortcut) {
            Write-Host "  [DUPLICATE] $($duplicateShortcut.FullName)" -ForegroundColor Red
            Write-Host "              Original: $($originalShortcut.FullName)" -ForegroundColor Green
            
            if (-not $DryRun) {
                try {
                    Remove-Item $duplicateShortcut.FullName -Force
                    Write-Host "              [SUCCESS] Deleted duplicate" -ForegroundColor Green
                    $totalDeleted++
                    $deletedShortcuts += $originalName -replace '\.lnk$', ''
                }
                catch {
                    Write-Host "              [ERROR] Failed to delete: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
            else {
                Write-Host "              [INFO] Would delete duplicate" -ForegroundColor Yellow
                $totalDeleted++
                $deletedShortcuts += $originalName -replace '\.lnk$', ''
            }
        }
        else {
            Write-Host "  [WARNING] Found $shortcutName but no original version exists!" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "                   SUMMARY                     " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[PREVIEW] WOULD DELETE $totalDeleted duplicate shortcuts:" -ForegroundColor Yellow
}
else {
    Write-Host "[COMPLETED] DELETED $totalDeleted duplicate shortcuts:" -ForegroundColor Green
}

Write-Host ""
foreach ($shortcut in $deletedShortcuts) {
    if ($DryRun) {
        Write-Host "   - Would remove: $shortcut`_1 (keeping: $shortcut)" -ForegroundColor Yellow
    }
    else {
        Write-Host "   - Removed: $shortcut`_1 (kept: $shortcut)" -ForegroundColor Green
    }
}

Write-Host ""
if ($DryRun) {
    Write-Host "To actually delete these shortcuts, run:" -ForegroundColor White
    Write-Host "   .\cleanup_duplicate_shortcuts.ps1" -ForegroundColor Cyan
}
else {
    Write-Host "Your desktop shortcuts are now cleaned up!" -ForegroundColor Green
    Write-Host "All applications now have single, clean shortcut names." -ForegroundColor White
}
Write-Host ""