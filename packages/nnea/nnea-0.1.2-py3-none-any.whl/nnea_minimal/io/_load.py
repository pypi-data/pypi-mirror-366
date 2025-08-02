import os
import pandas as pd
import numpy as np
import logging
from typing import Optional, Union, Dict, Any
from ._nadata import nadata

# 获取logger
logger = logging.getLogger(__name__)


def CreateNNEA(config: str) -> nadata:
    """
    从不同格式的文件或文件夹中读取数据，并储存到nadata类
    
    Parameters:
    -----------
    config : str
        配置文件路径
        
    Returns:
    --------
    nadata
        包含数据的nadata对象
    """
    # 加载配置
    config_dict = load_config(config)
    
    # 创建nadata对象
    nadata_obj = nadata()
    
    # 将配置保存到Model容器
    nadata_obj.Model.set_config(config_dict)
    
    # 根据配置加载数据
    if 'dataset' in config_dict:
        dataset_config = config_dict['dataset']
        if 'path' in dataset_config:
            data_path = dataset_config['path']
            
            # 检查路径类型
            if os.path.isdir(data_path):
                # 文件夹模式
                nadata_obj = _load_from_folder(data_path, nadata_obj, dataset_config)
            elif os.path.isfile(data_path):
                # 单文件模式
                nadata_obj = _load_from_file(data_path, nadata_obj)
            else:
                raise ValueError(f"Data path does not exist: {data_path}")
    
    return nadata_obj


def load_project(model_path: str) -> nadata:
    """
    从保存的模型文件中加载项目
    
    Parameters:
    -----------
    model_path : str
        模型文件路径
        
    Returns:
    --------
    nadata
        包含训练好的模型和数据的nadata对象
    """
    import torch
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    try:
        # 加载模型状态
        checkpoint = torch.load(model_path, map_location='cpu')
        
        # 创建nadata对象
        nadata_obj = nadata()
        
        # 恢复核心数据
        if 'X' in checkpoint:
            nadata_obj.X = checkpoint['X']
        if 'Meta' in checkpoint:
            nadata_obj.Meta = checkpoint['Meta']
        if 'Var' in checkpoint:
            nadata_obj.Var = checkpoint['Var']
        if 'Model' in checkpoint:
            nadata_obj.Model = checkpoint['Model']
        
        logger.info(f"Successfully loaded project from {model_path}")
        return nadata_obj
        
    except Exception as e:
        logger.error(f"Failed to load project: {e}")
        raise


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Parameters:
    -----------
    config_path : str
        配置文件路径
        
    Returns:
    --------
    Dict[str, Any]
        配置字典
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    # 简化版本只支持JSON格式
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_from_folder(folder_path: str, nadata_obj, dataset_config: Dict[str, Any]):
    """
    从文件夹加载数据
    
    Parameters:
    -----------
    folder_path : str
        文件夹路径
    nadata_obj : nadata
        nadata对象
    dataset_config : Dict[str, Any]
        数据集配置
        
    Returns:
    --------
    nadata
        更新后的nadata对象
    """
    # 查找数据文件
    data_files = []
    for file in os.listdir(folder_path):
        if file.endswith(('.csv', '.txt', '.tsv')):
            data_files.append(os.path.join(folder_path, file))
    
    if not data_files:
        raise ValueError(f"No data files found in {folder_path}")
    
    # 加载第一个找到的数据文件
    data_file = data_files[0]
    logger.info(f"Loading data from {data_file}")
    
    # 读取数据
    if data_file.endswith('.csv'):
        data = pd.read_csv(data_file, index_col=0)
    elif data_file.endswith('.tsv'):
        data = pd.read_csv(data_file, sep='\t', index_col=0)
    else:
        data = pd.read_csv(data_file, sep=None, engine='python', index_col=0)
    
    # 设置数据
    nadata_obj.X = data.values
    nadata_obj.Var = data.columns.tolist()
    nadata_obj.Meta = data.index.tolist()
    
    return nadata_obj


def _load_from_file(file_path: str, nadata_obj):
    """
    从单个文件加载数据
    
    Parameters:
    -----------
    file_path : str
        文件路径
    nadata_obj : nadata
        nadata对象
        
    Returns:
    --------
    nadata
        更新后的nadata对象
    """
    logger.info(f"Loading data from {file_path}")
    
    # 读取数据
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path, index_col=0)
    elif file_path.endswith('.tsv'):
        data = pd.read_csv(file_path, sep='\t', index_col=0)
    else:
        data = pd.read_csv(file_path, sep=None, engine='python', index_col=0)
    
    # 设置数据
    nadata_obj.X = data.values
    nadata_obj.Var = data.columns.tolist()
    nadata_obj.Meta = data.index.tolist()
    
    return nadata_obj 