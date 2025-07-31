import logging
# --- 替换为 yxmb_compatlib 的组件 ---
from yxmb_compatlib import login
from kapybara import CustomBrowser
from yxmb_compatlib.config import load_config
# --- 引擎自身的组件 ---
from phis_logging import setup_logging
from .main_数据 import 获取剩余数据
from .data_validator import validate_record
from .result_writer import ResultWriter  # 导入新创建的类
from .错误 import CustomException

def run(patient_func, menu_id: str):
    setup_logging()
    writer = None  # 在 try 外部初始化
    _driver = None # 在 try 外部初始化

    try:
        # 1. 使用 yxmb_compatlib 加载配置
        config = load_config()

        # 2. 将配置传入数据获取和验证模块
        data_remaining, headers, initial_completed = 获取剩余数据()

        # 创建 ResultWriter 实例，它会自动启动后台线程
        writer = ResultWriter(
            success_path="执行结果/成功名单.xlsx",
            failure_path="执行结果/异常名单.xlsx",
            env_path="执行结果/env.txt",
            initial_completed_count=initial_completed
        )

        remaining_counts = len(data_remaining)
        logging.info("剩余操作数: %d", remaining_counts)
        if remaining_counts == 0:
            logging.info("程序已执行完成")
            return
        if "身份证号" not in headers:
            logging.critical("未找到身份证号列，请检查文档/名单.xlsx")
            return

        # 3. 使用 yxmb_compatlib 的 CustomBrowser
        _driver = CustomBrowser(disable_image=False)

        # 4. 使用 yxmb_compatlib 的登录函数，它会利用加载的配置
        login(_driver)

        for record in data_remaining:
            # 5. 将配置和 writer 实例传递给验证器和业务函数
            result, _sfzh, date_data = validate_record(record, headers, config, writer)
            if not result:
                continue
            sfzh = _sfzh.strip()
            from .健康档案_页面 import 搜索并打开病人页面
            original_window = 搜索并打开病人页面(_driver, sfzh, menu_id, writer)
            if not original_window:
                writer.log_failure(sfzh, "未找到该档案")
                continue
            try:
                patient_func(_driver, record, headers, date_data, writer)
            except CustomException as e:
                logging.error(f"处理病人 {sfzh} 时发生错误: {e}", exc_info=True)
                writer.log_failure(sfzh, str(e))
            except Exception as e:
                logging.error(f"处理病人 {sfzh} 时发生未知错误: {e}", exc_info=True)
                writer.log_failure(sfzh, "未知错误 " + str(e))

            _driver.close() # 关闭当前标签页或窗口
            # 切换回原始窗口
            _driver.switch_to.window(original_window)


    except Exception as e:
        logging.error(e, exc_info=True) # 使用 exc_info=True 记录完整的堆栈跟踪
    else:
        logging.info("主程序执行完成。")
    finally:
        # 确保浏览器在任何情况下都能被关闭
        if _driver:
            _driver.quit()
        
        # 优雅地关闭写入器
        if writer:
            writer.shutdown()


if __name__ == "__main__":
    run()