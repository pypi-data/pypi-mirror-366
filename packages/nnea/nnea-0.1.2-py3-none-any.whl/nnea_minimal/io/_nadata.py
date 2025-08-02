import torch
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Union
import pickle


class nadata(object):
    """
    NNEA的核心数据类，用来储存数据
    
    重构后的简洁数据结构设计：
    1. **表达矩阵数据（X）**: 行是基因数，列是样本数，支持稀疏矩阵格式
    2. **表型数据（Meta）**: 行是样本数，列是样本的特征，包含train/test/val索引
    3. **基因数据（Var）**: 行是基因数，列是基因特征，包括基因名称、类型、重要性等
    4. **先验知识（Prior）**: 基因集的0，1稀疏矩阵，代表基因是否在基因集合里
    5. **模型容器（Model）**: 储存所有模型、配置、训练历史等
    """

    def __init__(self, X=None, Meta=None, Var=None, Prior=None):
        """
        初始化nadata对象
        
        Parameters:
        -----------
        X : Optional[Union[np.ndarray, torch.Tensor, pd.DataFrame]]
            表达矩阵，形状为(基因数, 样本数)
        Meta : Optional[Union[np.ndarray, pd.DataFrame]]
            表型数据，形状为(样本数, 特征数)，包含train/test/val索引
        Var : Optional[Union[np.ndarray, pd.DataFrame]]
            基因数据，形状为(基因数, 特征数)
        Prior : Optional[Union[np.ndarray, torch.Tensor]]
            先验知识矩阵，形状为(基因集数, 基因数)
        """
        # 核心数据
        self.X = X          # 表达矩阵
        self.Meta = Meta    # 表型数据（包含索引）
        self.Var = Var      # 基因数据
        self.Prior = Prior  # 先验知识
        
        # 模型容器 - 包含所有模型相关的内容
        self.Model = ModelContainer()
        # 设置ModelContainer对nadata的引用
        self.Model._nadata = self

    def save(self, filepath: str, format: str = 'pt', save_data: bool = True):
        """
        保存nadata对象
        
        Parameters:
        -----------
        filepath : str
            保存路径
        format : str
            保存格式，支持'pt', 'pickle'
        save_data : bool
            是否保存数据，如果为False只保存模型和配置
        """
        if format == 'pt':
            # 保存为PyTorch格式
            save_dict = {}
            if save_data:
                if self.X is not None:
                    save_dict['X'] = self.X
                if self.Meta is not None:
                    save_dict['Meta'] = self.Meta
                if self.Var is not None:
                    save_dict['Var'] = self.Var
                if self.Prior is not None:
                    save_dict['Prior'] = self.Prior
            
            # 保存模型容器
            if self.Model:
                save_dict['Model'] = self.Model
            
            torch.save(save_dict, filepath)
            
        elif format == 'pickle':
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def load(self, filepath: str):
        """
        加载nadata对象
        
        Parameters:
        -----------
        filepath : str
            文件路径
        """
        if filepath.endswith('.pt'):
            checkpoint = torch.load(filepath, map_location='cpu')
            
            if 'X' in checkpoint:
                self.X = checkpoint['X']
            if 'Meta' in checkpoint:
                self.Meta = checkpoint['Meta']
            if 'Var' in checkpoint:
                self.Var = checkpoint['Var']
            if 'Prior' in checkpoint:
                self.Prior = checkpoint['Prior']
            if 'Model' in checkpoint:
                self.Model = checkpoint['Model']
                
        elif filepath.endswith('.pkl'):
            with open(filepath, 'rb') as f:
                loaded_obj = pickle.load(f)
                self.__dict__.update(loaded_obj.__dict__)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")

    def print(self, module: Optional[str] = None):
        """
        打印nadata对象信息
        
        Parameters:
        -----------
        module : Optional[str]
            指定打印的模块
        """
        if module is None:
            print("=== NNEA Data Object ===")
            print(f"Expression matrix (X): {self.X.shape if self.X is not None else 'None'}")
            print(f"Meta data: {self.Meta.shape if self.Meta is not None else 'None'}")
            print(f"Variable data: {self.Var.shape if self.Var is not None else 'None'}")
            print(f"Prior knowledge: {self.Prior.shape if self.Prior is not None else 'None'}")
            print(f"Model container: {self.Model}")
        else:
            if module == 'X':
                print(f"Expression matrix: {self.X}")
            elif module == 'Meta':
                print(f"Meta data: {self.Meta}")
            elif module == 'Var':
                print(f"Variable data: {self.Var}")
            elif module == 'Prior':
                print(f"Prior knowledge: {self.Prior}")
            elif module == 'Model':
                print(f"Model container: {self.Model}")

    def copy(self):
        """
        复制nadata对象
        
        Returns:
        --------
        nadata
            复制的nadata对象
        """
        new_obj = nadata()
        new_obj.X = self.X.copy() if self.X is not None else None
        new_obj.Meta = self.Meta.copy() if self.Meta is not None else None
        new_obj.Var = self.Var.copy() if self.Var is not None else None
        new_obj.Prior = self.Prior.copy() if self.Prior is not None else None
        new_obj.Model = self.Model
        return new_obj

    def subset(self, samples: Optional[list] = None, genes: Optional[list] = None):
        """
        子集化数据
        
        Parameters:
        -----------
        samples : Optional[list]
            样本索引
        genes : Optional[list]
            基因索引
        """
        if samples is not None and self.X is not None:
            self.X = self.X[:, samples]
            if self.Meta is not None:
                if isinstance(self.Meta, pd.DataFrame):
                    self.Meta = self.Meta.iloc[samples]
                else:
                    self.Meta = self.Meta[samples]
        
        if genes is not None and self.X is not None:
            self.X = self.X[genes, :]
            if self.Var is not None:
                if isinstance(self.Var, pd.DataFrame):
                    self.Var = self.Var.iloc[genes]
                else:
                    self.Var = self.Var[genes]

    def build(self):
        """构建模型"""
        return self.Model.build()

    def train(self, verbose: int = 1):
        """训练模型"""
        return self.Model.train(verbose=verbose)

    def evaluate(self):
        """评估模型"""
        return self.Model.evaluate()

    def explain(self, verbose: int = 1):
        """解释模型"""
        return self.Model.explain(verbose=verbose)


class ModelContainer:
    """
    模型容器类，用于管理模型、配置、训练历史等
    """
    
    def __init__(self):
        """初始化模型容器"""
        self._nadata = None
        self.models = {}
        self.config = {}
        self.train_results = {}
        self.indices = {
            'train': None,
            'test': None,
            'val': None
        }
        self.metadata = {}

    def add_model(self, name: str, model):
        """
        添加模型
        
        Parameters:
        -----------
        name : str
            模型名称
        model : Any
            模型对象
        """
        self.models[name] = model

    def get_model(self, name: str):
        """
        获取模型
        
        Parameters:
        -----------
        name : str
            模型名称
            
        Returns:
        --------
        Any
            模型对象
        """
        return self.models.get(name)

    def has_model(self, name: str) -> bool:
        """
        检查是否有指定模型
        
        Parameters:
        -----------
        name : str
            模型名称
            
        Returns:
        --------
        bool
            是否有该模型
        """
        return name in self.models

    def list_models(self) -> list:
        """
        列出所有模型名称
        
        Returns:
        --------
        list
            模型名称列表
        """
        return list(self.models.keys())

    def set_config(self, config: dict):
        """
        设置配置
        
        Parameters:
        -----------
        config : dict
            配置字典
        """
        self.config = config

    def get_config(self) -> dict:
        """
        获取配置
        
        Returns:
        --------
        dict
            配置字典
        """
        return self.config

    def set_train_results(self, results: dict):
        """
        设置训练结果
        
        Parameters:
        -----------
        results : dict
            训练结果字典
        """
        self.train_results = results

    def get_train_results(self) -> dict:
        """
        获取训练结果
        
        Returns:
        --------
        dict
            训练结果字典
        """
        return self.train_results

    def set_indices(self, train_idx=None, test_idx=None, val_idx=None):
        """
        设置数据分割索引
        
        Parameters:
        -----------
        train_idx : Optional[list]
            训练集索引
        test_idx : Optional[list]
            测试集索引
        val_idx : Optional[list]
            验证集索引
        """
        if train_idx is not None:
            self.indices['train'] = train_idx
        if test_idx is not None:
            self.indices['test'] = test_idx
        if val_idx is not None:
            self.indices['val'] = val_idx

    def get_indices(self, split: str = None):
        """
        获取数据分割索引
        
        Parameters:
        -----------
        split : Optional[str]
            分割类型 ('train', 'test', 'val')
            
        Returns:
        --------
        Union[list, dict]
            索引列表或索引字典
        """
        if split is None:
            return self.indices
        return self.indices.get(split)

    def add_metadata(self, key: str, value):
        """
        添加元数据
        
        Parameters:
        -----------
        key : str
            键名
        value : Any
            值
        """
        self.metadata[key] = value

    def get_metadata(self, key: str = None):
        """
        获取元数据
        
        Parameters:
        -----------
        key : Optional[str]
            键名
            
        Returns:
        --------
        Union[Any, dict]
            元数据值或元数据字典
        """
        if key is None:
            return self.metadata
        return self.metadata.get(key)

    def build(self):
        """构建模型（占位符）"""
        print("Model build method called")
        return None

    def train(self, verbose: int = 1):
        """训练模型（占位符）"""
        print("Model train method called")
        return None

    def evaluate(self):
        """评估模型（占位符）"""
        print("Model evaluate method called")
        return None

    def explain(self, verbose: int = 1):
        """解释模型（占位符）"""
        print("Model explain method called")
        return None

    def __str__(self):
        return f"ModelContainer(models={list(self.models.keys())}, config_keys={list(self.config.keys())})"

    def __repr__(self):
        return self.__str__() 