"""
配置设置模块
提供配置文件的加载、保存和验证功能
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


def load_config(filepath: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        filepath: 配置文件路径
    
    Returns:
        配置字典
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"配置文件不存在: {filepath}")
    
    file_ext = Path(filepath).suffix.lower()
    
    if file_ext == '.json':
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError(f"不支持的配置文件格式: {file_ext}")


def save_config(config: Dict[str, Any], filepath: str, format: str = "json") -> None:
    """
    保存配置文件
    
    Args:
        config: 配置字典
        filepath: 文件路径
        format: 保存格式 ("json")
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    if format == "json":
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f"不支持的格式: {format}")


def update_config(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新配置
    
    Args:
        config: 原始配置
        updates: 更新内容
    
    Returns:
        更新后的配置
    """
    def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                d[k] = deep_update(d[k], v)
            else:
                d[k] = v
        return d
    
    return deep_update(config.copy(), updates)


def validate_config(config: Dict[str, Any], required_keys: list = None) -> bool:
    """
    验证配置有效性
    
    Args:
        config: 配置字典
        required_keys: 必需的键列表
    
    Returns:
        配置是否有效
    """
    if required_keys:
        missing_keys = set(required_keys) - set(config.keys())
        if missing_keys:
            raise ValueError(f"缺少必需的配置键: {missing_keys}")
    
    return True


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    获取配置值
    
    Args:
        config: 配置字典
        key_path: 键路径 (用.分隔)
        default: 默认值
    
    Returns:
        配置值
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> Dict[str, Any]:
    """
    设置配置值
    
    Args:
        config: 配置字典
        key_path: 键路径 (用.分隔)
        value: 要设置的值
    
    Returns:
        更新后的配置
    """
    keys = key_path.split('.')
    new_config = config.copy()
    current = new_config
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return new_config 