import logging
import re
import numpy as np
from .chinese_id_check import is_valid_chinese_id
from typing import Tuple, Optional
import pandas as pd
from .result_writer import ResultWriter # 确保导入

# 不再需要 excel_append
# from kapybara.common.write_excel import excel_append


def validate_record(record: dict, headers: list, config: dict, writer: ResultWriter) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    验证单个记录。
    """
    # ... (前面的空值检查不变) ...
    if isinstance(record["身份证号"], float) and np.isnan(record["身份证号"]):
        return False, None, None
    if isinstance(record["身份证号"], str) and record["身份证号"].strip() == "":
        return False, None, None

    # ... (获取验证配置不变) ...
    validation_config = config.get("validation", {})
    strict_id_check = validation_config.get("strict_id_check", True)

    # 验证身份证号格式
    id_number = str(record["身份证号"])
    if strict_id_check:
        verified, message = is_valid_chinese_id(id_number)
        if not verified:
            # 使用 writer 记录错误
            writer.log_failure(id_number, f"身份证号无效: {message}")
            return False, None, None

    sfzh = id_number.replace("x", "X").strip()

    # ... (日期查找逻辑不变) ...
    date_columns_priority = validation_config.get("date_columns", ["随访日期", "成功", "日期"])
    date_value = None
    found_column = None
    for col_name in date_columns_priority:
        if col_name in headers:
            date_value = record[col_name]
            found_column = col_name
            break
    
    if found_column is None:
        logging.critical(f'{sfzh} - 在表头中未找到任何指定的日期列: {date_columns_priority}')
        # 这种严重错误可能需要特殊处理，但也可以用writer记录
        writer.log_failure(sfzh, f"未找到日期列: {date_columns_priority}")
        return False, None, None

    # ... (日期解析逻辑不变) ...
    date_data_str = ""
    if isinstance(date_value, (int, float)) and not np.isnan(date_value):
        try:
            date_data_str = pd.to_datetime(
                date_value, unit="D", origin="1899-12-30"
            ).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass

    if not date_data_str:
        date_data_str = str(date_value)

    date_match = re.findall(r"\d{4}-\d{2}-\d{2}", date_data_str)
    if not date_match:
        # 使用 writer 记录错误
        reason = f"在列 '{found_column}' 中找到的日期格式不正确: {date_data_str}"
        writer.log_failure(sfzh, reason)
        logging.critical(f"{sfzh} - {reason}")
        return False, None, None

    return True, sfzh, date_match[0]