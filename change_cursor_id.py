#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Cursor ID 更改工具 - Python 版本
# 此脚本用于修改 Cursor 编辑器的机器标识符，创建新的身份标识
# 适用于 Windows、macOS 和 Linux 平台
# 通过修改这些 ID，可以让 Cursor 认为这是一个全新的安装，重置使用统计和追踪

# 导入 Python 2.x 中的 Python 3.x 风格的 print 函数，使代码在 Python 2 和 Python 3 中都兼容
from __future__ import print_function
# 导入操作系统模块，用于文件和目录操作，如路径拼接、创建目录等
import os
# 导入系统模块，用于访问与 Python 解释器交互的变量和函数，如退出程序等
import sys
# 导入 JSON 模块，用于处理 JSON 格式的数据，读写配置文件
import json
# 导入 UUID 模块，用于生成唯一标识符，创建随机 ID
import uuid
# 导入文件操作模块，用于高级文件操作如复制文件并保留元数据
import shutil
# 导入平台模块，用于获取当前运行系统的信息，以便执行平台特定的操作
import platform
# 导入正则表达式模块，用于在文本中进行模式匹配和替换
import re
# 从 datetime 模块导入 datetime 类，用于处理日期和时间，生成带时间戳的备份文件名
from datetime import datetime
# 导入错误码模块，用于处理系统错误码，特别是处理文件操作时的异常
import errno

# 定义一个函数，用于获取不同操作系统下 Cursor 编辑器的配置文件路径
def get_storage_path():
    """获取 Cursor 配置文件 storage.json 的平台特定路径"""
    # 获取当前操作系统名称并转换为小写，用于后续的条件判断
    system = platform.system().lower()
    # 获取用户主目录路径，展开 '~' 符号为实际路径
    home = os.path.expanduser('~')
    
    # 如果当前系统是 Windows
    if system == 'windows':
        # Windows 平台下配置文件存储在 APPDATA 环境变量指定的目录中
        # 返回拼接后的完整路径
        return os.path.join(os.getenv('APPDATA'), 'Cursor', 'User', 'globalStorage', 'storage.json')
    # 如果当前系统是 macOS（darwin 是 macOS 的内核名称）
    elif system == 'darwin':
        # macOS 平台下配置文件存储在用户的应用支持目录中
        # 返回拼接后的完整路径
        return os.path.join(home, 'Library', 'Application Support', 'Cursor', 'User', 'globalStorage', 'storage.json')
    # 如果是其他系统（默认认为是 Linux）
    else:
        # Linux 平台下配置文件存储在用户主目录的 .config 目录中
        # 返回拼接后的完整路径
        return os.path.join(home, '.config', 'Cursor', 'User', 'globalStorage', 'storage.json')

# 定义一个函数，用于获取不同操作系统下 Cursor 编辑器的 main.js 文件路径
def get_main_js_path():
    """获取 Cursor 的 main.js 文件的平台特定路径，该文件需要被修改以防止硬件标识符跟踪"""
    # 获取当前操作系统名称并转换为小写，用于后续的条件判断
    system = platform.system().lower()
    
    # 如果当前系统是 macOS
    if system == 'darwin':
        # macOS 平台下 main.js 文件位于应用程序包内的固定位置
        # 返回 macOS 下的 main.js 文件绝对路径
        return '/Applications/Cursor.app/Contents/Resources/app/out/main.js'
    # 如果当前系统是 Windows
    elif system == 'windows':
        # Windows 平台下 main.js 文件位于程序安装目录中
        # 获取 Windows 本地应用数据目录路径，此处使用 LOCALAPPDATA 而非 USERPROFILE
        user_profile = os.getenv('LOCALAPPDATA')
        # 如果获取环境变量失败或路径不存在
        if not user_profile:
            # 返回 None 表示路径不可用
            return None
        # 拼接并返回 Windows 下的 main.js 文件完整路径
        return os.path.join(user_profile, 'Programs', 'cursor', 'resources', 'app', 'out', 'main.js')
    # 如果不是上述支持的系统（Linux 下暂不支持修改 main.js）
    return None

# 定义一个函数，用于生成 64 位的随机十六进制标识符
def generate_random_id():
    """生成随机 ID (64位十六进制)，通过组合两个 UUID 创建，用于替换机器标识符"""
    # 生成一个 UUID，获取其十六进制表示（不带连字符的32个字符）
    # 再生成另一个 UUID，获取其十六进制表示，并将两者连接
    # 最终得到一个 64 字符的随机十六进制字符串
    return uuid.uuid4().hex + uuid.uuid4().hex

# 定义一个函数，用于生成标准格式的 UUID 字符串
def generate_uuid():
    """生成标准 UUID 字符串，用于作为设备标识符"""
    # 生成一个随机 UUID 对象并转换为字符串格式（带连字符的标准 UUID 格式）
    # 例如：'123e4567-e89b-12d3-a456-426655440000'
    return str(uuid.uuid4())

# 定义一个函数，用于创建文件的备份，防止修改出错导致文件损坏
def backup_file(file_path):
    """创建指定文件的带时间戳的备份，防止修改出错后无法恢复原始文件"""
    # 检查指定的文件是否存在，避免尝试备份不存在的文件
    if os.path.exists(file_path):
        # 创建备份文件路径，格式为：原文件路径.backup_年月日_时分秒
        backup_path = '{}.backup_{}'.format(
            # 原始文件的完整路径
            file_path,
            # 获取当前时间并格式化为易读的时间戳
            datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        # 复制文件到备份路径，使用 copy2 保留所有元数据信息（如文件权限、创建时间等）
        shutil.copy2(file_path, backup_path)
        # 打印备份成功的消息，显示备份文件的路径
        print('已创建备份文件:', backup_path)

# 定义一个函数，用于确保目录存在，如果不存在则创建
def ensure_dir_exists(path):
    """确保目录存在，如果不存在则创建该目录及其所有父目录（兼容 Python 2/3）"""
    # 检查指定的路径是否已经存在
    if not os.path.exists(path):
        # 尝试创建目录，可能会遇到并发问题（其他进程同时创建）
        try:
            # 递归创建目录及其所有父目录
            os.makedirs(path)
        # 捕获操作系统相关的错误
        except OSError as e:
            # 处理目录已存在的竞争条件（在检查和创建之间可能已被其他进程创建）
            # 如果错误不是"文件已存在"错误，则重新抛出异常
            if e.errno != errno.EEXIST:
                # 重新抛出异常，因为这是一个无法处理的错误
                raise

# 定义一个函数，用于修改 main.js 文件，使其使用随机 ID 而非硬件 ID
def update_main_js(file_path):
    """
    修改 main.js 文件以使用随机生成的机器 ID 而非基于硬件的 ID。
    这可以防止 Cursor 使用硬件标识符进行遥测/跟踪。
    """
    # 检查指定的 main.js 文件是否存在
    if not os.path.exists(file_path):
        # 如果文件不存在，打印警告信息
        print('警告: main.js 文件不存在:', file_path)
        # 返回 False 表示操作失败
        return False

    # 在修改文件之前，先创建一个备份，防止修改出错
    backup_file(file_path)

    # 使用异常处理来捕获可能的文件操作错误
    try:
        # 读取 main.js 文件的全部内容
        with open(file_path, 'r') as f:
            # 读取文件的全部内容到内存中
            content = f.read()

        # 获取当前操作系统名称并转换为小写
        system = platform.system().lower()
        
        # 如果是 macOS 系统
        if system == 'darwin':
            # 在 macOS 上: 替换用于获取硬件 UUID 的 ioreg 命令，改为生成随机 UUID 的命令
            # 使用正则表达式替换
            new_content = re.sub(
                # 要替换的原始命令模式，这是 macOS 用来获取硬件 UUID 的命令
                r'ioreg -rd1 -c IOPlatformExpertDevice',
                # 替换为的新命令，使用 uuidgen 生成随机 UUID 并格式化
                'UUID=$(uuidgen | tr \'[:upper:]\' \'[:lower:]\');echo \\"IOPlatformUUID = \\"$UUID\\";',
                # 在整个文件内容中进行替换
                content
            )
        # 如果是 Windows 系统
        elif system == 'windows':
            # 在 Windows 上: 替换用于获取 MachineGuid 的 REG.exe 命令，改为 PowerShell 生成随机 GUID 的命令
            # 注意：这里使用原始字符串处理复杂的转义字符
            
            # 要替换的原始命令模式，这是 Windows 用来获取注册表中的机器 GUID 的命令
            old_cmd = r'${v5[s$()]}\\REG.exe QUERY HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography /v MachineGuid'
            
            # 替换为的新命令，使用 PowerShell 生成随机 GUID 并转换为小写
            new_cmd = r'powershell -Command "[guid]::NewGuid().ToString().ToLower()"'
            
            # 在整个文件内容中替换特定字符串
            new_content = content.replace(old_cmd, new_cmd)
        # 如果不是上述系统
        else:
            # 打印警告信息，说明当前操作系统不支持修改 main.js
            print('警告: 当前操作系统不支持修改 main.js')
            
            # 返回 False 表示操作失败
            return False

        # 将修改后的内容写回文件
        with open(file_path, 'w') as f:
            # 写入修改后的内容，覆盖原有内容
            f.write(new_content)

        # 根据当前操作系统选择对应的成功标记字符串
        # 如果是 macOS 系统，使用 UUID 生成命令作为标记
        # 如果是 Windows 系统，使用 PowerShell GUID 生成命令作为标记
        success_marker = 'UUID=$(uuidgen | tr \'[:upper:]\' \'[:lower:]\');echo \\"IOPlatformUUID = \\"$UUID\\";' if system == 'darwin' else 'powershell -Command "[guid]::NewGuid().ToString().ToLower()"'
        
        # 检查修改后的文件内容中是否包含成功标记
        if success_marker in new_content:
            # 如果包含成功标记，说明修改成功
            print('main.js 文件修改成功')
            # 返回 True 表示操作成功完成
            return True
        else:
            # 如果不包含成功标记，说明修改可能失败
            # 输出警告信息，提醒用户检查文件内容
            print('警告: main.js 文件可能未被正确修改，请检查文件内容')
            # 提示用户可以从之前创建的备份文件恢复
            print('你可以从备份文件恢复:', file_path + '.backup_*')
            # 返回 False 表示操作可能未成功完成
            return False

    # 捕获文件操作或其他可能发生的任何异常
    except Exception as e:
        # 打印错误信息，包括异常的具体内容
        print('修改 main.js 时出错:', str(e))
        # 返回 False 表示操作失败
        return False

# 定义一个函数，用于更新 storage.json 文件中的各种标识符
def update_storage_file(file_path):
    """
    更新 Cursor 存储文件 storage.json 中的标识符，使用新的随机生成的值。
    这会更改 Cursor 用于遥测和跟踪的所有 ID，使其无法关联到之前的用户身份。
    """
    # 生成一个新的随机机器 ID，用于替换原有的机器 ID
    new_machine_id = generate_random_id()
    # 生成一个新的随机 MAC 机器 ID，用于替换原有的 MAC 机器 ID
    new_mac_machine_id = generate_random_id()
    # 生成一个新的随机设备 ID，使用标准 UUID 格式
    new_dev_device_id = generate_uuid()
    
    # 确保存储文件所在的目录存在，如果不存在则创建
    ensure_dir_exists(os.path.dirname(file_path))
    
    # 读取现有的配置文件或创建新的配置
    if os.path.exists(file_path):
        # 如果文件存在，尝试读取其内容
        try:
            # 以只读模式打开文件
            with open(file_path, 'r') as f:
                # 解析 JSON 内容为 Python 字典
                data = json.load(f)
        # 捕获 JSON 解析错误（文件可能损坏或格式不正确）
        except ValueError:
            # 如果 JSON 无效，则使用空字典作为起点
            data = {}
    else:
        # 如果文件不存在，则创建一个空字典作为起点
        data = {}
    
    # 更新字典中的各种标识符字段
    # 更新主要的机器 ID
    data['telemetry.machineId'] = new_machine_id
    # 更新 MAC 机器 ID
    data['telemetry.macMachineId'] = new_mac_machine_id
    # 更新设备 ID
    data['telemetry.devDeviceId'] = new_dev_device_id
    # 更新 SQM ID，它使用带大括号的大写 UUID 格式
    data['telemetry.sqmId'] = '{' + str(uuid.uuid4()).upper() + '}'
    
    # 将更新后的数据写回文件
    with open(file_path, 'w') as f:
        # 将 Python 字典转换为 JSON 格式并写入文件
        # 使用 4 空格缩进使得 JSON 文件更易读
        json.dump(data, f, indent=4)
    
    # 返回所有生成的新 ID，以便主函数中显示给用户
    return new_machine_id, new_mac_machine_id, new_dev_device_id

# 定义主函数，作为程序的入口点
def main():
    """
    主函数，协调整个 ID 更改过程：
    1. 定位存储文件
    2. 创建备份
    3. 更新 storage.json 中的 ID
    4. 修改 main.js 以使用随机硬件 ID
    这样做可以重置 Cursor 对当前安装的识别，相当于全新安装。
    """
    # 使用异常处理来捕获可能的错误
    try:
        # 获取当前平台的配置文件路径
        storage_path = get_storage_path()
        # 打印找到的配置文件路径，方便用户确认
        print('配置文件路径:', storage_path)
        
        # 在修改前创建原始文件的备份
        backup_file(storage_path)
        
        # 调用更新函数修改 storage.json 中的 ID，并获取新生成的 ID
        machine_id, mac_machine_id, dev_device_id = update_storage_file(storage_path)
        
        # 向用户显示操作结果和新生成的 ID
        print('\n已成功修改 ID:')
        # 显示新的机器 ID
        print('machineId:', machine_id)
        # 显示新的 MAC 机器 ID
        print('macMachineId:', mac_machine_id)
        # 显示新的设备 ID
        print('devDeviceId:', dev_device_id)

        # 根据当前操作系统类型决定是否修改 main.js 文件
        # 获取当前操作系统名称并转换为小写
        system = platform.system().lower()
        # 检查是否是支持修改 main.js 的系统（目前仅支持 macOS 和 Windows）
        if system in ['darwin', 'windows']:
            # 获取 main.js 文件的路径
            main_js_path = get_main_js_path()
            # 如果成功获取到路径（不为 None）
            if main_js_path:
                # 调用更新函数修改 main.js 文件
                update_main_js(main_js_path)
        
    # 捕获执行过程中可能发生的任何异常
    except Exception as e:
        # 打印错误信息到标准错误流
        print('错误:', str(e), file=sys.stderr)
        # 以非零状态码退出程序，表示执行失败
        sys.exit(1)

# 检查脚本是否作为主程序运行（而不是被导入为模块）
if __name__ == '__main__':
    # 如果是主程序，调用主函数开始执行
    main() 
