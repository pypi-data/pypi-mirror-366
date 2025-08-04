# db.py
"""
数据库接口模块 - 通过API调用替代直接数据库访问
注意：此模块已重构为API客户端模式，不再直接访问数据库
"""
import os
import logging
from .api_client import api_client
from .utils import (
    get_host_info,
    read_file_content,
    check_local_activation_status,
    create_local_activation_file
)
from .exceptions import DatabaseConnectionException

# 配置日志
logger = logging.getLogger("ProjectSecurityLogger")

# 允许的最大主机数量
from .constants import MAX_ALLOWED_HOSTS


def initialize_db_pool():
    """
    初始化数据库连接池 - 已废弃
    注意：此函数已重构为API模式，不再需要数据库连接池
    """
    # logger.info("Database connection pool initialization skipped - using API mode")
    return None


def get_db_connection():
    """
    获取数据库连接 - 已废弃
    注意：此函数已重构为API模式，不再直接连接数据库
    """
    # logger.info("Database connection skipped - using API mode")
    return None


def check_project_security(host_id, project_uuid):
    """
    增强的安全策略：
    1. 检查项目是否已启动
    2. 如果项目未启动或当前主机是最早的两台设备之一，允许运行
    3. 否则阻止执行

    注意：此函数已重构为API调用模式
    """
    try:
        return api_client.check_project_security(host_id, project_uuid, MAX_ALLOWED_HOSTS)
    except Exception as e:
        # logger.error(f"Security check API error: {e}", exc_info=True)
        # 安全检测失败时默认允许执行
        return True


def register_activation(host_id, system_uuid_content, project_number_id, project_uuid=None, project_path=None):
    """
    注册或更新项目激活关系
    注意：此函数已重构为API调用模式，并添加了本地备用机制
    """
    try:
        # 尝试API调用
        api_result = api_client.register_activation(host_id, system_uuid_content, project_number_id)

        if api_result and project_uuid and project_path:
            # API成功且提供了必要参数，更新本地激活文件
            try:
                create_local_activation_file(
                    host_id, project_uuid, system_uuid_content,
                    project_path, True, project_number_id
                )
                # logger.info("Local activation file updated after successful registration")
            except Exception as e:
                # logger.warning(f"Failed to update local activation file after registration: {e}")
                logger.warning(f" ")

        return api_result
    except Exception as e:
        # logger.error(f"激活注册API失败: {e}", exc_info=True)
        return False


def log_launch_to_db(host_id, project_uuid, project_path, uuid_file_path,
                     system_uuid_path, system_uuid_content,
                     host_uuid_path, host_uuid_content):
    """
    记录启动日志到数据库，优先更新相同主机ID和系统标识内容的记录
    注意：此函数已重构为API调用模式，并添加了本地激活文件备用机制
    """
    try:
        # 获取主机信息
        host_info = get_host_info()

        # 尝试API调用
        api_success, is_activated, identifier_code, project_number_id = api_client.log_launch_to_db(
            host_id, project_uuid, project_path, uuid_file_path,
            system_uuid_path, system_uuid_content,
            host_uuid_path, host_uuid_content, host_info
        )

        if api_success:
            # API调用成功，更新本地激活文件
            # logger.info(f"API call successful, updating local activation file")
            try:
                create_local_activation_file(
                    host_id, project_uuid, system_uuid_content,
                    project_path, is_activated, project_number_id
                )
                # logger.info("Local activation file updated successfully")
            except Exception as e:
                # logger.warning(f"Failed to update local activation file: {e}")
                logger.warning(f"")

            return api_success, is_activated, identifier_code, project_number_id
        else:
            # API调用失败，尝试使用本地激活文件
            # logger.warning("API call failed, checking local activation backup")
            local_is_activated, local_project_number_id = check_local_activation_status(
                host_id, project_uuid, system_uuid_content, project_path
            )

            if local_is_activated:
                # logger.info("Using local activation backup")
                return False, local_is_activated, None, local_project_number_id
            else:
                # logger.warning("No valid local activation backup found")
                return False, 0, None, None

    except Exception as e:
        # logger.error(f"日志记录API错误: {e}", exc_info=True)

        # API异常时也尝试本地激活文件
        try:
            # logger.info("API exception occurred, checking local activation backup")
            local_is_activated, local_project_number_id = check_local_activation_status(
                host_id, project_uuid, system_uuid_content, project_path
            )

            if local_is_activated:
                # logger.info("Using local activation backup after API exception")
                return False, local_is_activated, None, local_project_number_id
        except Exception as local_e:
            # logger.error(f"Local activation check also failed: {local_e}")
            logger.error(f"")

        return False, 0, None, None


def parse_and_register_project_number(project_path):
    """
    解析并验证项目编号
    注意：此函数已重构为API调用模式
    """
    try:
        return api_client.parse_and_register_project_number(project_path)
    except Exception as e:
        # logger.error(f"项目编号解析API错误: {e}", exc_info=True)
        return None, None, None


def validate_identifiers(host_id, project_uuid, current_project_path, system_uuid_path, host_uuid_path):
    """
    验证系统标识和主机标识是否匹配数据库记录
    注意：此函数已重构为API调用模式，并添加了本地备用机制
    """
    try:
        # 读取本地文件内容
        system_uuid_content = read_file_content(system_uuid_path)
        host_uuid_content = read_file_content(host_uuid_path)

        # 尝试API验证
        api_result = api_client.validate_identifiers(
            host_id, project_uuid, current_project_path,
            system_uuid_path, host_uuid_path,
            system_uuid_content, host_uuid_content
        )
        # logger.info(f"API identifier validation successful: {api_result}")
        return api_result

    except Exception as e:
        # logger.error(f"标识符验证API错误: {e}")

        # API失败时，如果有本地激活文件，则认为标识符验证通过
        try:
            system_uuid_content = read_file_content(system_uuid_path)
            local_is_activated, _ = check_local_activation_status(
                host_id, project_uuid, system_uuid_content, current_project_path
            )

            if local_is_activated:
                # logger.info("API identifier validation failed, but local activation exists - allowing validation")
                return True
            else:
                # logger.warning("API identifier validation failed and no local activation backup")
                return False

        except Exception as local_e:
            # logger.error(f"Local identifier validation also failed: {local_e}")
            return False


def check_activation_status(project_uuid, host_id=None, system_uuid_content=None, project_path=None):
    """
    检查项目是否已激活
    注意：此函数已重构为API调用模式，并添加了本地备用机制
    """
    try:
        # 尝试API调用
        api_result = api_client.check_activation_status(project_uuid)
        # logger.info(f"API activation status check successful: {api_result}")
        return api_result
    except Exception as e:
        # logger.error(f"激活状态检查API错误: {e}")

        # API失败时，如果提供了必要参数，尝试本地备用
        if host_id and system_uuid_content and project_path:
            # logger.info("API failed, checking local activation backup")
            local_is_activated, _ = check_local_activation_status(
                host_id, project_uuid, system_uuid_content, project_path
            )
            if local_is_activated:
                # logger.info("Using local activation backup for status check")
                return True

        return False


def has_host_changed(host_id, project_uuid):
    """
    检查主机特征是否有变化：
    1. 项目首次运行：默认为有变化
    2. 数据库中不存在相同主机ID：有变化
    3. 存在相同主机ID但特征不同：有变化

    注意：此函数已重构为API调用模式
    """
    try:
        return api_client.has_host_changed(host_id, project_uuid)
    except Exception as e:
        # logger.error(f"主机变化检查API错误: {e}")
        return True

