"""
Gfruit - 一个用于浏览器自动化和数据库管理的Python包
"""

__version__ = "0.1.1"
__author__ = "Your Name"

# 为了让用户可以直接从包中导入类
from .browser_use import SeleniumBase
from .db_manager import DatabaseManager

__all__ = ["SeleniumBase", "DatabaseManager"]