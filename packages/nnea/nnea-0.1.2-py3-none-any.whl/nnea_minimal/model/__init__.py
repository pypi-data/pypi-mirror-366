"""
模型模块，包含模型构建、训练、评估、解释等功能
"""

from . import base
from . import models

# 导入主要功能
from .base import BaseModel
from .models import build, train, eval, explain, save_model, load_project, get_summary

__all__ = [
    "BaseModel",
    "build",
    "train", 
    "eval",
    "explain",
    "save_model",
    "load_project",
    "get_summary"
] 