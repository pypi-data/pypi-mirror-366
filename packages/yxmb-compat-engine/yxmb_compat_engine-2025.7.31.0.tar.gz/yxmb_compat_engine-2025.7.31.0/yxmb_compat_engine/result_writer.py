import pandas as pd
from kapybara.common import env_write, excel_append, check_and_create_excel
import logging
import queue
import threading
import time

class ResultWriter:
    """
    负责记录程序执行结果。
    使用一个专用的后台线程来写入Excel文件，以避免主程序因文件锁定而被阻塞。
    """

    def __init__(self, success_path: str, failure_path: str, env_path: str, initial_completed_count: int = 0):
        self.success_path = success_path
        self.failure_path = failure_path
        self.env_path = env_path
        self.completed_count = initial_completed_count

        # 定义表头
        self.success_columns = ["身份证号", "成功"]
        self.failure_columns = ["身份证号", "异常原因"]

        # 初始化Excel文件
        self._setup_excel_file(self.success_path, self.success_columns)
        self._setup_excel_file(self.failure_path, self.failure_columns)

        # 创建一个线程安全的队列来存放写任务
        self.write_queue = queue.Queue()
        
        # 启动后台写入线程
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _worker(self):
        """后台工作线程，从队列中获取任务并写入文件。"""
        while True:
            try:
                task = self.write_queue.get()
                if task is None:  # 哨兵值，表示结束线程
                    break
                
                file_path, key_col, key_val, data_col, data_val = task
                
                # 尝试写入，如果失败则重试
                while True:
                    try:
                        excel_append(file_path, key_col, key_val, data_col, data_val)
                        break  # 写入成功，跳出重试循环
                    except PermissionError:
                        logging.warning(f"文件 {file_path} 正被使用，将在5秒后重试...")
                        time.sleep(5)
                    except Exception as e:
                        logging.error(f"写入文件 {file_path} 时发生未知错误: {e}")
                        break # 发生其他错误，放弃此条记录以避免死循环
                
                self.write_queue.task_done()
            except Exception as e:
                logging.error(f"写入线程发生致命错误: {e}")


    def _setup_excel_file(self, file_path, columns):
        """检查Excel是否具有正确的表头,如果没有，则添加表头"""
        check_and_create_excel(file_path)
        try:
            # 尝试读取，如果文件被占用，此操作也可能失败，但这是启动时的一次性检查
            existing_data = pd.read_excel(file_path)
            if not set(columns).issubset(existing_data.columns):
                header_df = pd.DataFrame(columns=columns)
                header_df.to_excel(file_path, index=False, header=True)
                logging.warning('文件 %s 没有表头,已添加表头', file_path)
        except (pd.errors.EmptyDataError, ValueError):
            header_df = pd.DataFrame(columns=columns)
            header_df.to_excel(file_path, index=False, header=True)
            logging.info('文件 %s 为空,已添加表头', file_path)
        except PermissionError:
            logging.warning(f"无法检查文件 {file_path} 的表头，因为它正被使用。")
        except Exception as e:
            logging.error(f"初始化文件 {file_path} 失败: {e}")


    def _increment_and_log_count(self):
        """内部方法，用于增加计数并写入env文件"""
        self.completed_count += 1
        env_write(self.env_path, 3, f"已完成数量:{self.completed_count}")

    def log_success(self, id_number: str, reason: str = "成功"):
        """将成功的操作任务放入队列。"""
        task = (self.success_path, "身份证号", id_number + "\t", "成功", reason)
        self.write_queue.put(task)
        self._increment_and_log_count()
        logging.info(f"记录成功: {id_number}")

    def log_failure(self, id_number: str, reason: str):
        """将失败的操作任务放入队列。"""
        task = (self.failure_path, "身份证号", id_number + "\t", "异常原因", reason)
        self.write_queue.put(task)
        self._increment_and_log_count()
        logging.warning(f"记录异常: {id_number}, 原因: {reason}")

    def log_current_person(self, id_number: str):
        """更新当前正在处理的人员信息"""
        env_write(self.env_path, 2, f"当前处理身份证号:{id_number}")
        logging.info("当前处理身份证号: %s", id_number)

    def shutdown(self):
        """等待所有任务完成并关闭工作线程。"""
        logging.info("正在等待所有日志写入完成...")
        self.write_queue.join()  # 等待队列中的所有任务被处理
        self.write_queue.put(None) # 发送哨兵值来停止线程
        self.worker_thread.join() # 等待线程真正结束
        logging.info("日志写入完成，程序关闭。")
