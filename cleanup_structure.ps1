# cleanup_structure.ps1 - 修复版
Write-Host "=== 开始清理项目结构 ===" -ForegroundColor Cyan
Write-Host "=" * 50

$deletedItems = @()

# 1. 删除重复的LabManager目录
if (Test-Path "LabManager") {
    Write-Host "删除重复的LabManager目录..." -ForegroundColor Yellow
    try {
        Remove-Item "LabManager" -Recurse -Force
        Write-Host "✅ 已删除: LabManager目录" -ForegroundColor Green
        $deletedItems += "LabManager目录"
    } catch {
        Write-Host "❌ 删除失败: LabManager目录" -ForegroundColor Red
    }
}

# 2. 删除重复的auth.py
if (Test-Path "app\auth.py") {
    Write-Host "删除重复的app\auth.py..." -ForegroundColor Yellow
    try {
        Remove-Item "app\auth.py" -Force
        Write-Host "✅ 已删除: app\auth.py" -ForegroundColor Green
        $deletedItems += "app\auth.py"
    } catch {
        Write-Host "❌ 删除失败: app\auth.py" -ForegroundColor Red
    }
}

# 3. 删除routes目录中的models.py
if (Test-Path "app\routes\models.py") {
    Write-Host "删除app\routes\models.py..." -ForegroundColor Yellow
    try {
        Remove-Item "app\routes\models.py" -Force
        Write-Host "✅ 已删除: app\routes\models.py" -ForegroundColor Green
        $deletedItems += "app\routes\models.py"
    } catch {
        Write-Host "❌ 删除失败: app\routes\models.py" -ForegroundColor Red
    }
}

# 4. 清理空的__pycache__目录
if (Test-Path "__pycache__") {
    Write-Host "清理__pycache__目录..." -ForegroundColor Yellow
    try {
        Remove-Item "__pycache__" -Recurse -Force
        Write-Host "✅ 已删除: __pycache__目录" -ForegroundColor Green
        $deletedItems += "__pycache__目录"
    } catch {
        Write-Host "❌ 删除失败: __pycache__目录" -ForegroundColor Red
    }
}

# 5. 清理重复的配置文件
$duplicateFiles = @(
    "organize_tests_final.py"
)

foreach ($file in $duplicateFiles) {
    if (Test-Path $file) {
        Write-Host "删除临时文件: $file..." -ForegroundColor Yellow
        try {
            Remove-Item $file -Force
            Write-Host "✅ 已删除: $file" -ForegroundColor Green
            $deletedItems += $file
        } catch {
            Write-Host "❌ 删除失败: $file" -ForegroundColor Red
        }
    }
}

Write-Host "`n" + "=" * 50
Write-Host "清理完成！" -ForegroundColor Green

if ($deletedItems.Count -gt 0) {
    Write-Host "已删除的项目:" -ForegroundColor Cyan
    foreach ($item in $deletedItems) {
        Write-Host "  - $item" -ForegroundColor Gray
    }
} else {
    Write-Host "没有需要清理的项目。" -ForegroundColor Yellow
}

Write-Host "`n当前项目结构:" -ForegroundColor Cyan
Get-ChildItem | ForEach-Object {
    if ($_.PSIsContainer) {
        Write-Host "📁 $($_.Name)" -ForegroundColor Blue
    } else {
        Write-Host "📄 $($_.Name)" -ForegroundColor Gray
    }
}