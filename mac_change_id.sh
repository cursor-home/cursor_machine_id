#!/bin/bash
#
# Cursor ID 更改工具 - macOS 版本
# 此脚本用于修改 macOS 上 Cursor 编辑器的机器标识符，创建新的身份标识
# 使用方法: ./mac_change_id.sh [可选的自定义机器ID]

# 配置文件路径
STORAGE_FILE="$HOME/Library/Application Support/Cursor/User/globalStorage/storage.json"
MAIN_JS_FILE="/Applications/Cursor.app/Contents/Resources/app/out/main.js"

# 生成随机 ID（64位十六进制）
generate_random_id() {
    # 使用 openssl 生成随机十六进制字符串
    openssl rand -hex 32
}

# 生成随机 UUID
generate_random_uuid() {
    # 生成 UUID 并转换为小写
    uuidgen | tr '[:upper:]' '[:lower:]'
}

# 生成新的 IDs
# 如果提供了命令行参数，则使用它作为机器ID，否则生成随机ID
NEW_MACHINE_ID=${1:-$(generate_random_id)}
NEW_MAC_MACHINE_ID=$(generate_random_id)
NEW_DEV_DEVICE_ID=$(generate_random_uuid)

# 创建备份函数
backup_file() {
    if [ -f "$STORAGE_FILE" ]; then
        # 创建带时间戳的备份文件
        cp "$STORAGE_FILE" "${STORAGE_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
        echo "已创建 storage.json 备份文件"
    fi
}

# 确保目录存在
mkdir -p "$(dirname "$STORAGE_FILE")"

# 创建配置文件备份
backup_file

# 创建 main.js 备份
cp "$MAIN_JS_FILE" "${MAIN_JS_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
echo "已创建 main.js 备份文件"

# 如果配置文件不存在，创建新的 JSON
if [ ! -f "$STORAGE_FILE" ]; then
    echo "{}" > "$STORAGE_FILE"
fi

# 更新所有遥测 ID
# 使用 perl 进行正则表达式替换，因为它比 sed 更可靠地处理特殊字符
tmp=$(mktemp)
perl -i -pe 's/"telemetry\.machineId":\s*"[^"]*"/"telemetry.machineId": "'$NEW_MACHINE_ID'"/' "$STORAGE_FILE"
perl -i -pe 's/"telemetry\.macMachineId":\s*"[^"]*"/"telemetry.macMachineId": "'$NEW_MAC_MACHINE_ID'"/' "$STORAGE_FILE"
perl -i -pe 's/"telemetry\.devDeviceId":\s*"[^"]*"/"telemetry.devDeviceId": "'$NEW_DEV_DEVICE_ID'"/' "$STORAGE_FILE"

# 更新 main.js 文件
# 替换 ioreg 命令为 uuidgen 命令，这样每次启动 Cursor 时都会生成新的随机 UUID
# 而不是使用设备的硬件 UUID
perl -i -pe 's/ioreg -rd1 -c IOPlatformExpertDevice/UUID=\$(uuidgen | tr '\''[:upper:]'\'' '\''[:lower:]'\'');echo \\"IOPlatformUUID = \\"\$UUID\\";/g' "$MAIN_JS_FILE"

# 显示修改结果
echo "已成功修改 ID"
echo "machineId: $NEW_MACHINE_ID"
echo "macMachineId: $NEW_MAC_MACHINE_ID"
echo "devDeviceId: $NEW_DEV_DEVICE_ID"

# 检查替换是否成功
# 在修改后的文件中查找我们添加的代码片段
if grep -F 'darwin:"UUID=$(uuidgen' "$MAIN_JS_FILE" > /dev/null; then
    echo "main.js 文件修改成功"
else
    echo "警告: main.js 文件可能未被正确修改，请检查文件内容"
    echo "你可以从备份文件恢复: ${MAIN_JS_FILE}.backup_*"
fi