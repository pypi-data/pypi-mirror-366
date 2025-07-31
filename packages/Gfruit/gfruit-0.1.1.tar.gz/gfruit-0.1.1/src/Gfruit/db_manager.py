"""
Gfruit Database Manager Module

This module provides the DatabaseManager class for database operations.
"""

import pymysql
from pymysql.cursors import DictCursor
from loguru import logger
import time

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.db_config = {
            'host': host ,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'cursorclass': DictCursor,
            'connect_timeout': 60,  # 连接超时时间
            'read_timeout': 30,     # 读取超时时间
            'write_timeout': 30     # 写入超时时间
        }
        self.max_retries = 3
        self.retry_delay = 1  # 重试延迟（秒）
        self.conn = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        try:
            if self.conn is None or not self.conn.open:
                self.conn = pymysql.connect(**self.db_config)
                self.cursor = self.conn.cursor()
                # logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise

    def execute_with_retry(self, sql, params=None):
        """执行SQL语句，带有重试机制"""
        for attempt in range(self.max_retries):
            try:
                if not self.conn or not self.conn.open:
                    self.connect()
                
                self.cursor.execute(sql, params)
                self.conn.commit()
                return self.cursor.fetchall()
            
            except (pymysql.Error, Exception) as e:
                logger.warning(f"执行SQL失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    try:
                        self.close()
                    except:
                        pass
                    continue
                else:
                    logger.error(f"SQL执行失败，已达到最大重试次数: {str(e)}")
                    raise

    def executemany_with_retry(self, sql, params_list):
        """批量执行SQL语句，带有重试机制"""
        for attempt in range(self.max_retries):
            try:
                if not self.conn or not self.conn.open:
                    self.connect()

                affected_rows = self.cursor.executemany(sql, params_list)
                self.conn.commit()
                return affected_rows

            except (pymysql.Error, Exception) as e:
                logger.warning(f"批量执行SQL失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    try:
                        self.close()
                    except:
                        pass
                    continue
                else:
                    logger.error(f"批量SQL执行失败，已达到最大重试次数: {str(e)}")
                    raise

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params or ())
        return  self.cursor.fetchone()

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params or ())
        return  self.cursor.fetchall()
    def close(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn and self.conn.open:
                self.conn.close()
            # logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {str(e)}")

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close() 