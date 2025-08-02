"""
获取剩余需要处理的数据
文档/名单.xlsx

已处理数量在 执行结果/env.txt
"""

import pandas as pd
import logging

from kapybara.common.envWrite import env_write
from phis_config import ProgramConfigV2


def 获取剩余数据() -> tuple:
    completed_count = int(ProgramConfigV2.get_completed_count())

    df_full = pd.read_excel('文档/名单.xlsx', engine='openpyxl',  dtype={'身份证号': str})
    data1 = df_full.to_dict('records')
    max_number = len(data1)
    # 获取表头（列名）
    headers = df_full.columns.tolist()
    logging.info('总操作数: %d', max_number)

    env_write('执行结果/env.txt', 1, f'总操作数:{max_number}')

    data_remaining = df_full.iloc[completed_count:].to_dict('records')
    return data_remaining, headers, completed_count