"""
默认配置模块
提供各种默认配置参数
"""

from typing import Dict, Any


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    
    Returns:
        默认配置字典
    """
    return {
        "model": {
            "type": "neural_network",
            "layers": [100, 50, 25],
            "activation": "relu",
            "dropout": 0.2,
            "batch_norm": True,
            "regularization": "l2",
            "regularization_factor": 0.01
        },
        "data": {
            "train_path": "",
            "test_path": "",
            "validation_split": 0.2,
            "batch_size": 32,
            "shuffle": True,
            "normalize": True,
            "augmentation": False
        },
        "training": {
            "epochs": 100,
            "learning_rate": 0.001,
            "optimizer": "adam",
            "loss": "binary_crossentropy",
            "early_stopping": True,
            "patience": 10,
            "reduce_lr_on_plateau": True,
            "min_lr": 1e-7
        },
        "output": {
            "model_path": "models/",
            "results_path": "results/",
            "log_path": "logs/",
            "save_best_only": True,
            "save_format": "h5"
        },
        "explainability": {
            "feature_importance": True,
            "shap_values": True,
            "gradient_analysis": True,
            "attention_weights": True
        }
    }


def get_classification_config() -> Dict[str, Any]:
    """
    获取分类任务默认配置
    
    Returns:
        分类任务配置
    """
    config = get_default_config()
    config["model"]["output_activation"] = "softmax"
    config["training"]["loss"] = "categorical_crossentropy"
    config["training"]["metrics"] = ["accuracy", "precision", "recall", "f1"]
    return config


def get_regression_config() -> Dict[str, Any]:
    """
    获取回归任务默认配置
    
    Returns:
        回归任务配置
    """
    config = get_default_config()
    config["model"]["output_activation"] = "linear"
    config["training"]["loss"] = "mse"
    config["training"]["metrics"] = ["mae", "mse", "rmse"]
    return config


def get_binary_classification_config() -> Dict[str, Any]:
    """
    获取二分类任务默认配置
    
    Returns:
        二分类任务配置
    """
    config = get_default_config()
    config["model"]["output_activation"] = "sigmoid"
    config["training"]["loss"] = "binary_crossentropy"
    config["training"]["metrics"] = ["accuracy", "precision", "recall", "f1", "auc"]
    return config 