@echo off
setlocal EnableDelayedExpansion

:: Cursor ID 更改工具 - Windows 批处理版本
:: 此脚本用于修改 Windows 上 Cursor 编辑器的机器标识符，创建新的身份标识
:: 使用方法: 双击运行此批处理文件

:: 设置配置文件路径
set "STORAGE_FILE=%APPDATA%\Cursor\User\globalStorage\storage.json"

echo 开始运行脚本...
echo 目标文件路径: %STORAGE_FILE%

:: 生成正确格式的随机 ID
:: 生成 machineId (40字符十六进制)
powershell -Command "$bytes = New-Object Byte[] 32; (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); -join ($bytes | ForEach-Object { $_.ToString('x2') })" > "%TEMP%\guid1.txt"
if errorlevel 1 goto :error
set /p NEW_MACHINE_ID=<"%TEMP%\guid1.txt"

:: 生成 macMachineId (40字符十六进制)
powershell -Command "$bytes = New-Object Byte[] 32; (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); -join ($bytes | ForEach-Object { $_.ToString('x2') })" > "%TEMP%\guid2.txt"
if errorlevel 1 goto :error
set /p NEW_MAC_MACHINE_ID=<"%TEMP%\guid2.txt"

:: 生成 sqmId (带大括号的大写 UUID)
powershell -Command "$guid = [guid]::NewGuid(); '{' + $guid.ToString().ToUpper() + '}'" > "%TEMP%\guid3.txt"
if errorlevel 1 goto :error
set /p NEW_SQM_ID=<"%TEMP%\guid3.txt"

:: 生成 devDeviceId (标准 UUID 格式)
powershell -Command "[guid]::NewGuid().ToString()" > "%TEMP%\guid4.txt"
if errorlevel 1 goto :error
set /p NEW_DEV_DEVICE_ID=<"%TEMP%\guid4.txt"

:: 清理临时文件
del "%TEMP%\guid1.txt" "%TEMP%\guid2.txt" "%TEMP%\guid3.txt" "%TEMP%\guid4.txt"

:: 创建备份
if exist "%STORAGE_FILE%" (
    copy "%STORAGE_FILE%" "%STORAGE_FILE%.backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul
)

:: 创建并执行更新脚本
:: 使用 PowerShell 进行 JSON 处理更可靠
(
    echo $ErrorActionPreference = 'Stop'
    echo try {
    echo     $json = Get-Content '%STORAGE_FILE%' -Raw
    echo     $json = $json -replace '"telemetry\.machineId"\s*:\s*"[^"]*"', '"telemetry.machineId": "%NEW_MACHINE_ID%"'
    echo     $json = $json -replace '"telemetry\.macMachineId"\s*:\s*"[^"]*"', '"telemetry.macMachineId": "%NEW_MAC_MACHINE_ID%"'
    echo     $json = $json -replace '"telemetry\.sqmId"\s*:\s*"[^"]*"', '"telemetry.sqmId": "%NEW_SQM_ID%"'
    echo     $json = $json -replace '"telemetry\.devDeviceId"\s*:\s*"[^"]*"', '"telemetry.devDeviceId": "%NEW_DEV_DEVICE_ID%"'
    echo     $json ^| Set-Content '%STORAGE_FILE%' -NoNewline
    echo } catch {
    echo     Write-Host "Error: $($_.Exception.Message)"
    echo     exit 1
    echo }
) > "%TEMP%\update_json.ps1"

:: 以绕过执行策略的方式运行 PowerShell 脚本
powershell -ExecutionPolicy Bypass -File "%TEMP%\update_json.ps1"
if errorlevel 1 (
    del "%TEMP%\update_json.ps1"
    goto :error
)

:: 删除临时 PowerShell 脚本
del "%TEMP%\update_json.ps1"

echo 操作成功完成！
goto :end

:error
echo 脚本执行出错！
echo 请确保 Cursor 编辑器已关闭且您有足够的文件访问权限。

:end
pause