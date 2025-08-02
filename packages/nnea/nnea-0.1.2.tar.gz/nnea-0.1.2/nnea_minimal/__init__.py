"""
NNEA (Neural Network with Explainable Architecture) 精简版包

一个集成了model、io、utils、config功能的生物学可解释性神经网络包，
专门用于转录组学研究。精简版只包含核心功能。
"""

from . import io
from . import model
from . import utils
from . import config
from . import logging_utils

# 主要接口函数
from .io import CreateNNEA, nadata
from .model.models import build, train, eval, explain, save_model, load_project, get_summary

# 日志相关
from .logging_utils import setup_logging, get_logger, logger

__version__ = "0.1.0"
__author__ = "NNEA Team"
__email__ = "nnea@example.com"

__all__ = [
    "CreateNNEA",
    "nadata",
    "build", 
    "train", 
    "eval", 
    "explain",
    "save_model",
    "load_project", 
    "get_summary",
    "setup_logging",
    "get_logger",
    "logger"
] 