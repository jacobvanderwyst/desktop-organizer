param(
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

# Desktop cleanup script for duplicate files
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "      DESKTOP DUPLICATE CLEANUP SCRIPT        " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN] MODE - No files will be deleted" -ForegroundColor Yellow
    Write-Host ""
}

$desktopPath = [Environment]::GetFolderPath("Desktop")
$foldersPath = Join-Path $desktopPath "Folders"

# Statistics
$totalFilesDeleted = 0
$totalSpaceSaved = 0

# Function to safely delete a folder
function Remove-FolderSafely {
    param(
        [string]$FolderPath,
        [bool]$IsDryRun
    )
    
    if (Test-Path $FolderPath) {
        $folderSize = (Get-ChildItem $FolderPath -Recurse | Measure-Object -Property Length -Sum).Sum
        if ($null -eq $folderSize) { $folderSize = 0 }
        $folderSizeMB = [math]::Round($folderSize / 1MB, 2)
        
        Write-Host "  [FOLDER] $FolderPath ($folderSizeMB MB)" -ForegroundColor Red
        
        if (-not $IsDryRun) {
            try {
                Remove-Item $FolderPath -Recurse -Force
                Write-Host "    [SUCCESS] Deleted successfully" -ForegroundColor Green
                $script:totalSpaceSaved += $folderSize
                $script:totalFilesDeleted += (Get-ChildItem $FolderPath -Recurse -File -ErrorAction SilentlyContinue).Count
            }
            catch {
                Write-Host "    [ERROR] Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        else {
            $fileCount = (Get-ChildItem $FolderPath -Recurse -File -ErrorAction SilentlyContinue).Count
            Write-Host "    [INFO] Would delete: $fileCount files, $folderSizeMB MB" -ForegroundColor Yellow
            $script:totalFilesDeleted += $fileCount
            $script:totalSpaceSaved += $folderSize
        }
    }
}

# Function to safely delete a file
function Remove-FileSafely {
    param(
        [string]$FilePath,
        [bool]$IsDryRun
    )
    
    if (Test-Path $FilePath) {
        $fileSize = (Get-Item $FilePath).Length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        
        Write-Host "  [FILE] $FilePath ($fileSizeMB MB)" -ForegroundColor Red
        
        if (-not $IsDryRun) {
            try {
                Remove-Item $FilePath -Force
                Write-Host "    [SUCCESS] Deleted successfully" -ForegroundColor Green
                $script:totalSpaceSaved += $fileSize
                $script:totalFilesDeleted += 1
            }
            catch {
                Write-Host "    [ERROR] Error: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        else {
            Write-Host "    [INFO] Would delete: $fileSizeMB MB" -ForegroundColor Yellow
            $script:totalFilesDeleted += 1
            $script:totalSpaceSaved += $fileSize
        }
    }
}

Write-Host "[GAMES] CLEANING KALYSKAH GAME DUPLICATES" -ForegroundColor Magenta
Write-Host "Keeping the most recent version in 'Other' folder..." -ForegroundColor White
Write-Host ""

# Remove Kalyskah duplicates (keep the one in "Other" folder)
$duplicateGamePaths = @(
    "$foldersPath\Other_1\kalyskah-legacy",
    "$foldersPath\Other_1\kalyskah-win", 
    "$foldersPath\Other_2\kalyskah-legacy",
    "$foldersPath\Other_2\kalyskah-win",
    "$foldersPath\Other_3\kalyskah-legacy",
    "$foldersPath\Other_3\kalyskah-win"
)

foreach ($path in $duplicateGamePaths) {
    Remove-FolderSafely -FolderPath $path -IsDryRun $DryRun
}

Write-Host ""
Write-Host "[SOFTWARE] CLEANING AITRACK SOFTWARE DUPLICATES" -ForegroundColor Magenta
Write-Host "Keeping the most recent version in 'Other' folder..." -ForegroundColor White
Write-Host ""

# Remove AITrack duplicates (keep the one in "Other" folder)
$duplicateAITrackPaths = @(
    "$foldersPath\Other_1\aitrack-v0.7.1",
    "$foldersPath\Other_2\aitrack-v0.7.1",
    "$foldersPath\Other_3\aitrack-v0.7.1"
)

foreach ($path in $duplicateAITrackPaths) {
    Remove-FolderSafely -FolderPath $path -IsDryRun $DryRun
}

Write-Host ""
Write-Host "[SETUP] CLEANING SETUP FILE DUPLICATES" -ForegroundColor Magenta
Write-Host "Keeping the most recent version in 'Other' folder..." -ForegroundColor White
Write-Host ""

# Remove duplicate setup files (keep the ones in "Other" folder)
$duplicateSetupFiles = @(
    "$foldersPath\Other_1\setup.ps1",
    "$foldersPath\Other_1\setupFiles.zip",
    "$foldersPath\Other_1\AudezeHQ_Installer_126.exe",
    "$foldersPath\Other_2\setup.ps1",
    "$foldersPath\Other_2\setupFiles.zip", 
    "$foldersPath\Other_2\AudezeHQ_Installer_126.exe",
    "$foldersPath\Other_3\setup.ps1",
    "$foldersPath\Other_3\setupFiles.zip",
    "$foldersPath\Other_3\AudezeHQ_Installer_126.exe"
)

foreach ($filePath in $duplicateSetupFiles) {
    Remove-FileSafely -FilePath $filePath -IsDryRun $DryRun
}

Write-Host ""
Write-Host "[SHORTCUTS] HANDLING DUPLICATE SHORTCUTS" -ForegroundColor Magenta
Write-Host "Removing duplicate Oracle VirtualBox shortcut from Work Tools (keeping in Coding Tools)..." -ForegroundColor White
Write-Host ""

# Remove duplicate Oracle VirtualBox shortcut from Work Tools (keep in Coding Tools)
$duplicateShortcut = "$desktopPath\Work Tools\Oracle VirtualBox.lnk"
Remove-FileSafely -FilePath $duplicateShortcut -IsDryRun $DryRun

Write-Host ""
Write-Host "[CLEANUP] CLEANING EMPTY FOLDERS" -ForegroundColor Magenta
Write-Host ""

# Check and remove empty Other_X folders
$otherFolders = @("Other_1", "Other_2", "Other_3")
foreach ($folderName in $otherFolders) {
    $folderPath = "$foldersPath\$folderName"
    if (Test-Path $folderPath) {
        $contents = Get-ChildItem $folderPath -Force
        if ($contents.Count -eq 0) {
            Write-Host "  [EMPTY] Empty folder: $folderPath" -ForegroundColor Yellow
            if (-not $DryRun) {
                Remove-Item $folderPath -Force
                Write-Host "    [SUCCESS] Removed empty folder" -ForegroundColor Green
            }
            else {
                Write-Host "    [INFO] Would remove empty folder" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "  [KEEP] Keeping $folderPath (contains $($contents.Count) items)" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "                   SUMMARY                     " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

$totalSpaceSavedMB = [math]::Round($totalSpaceSaved / 1MB, 2)
$totalSpaceSavedGB = [math]::Round($totalSpaceSaved / 1GB, 2)

if ($DryRun) {
    Write-Host "[PREVIEW] WOULD DELETE:" -ForegroundColor Yellow
    Write-Host "   Files: $totalFilesDeleted" -ForegroundColor Yellow
    Write-Host "   Space: $totalSpaceSavedMB MB ($totalSpaceSavedGB GB)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To actually delete these files, run:" -ForegroundColor White
    Write-Host "   .\cleanup_duplicates.ps1" -ForegroundColor Cyan
}
else {
    Write-Host "[COMPLETED] CLEANUP COMPLETED:" -ForegroundColor Green
    Write-Host "   Files deleted: $totalFilesDeleted" -ForegroundColor Green
    Write-Host "   Space saved: $totalSpaceSavedMB MB ($totalSpaceSavedGB GB)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your desktop is now organized with duplicates removed!" -ForegroundColor Green
}

Write-Host ""
Write-Host "[PRESERVED] PRESERVED FILES:" -ForegroundColor Green
Write-Host "   - Kalyskah games in 'Other' folder" -ForegroundColor White
Write-Host "   - AITrack software in 'Other' folder" -ForegroundColor White  
Write-Host "   - Setup files in 'Other' folder" -ForegroundColor White
Write-Host "   - Oracle VirtualBox shortcut in 'Coding Tools'" -ForegroundColor White
