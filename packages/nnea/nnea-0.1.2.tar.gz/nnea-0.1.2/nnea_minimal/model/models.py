"""
NNEA模型工厂
根据配置选择不同的模型类型
"""

import logging
import torch
from typing import Dict, Any, Optional
from .base import BaseModel

logger = logging.getLogger(__name__)

def build_model(config: Dict[str, Any]) -> BaseModel:
    """
    根据配置构建模型
    
    Args:
        config: 模型配置
        
    Returns:
        构建好的模型实例
    """
    model_type = config.get('global', {}).get('model', 'nnea')
    
    # 确保设备配置正确传递
    device_config = config.get('global', {}).get('device', 'cpu')
    if device_config == 'cuda' and torch.cuda.is_available():
        config['device'] = 'cuda'
    else:
        config['device'] = 'cpu'
    
    if model_type == 'nnea':
        logger.info("构建NNEA分类器")
        # 创建一个简单的占位符模型
        return SimpleNNEA(config)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")

def build(nadata) -> None:
    """
    构建模型并添加到nadata的Model容器中
    
    Args:
        nadata: nadata对象
    """
    if nadata is None:
        raise ValueError("nadata对象不能为空")
    
    # 获取模型配置
    config = nadata.Model.get_config()
    if not config:
        # 如果没有配置，尝试从nadata.config获取（向后兼容）
        config = getattr(nadata, 'config', {})
        if config:
            nadata.Model.set_config(config)
    
    model_type = config.get('global', {}).get('model', 'nnea')
    
    # 构建模型
    model = build_model(config)
    
    # 构建模型
    model.build(nadata)
    
    # 保存到nadata的Model容器
    nadata.Model.add_model(model_type, model)
    logger.info(f"模型 {model_type} 已构建并添加到nadata")

def train(nadata, model_name: Optional[str] = None, verbose: int = 1) -> Dict[str, Any]:
    """
    训练模型
    
    Args:
        nadata: nadata对象
        model_name: 模型名称，如果为None则使用默认模型
        verbose: 详细程度
        
    Returns:
        训练结果字典
    """
    if nadata is None:
        raise ValueError("nadata对象不能为空")
    
    # 获取模型
    if model_name is None:
        model_name = nadata.Model.list_models()[0] if nadata.Model.list_models() else 'nnea'
    
    model = nadata.Model.get_model(model_name)
    if model is None:
        raise ValueError(f"模型 {model_name} 不存在")
    
    # 训练模型
    results = model.train(nadata, verbose=verbose)
    
    # 保存训练结果
    nadata.Model.set_train_results(results)
    
    logger.info(f"模型 {model_name} 训练完成")
    return results

def eval(nadata, split='test', model_name: Optional[str] = None) -> Dict[str, float]:
    """
    评估模型
    
    Args:
        nadata: nadata对象
        split: 评估的数据集分割
        model_name: 模型名称
        
    Returns:
        评估指标字典
    """
    if nadata is None:
        raise ValueError("nadata对象不能为空")
    
    # 获取模型
    if model_name is None:
        model_name = nadata.Model.list_models()[0] if nadata.Model.list_models() else 'nnea'
    
    model = nadata.Model.get_model(model_name)
    if model is None:
        raise ValueError(f"模型 {model_name} 不存在")
    
    # 评估模型
    metrics = model.evaluate(nadata, split=split)
    
    logger.info(f"模型 {model_name} 在 {split} 集上的评估结果: {metrics}")
    return metrics

def explain(nadata, method='importance', model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    解释模型
    
    Args:
        nadata: nadata对象
        method: 解释方法
        model_name: 模型名称
        
    Returns:
        解释结果字典
    """
    if nadata is None:
        raise ValueError("nadata对象不能为空")
    
    # 获取模型
    if model_name is None:
        model_name = nadata.Model.list_models()[0] if nadata.Model.list_models() else 'nnea'
    
    model = nadata.Model.get_model(model_name)
    if model is None:
        raise ValueError(f"模型 {model_name} 不存在")
    
    # 解释模型
    explanation = model.explain(nadata, method=method)
    
    logger.info(f"模型 {model_name} 解释完成")
    return explanation

def save_model(nadata, save_path: str, model_name: Optional[str] = None) -> None:
    """
    保存模型
    
    Args:
        nadata: nadata对象
        save_path: 保存路径
        model_name: 模型名称
    """
    if nadata is None:
        raise ValueError("nadata对象不能为空")
    
    # 获取模型
    if model_name is None:
        model_name = nadata.Model.list_models()[0] if nadata.Model.list_models() else 'nnea'
    
    model = nadata.Model.get_model(model_name)
    if model is None:
        raise ValueError(f"模型 {model_name} 不存在")
    
    # 保存模型
    model.save(save_path)
    
    logger.info(f"模型 {model_name} 已保存到 {save_path}")

def load_project(load_path: str):
    """
    加载项目
    
    Args:
        load_path: 加载路径
        
    Returns:
        nadata对象
    """
    from ..io import load_project
    return load_project(load_path)

def get_summary(nadata) -> Dict[str, Any]:
    """
    获取模型摘要
    
    Args:
        nadata: nadata对象
        
    Returns:
        摘要字典
    """
    if nadata is None:
        raise ValueError("nadata对象不能为空")
    
    summary = {
        'data_shape': nadata.X.shape if nadata.X is not None else None,
        'models': nadata.Model.list_models(),
        'config': nadata.Model.get_config(),
        'train_results': nadata.Model.get_train_results()
    }
    
    return summary


class SimpleNNEA(BaseModel):
    """
    简单的NNEA模型实现（占位符）
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
    def build(self, nadata) -> None:
        """构建模型（占位符）"""
        print("SimpleNNEA build method called")
        self.model = None
        
    def train(self, nadata, **kwargs) -> Dict[str, Any]:
        """训练模型（占位符）"""
        print("SimpleNNEA train method called")
        return {'loss': 0.0, 'accuracy': 0.0}
        
    def predict(self, nadata) -> np.ndarray:
        """模型预测（占位符）"""
        print("SimpleNNEA predict method called")
        return np.zeros((10, 1))
        
    def evaluate(self, nadata, split='test') -> Dict[str, float]:
        """模型评估（占位符）"""
        print("SimpleNNEA evaluate method called")
        return {'accuracy': 0.0, 'loss': 0.0}
        
    def explain(self, nadata, method='importance') -> Dict[str, Any]:
        """模型解释（占位符）"""
        print("SimpleNNEA explain method called")
        return {'importance': np.zeros(10)} 