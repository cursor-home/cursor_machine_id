#!/bin/bash
#
# Cursor ID 更改工具 - Linux 版本
# 此脚本用于修改 Linux 上 Cursor 编辑器的机器标识符，创建新的身份标识
# 使用方法: ./linux_change_id.sh [可选的自定义机器ID]

# 配置文件路径 (Linux版本)
STORAGE_FILE="$HOME/.config/Cursor/User/globalStorage/storage.json"

# 检查必要命令
check_commands() {
    # 定义需要检查的命令列表
    local commands=("openssl" "uuidgen" "perl")
    for cmd in "${commands[@]}"; do
        # 检查每个命令是否存在于系统中
        if ! command -v "$cmd" &> /dev/null; then
            echo "错误: 未找到命令 '$cmd'. 请先安装必要的工具。"
            exit 1
        fi
    done
}


# 生成随机 ID（64位十六进制）
generate_random_id() {
    # 使用 openssl 生成随机十六进制字符串
    openssl rand -hex 32 || {
        echo "生成随机ID失败"
        exit 1
    }
}

# 生成随机 UUID
generate_random_uuid() {
    # 生成 UUID 并转换为小写
    uuidgen | tr '[:upper:]' '[:lower:]' || {
        echo "生成UUID失败"
        exit 1
    }
}

# 执行命令检查
check_commands

# 生成新的 IDs
# 如果提供了命令行参数，则使用它作为机器ID，否则生成随机ID
NEW_MACHINE_ID=${1:-$(generate_random_id)}
NEW_MAC_MACHINE_ID=$(generate_random_id)
NEW_DEV_DEVICE_ID=$(generate_random_uuid)

# 创建备份函数
backup_file() {
    if [ -f "$STORAGE_FILE" ]; then
        # 创建带时间戳的备份文件
        cp "$STORAGE_FILE" "${STORAGE_FILE}.backup_$(date +%Y%m%d_%H%M%S)" || {
            echo "创建备份失败"
            exit 1
        }
        echo "已创建备份文件"
    fi
}

# 确保配置文件的目录存在
mkdir -p "$(dirname "$STORAGE_FILE")" || {
    echo "创建目录失败"
    exit 1
}

# 创建配置文件备份
backup_file

# 如果配置文件不存在，创建新的空 JSON 对象
if [ ! -f "$STORAGE_FILE" ]; then
    echo "{}" > "$STORAGE_FILE" || {
        echo "创建配置文件失败"
        exit 1
    }
fi

# 检查文件是否可写
if [ ! -w "$STORAGE_FILE" ]; then
    echo "错误: 配置文件不可写"
    exit 1
fi

# 更新所有遥测 ID
# 使用 perl 进行正则表达式替换，因为它比 sed 更可靠地处理特殊字符
perl -i -pe 's/"telemetry\.machineId":\s*"[^"]*"/"telemetry.machineId": "'$NEW_MACHINE_ID'"/' "$STORAGE_FILE" || {
    echo "更新 machineId 失败"
    exit 1
}
perl -i -pe 's/"telemetry\.macMachineId":\s*"[^"]*"/"telemetry.macMachineId": "'$NEW_MAC_MACHINE_ID'"/' "$STORAGE_FILE" || {
    echo "更新 macMachineId 失败"
    exit 1
}
perl -i -pe 's/"telemetry\.devDeviceId":\s*"[^"]*"/"telemetry.devDeviceId": "'$NEW_DEV_DEVICE_ID'"/' "$STORAGE_FILE" || {
    echo "更新 devDeviceId 失败"
    exit 1
}

# 显示修改结果
echo "已成功修改 ID:"
echo "machineId: $NEW_MACHINE_ID"
echo "macMachineId: $NEW_MAC_MACHINE_ID"
echo "devDeviceId: $NEW_DEV_DEVICE_ID"
