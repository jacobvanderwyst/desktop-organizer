param(
    [switch]$DryRun = $false
)

# Desktop folder consolidation script
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "      DESKTOP FOLDER CONSOLIDATION SCRIPT     " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN] MODE - No files will be moved" -ForegroundColor Yellow
    Write-Host ""
}

$desktopPath = [Environment]::GetFolderPath("Desktop")
$foldersPath = Join-Path $desktopPath "Folders"

# Statistics
$totalFilesMoved = 0
$totalFoldersMoved = 0

# Function to safely move items
function Move-ItemSafely {
    param(
        [string]$SourcePath,
        [string]$DestinationPath,
        [bool]$IsDryRun,
        [string]$ItemType = "File"
    )
    
    $itemName = Split-Path $SourcePath -Leaf
    Write-Host "  [$ItemType] $itemName" -ForegroundColor Yellow
    Write-Host "       From: $SourcePath" -ForegroundColor Gray
    Write-Host "       To:   $DestinationPath" -ForegroundColor Gray
    
    if (-not $IsDryRun) {
        try {
            # Check if destination already exists
            if (Test-Path $DestinationPath) {
                $counter = 1
                $baseName = [System.IO.Path]::GetFileNameWithoutExtension($itemName)
                $extension = [System.IO.Path]::GetExtension($itemName)
                do {
                    $newName = "$baseName`_$counter$extension"
                    $DestinationPath = Join-Path (Split-Path $DestinationPath) $newName
                    $counter++
                } while (Test-Path $DestinationPath)
                Write-Host "       Renamed to: $(Split-Path $DestinationPath -Leaf)" -ForegroundColor Magenta
            }
            
            Move-Item $SourcePath $DestinationPath -Force
            Write-Host "       [SUCCESS] Moved" -ForegroundColor Green
            if ($ItemType -eq "File") {
                $script:totalFilesMoved++
            } else {
                $script:totalFoldersMoved++
            }
        }
        catch {
            Write-Host "       [ERROR] Failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "       [INFO] Would move here" -ForegroundColor Yellow
        if ($ItemType -eq "File") {
            $script:totalFilesMoved++
        } else {
            $script:totalFoldersMoved++
        }
    }
    Write-Host ""
}

# Check if Folders directory exists
if (-not (Test-Path $foldersPath)) {
    Write-Host "[INFO] No 'Folders' directory found. Nothing to consolidate." -ForegroundColor Green
    exit 0
}

Write-Host "[CONSOLIDATION] Moving content from nested 'Folders' to top-level categories..." -ForegroundColor Magenta
Write-Host ""

# Get all subdirectories in the Folders directory
$nestedCategories = Get-ChildItem $foldersPath -Directory

foreach ($nestedCategory in $nestedCategories) {
    $categoryName = $nestedCategory.Name
    $topLevelCategory = Join-Path $desktopPath $categoryName
    
    Write-Host "=== CATEGORY: $categoryName ===" -ForegroundColor Cyan
    
    # Create top-level category if it doesn't exist
    if (-not (Test-Path $topLevelCategory)) {
        Write-Host "[CREATE] Creating top-level folder: $categoryName" -ForegroundColor Green
        if (-not $DryRun) {
            New-Item -Path $topLevelCategory -ItemType Directory -Force | Out-Null
        }
    }
    
    # Get all items in the nested category
    $items = Get-ChildItem $nestedCategory.FullName -Force
    
    if ($items.Count -eq 0) {
        Write-Host "[EMPTY] No items to move" -ForegroundColor Yellow
        Write-Host ""
        continue
    }
    
    foreach ($item in $items) {
        $destinationPath = Join-Path $topLevelCategory $item.Name
        
        if ($item.PSIsContainer) {
            # Handle folders
            Move-ItemSafely -SourcePath $item.FullName -DestinationPath $destinationPath -IsDryRun $DryRun -ItemType "Folder"
        } else {
            # Handle files
            Move-ItemSafely -SourcePath $item.FullName -DestinationPath $destinationPath -IsDryRun $DryRun -ItemType "File"
        }
    }
}

Write-Host "=== CLEANUP ===" -ForegroundColor Cyan

# Remove empty nested categories
foreach ($nestedCategory in $nestedCategories) {
    if ((Get-ChildItem $nestedCategory.FullName -Force).Count -eq 0) {
        Write-Host "[REMOVE] Empty category: $($nestedCategory.Name)" -ForegroundColor Yellow
        if (-not $DryRun) {
            try {
                Remove-Item $nestedCategory.FullName -Force
                Write-Host "         [SUCCESS] Removed empty folder" -ForegroundColor Green
            }
            catch {
                Write-Host "         [ERROR] Failed to remove: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        else {
            Write-Host "         [INFO] Would remove empty folder" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "[KEEP] Category still has content: $($nestedCategory.Name)" -ForegroundColor Green
    }
}

# Remove the Folders directory if empty
if ((Get-ChildItem $foldersPath -Force).Count -eq 0) {
    Write-Host "[REMOVE] Empty 'Folders' directory" -ForegroundColor Yellow
    if (-not $DryRun) {
        try {
            Remove-Item $foldersPath -Force
            Write-Host "         [SUCCESS] Removed 'Folders' directory" -ForegroundColor Green
        }
        catch {
            Write-Host "         [ERROR] Failed to remove: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "         [INFO] Would remove 'Folders' directory" -ForegroundColor Yellow
    }
}
else {
    Write-Host "[KEEP] 'Folders' directory still has content" -ForegroundColor Green
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "                   SUMMARY                     " -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[PREVIEW] WOULD MOVE:" -ForegroundColor Yellow
    Write-Host "   Files: $totalFilesMoved" -ForegroundColor Yellow
    Write-Host "   Folders: $totalFoldersMoved" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To actually consolidate folders, run:" -ForegroundColor White
    Write-Host "   .\consolidate_folders.ps1" -ForegroundColor Cyan
}
else {
    Write-Host "[COMPLETED] CONSOLIDATION COMPLETED:" -ForegroundColor Green
    Write-Host "   Files moved: $totalFilesMoved" -ForegroundColor Green
    Write-Host "   Folders moved: $totalFoldersMoved" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your desktop now has a single, clean organizational structure!" -ForegroundColor Green
}
Write-Host ""