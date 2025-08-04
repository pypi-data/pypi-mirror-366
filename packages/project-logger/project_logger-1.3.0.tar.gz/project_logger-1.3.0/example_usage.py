#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地激活机制使用示例
演示如何在项目中使用新的激活备用机制
"""

import os
import sys
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demonstrate_activation_mechanism():
    """演示激活机制的工作流程"""
    print("=" * 60)
    print("本地激活机制演示")
    print("=" * 60)
    
    try:
        # 导入必要的模块
        from security import perform_security_check
        from utils import (
            get_host_id,
            get_project_uuid,
            create_system_uuid_file,
            check_local_activation_status
        )
        
        print("\n1. 获取项目基本信息...")
        host_id = get_host_id()
        project_uuid, _ = get_project_uuid()
        project_path = os.getcwd()
        
        print(f"   主机ID: {host_id[:16]}...")
        print(f"   项目UUID: {project_uuid[:16]}...")
        print(f"   项目路径: {project_path}")
        
        # 创建系统标识文件
        print("\n2. 创建系统标识文件...")
        system_uuid_path, system_uuid_content = create_system_uuid_file(project_path)
        print(f"   系统标识文件: {system_uuid_path}")
        
        # 检查当前本地激活状态
        print("\n3. 检查当前本地激活状态...")
        is_activated, project_number_id = check_local_activation_status(
            host_id, project_uuid, system_uuid_content, project_path
        )
        print(f"   本地激活状态: {is_activated}")
        print(f"   项目编号ID: {project_number_id}")
        
        print("\n4. 执行安全检查（包含激活验证）...")
        print("   注意：这会尝试API调用，如果失败会使用本地备用机制")
        
        # 这里我们不直接调用perform_security_check()，因为它会退出程序
        # 而是演示相关的逻辑
        
        print("\n5. 激活机制工作原理说明：")
        print("   a) 优先尝试API调用获取激活状态")
        print("   b) API成功时，更新本地激活文件")
        print("   c) API失败时，读取本地激活文件作为备用")
        print("   d) 本地文件包含项目和主机绑定信息，防止误用")
        
        print("\n6. 本地激活文件特性：")
        print("   - 文件名基于主机ID、项目UUID和系统UUID生成")
        print("   - 文件内容加密存储")
        print("   - 包含项目路径信息，支持项目迁移检测")
        print("   - 存储在用户主目录的隐藏文件夹中")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_activation_file_location():
    """显示激活文件的存储位置"""
    try:
        from utils import get_local_activation_file_path, get_host_id, get_project_uuid, create_system_uuid_file
        
        print("\n" + "=" * 60)
        print("本地激活文件位置信息")
        print("=" * 60)
        
        host_id = get_host_id()
        project_uuid, _ = get_project_uuid()
        project_path = os.getcwd()
        system_uuid_path, system_uuid_content = create_system_uuid_file(project_path)
        
        activation_file_path = get_local_activation_file_path(
            host_id, project_uuid, system_uuid_content
        )
        
        print(f"激活文件路径: {activation_file_path}")
        print(f"文件是否存在: {activation_file_path.exists()}")
        
        if activation_file_path.exists():
            import os
            file_size = os.path.getsize(activation_file_path)
            print(f"文件大小: {file_size} 字节")
            
            # 显示文件修改时间
            import time
            mod_time = os.path.getmtime(activation_file_path)
            print(f"最后修改时间: {time.ctime(mod_time)}")
        
    except Exception as e:
        print(f"❌ 获取文件信息时发生错误: {e}")


if __name__ == "__main__":
    print("本地激活机制使用示例")
    
    # 演示激活机制
    success = demonstrate_activation_mechanism()
    
    # 显示文件位置信息
    show_activation_file_location()
    
    if success:
        print("\n🎉 演示完成！")
        print("\n使用说明：")
        print("1. 在正常情况下，项目会通过API验证激活状态")
        print("2. 当API服务器不可用时，会自动使用本地激活文件")
        print("3. 本地激活文件只有在API成功验证后才会创建/更新")
        print("4. 这确保了即使API断开，已激活的项目仍能正常运行")
    else:
        print("\n❌ 演示失败！")
