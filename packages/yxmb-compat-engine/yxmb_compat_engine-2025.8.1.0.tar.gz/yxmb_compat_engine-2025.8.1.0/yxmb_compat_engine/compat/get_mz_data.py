import logging
import re
from datetime import datetime
from typing import Tuple

from kapybara import By, ec, WebDriverWait, FormElement
from kapybara.hightlight_text import highlight_text
from phis_config import Config, AdminConfig


def get_selected_mz_data(all_data, choice_dates):
    logging.info(highlight_text('获取门诊数据'))
    r2 = []
    for date in choice_dates:
        for d, r in all_data:
            if d == date:
                r['随访日期:'] = d
                r2.append(r)
                break

    logging.info('获取门诊数据:%s', r2)
    return r2


def get门诊数据(
    driver, record: dict[str, int], headers: list[str]
) -> Tuple[list[str], list]:
    """
    遍历表格，获取所有在随访起始和结束时间之内的门诊时间

    函数参数

    record : dict
        {'身份证号': 110107197403170328}
    headers : list[str]
        ['身份证号']

    参数配置：admin.txt

    配置内容：
        - 随访新建起始时间:2025-04-01
        - 随访新建结束时间:2025-04-30

    **门诊日期布局示例:**

    .. image:: /_static/images/all_clinic_dates.png
       :alt: 所有门诊日期
       :align: center
       :width: 70%
    """
    global Config, AdminConfig
    place = Config.机构名称
    logging.info('需要判断的机构名称: %s', place)

    start_date = AdminConfig.随访新建起始时间
    end_date = AdminConfig.随访新建结束时间
    logging.info('随访新建起始时间: %s', start_date)
    logging.info('随访新建结束时间: %s', end_date)

    require = False
    doctor = ''
    # 判断是否需要根据签约医生来获取门诊日期
    if '签约医生' in headers:
        doctor = record['签约医生'].strip()
        logging.info(f'需要根据签约医生{doctor}来获取门诊日期')
        require = True
    # 判断当前是否在门诊服务页面
    driver.switch_to.default_content()
    form = driver.find_element(By.CSS_SELECTOR, 'iframe')
    url = form.get_attribute('src')
    if 'app/svc/clinic' not in url:
        FormElement('门诊服务', 'menu_6').click()

    # 切换到第一个 iframe
    driver.switch_to.default_content()
    first_iframe = FormElement('iframe', '//*[@id="ext-gen21"]/iframe').element
    driver.switch_to.frame(first_iframe)

    FormElement('读取中', '//div[contains(text(),"读取中")]').wait_until_disappeared()
    # 获取页脚值
    page_number = FormElement('页脚', '//*[@id="ext-comp-1006"]').text

    # 获取总页数
    count_number = re.findall(r'\d+', page_number)
    logging.info('门诊总页数: %s', count_number)

    data_list = []
    minimiumDateReached = False
    result = []  # list of (date, dict[key, value])

    for i in range(0, int(count_number[0])):
        if minimiumDateReached:
            break
        try:
            # 获取div下子div的数量
            WebDriverWait(driver, 40).until(
                ec.presence_of_element_located(
                    (
                        By.XPATH,
                        '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div/child::div',
                    )
                )
            )
            div_elements = driver.find_elements(
                By.XPATH,
                '/html/body/div[1]/div/div[1]/div/div[1]/div[2]/div/child::div',
            )
        except Exception as e:
            logging.info(e)
            logging.info(f'没有门诊记录')
            return data_list, result
        for j in range(1, len(div_elements) + 1):
            # 获取门诊机构名称
            name = FormElement(
                '门诊机构',
                f'//*[@id="ext-gen22"]/div[{j}]/table/tbody/tr[1]/td[3]/div',
            ).text

            doctor_name = FormElement(
                '医生姓名',
                f'//*[@id="ext-gen22"]/div[{j}]/table/tbody/tr[1]/td[4]/div',
            ).text

            if place in name:
                # logging.info(f"当前选中的机构名称: {name}")
                # 获取门诊日期
                date_element = FormElement(
                    '门诊日期',
                    f'//*[@id="ext-gen22"]/div[{j}]/table/tbody/tr[1]/td[2]/div',
                )
                date = date_element.text
                # logging.info(f"门诊日期: {date}")
                date_object = datetime.strptime(date, '%Y-%m-%d')
                if date_object < datetime.strptime(start_date, '%Y-%m-%d'):
                    minimiumDateReached = True
                    break
                from selenium.webdriver import ActionChains

                ActionChains(driver).double_click(date_element.element).perform()
                needData_element = FormElement(
                    '门诊数据详情',
                    f'//*[@id="ext-gen22"]/div[{j}]/table/tbody/tr[2]/td/div',
                )
                needData = needData_element.text

                # pattern = r'(身高|脉搏|舒张压|体温|收缩压|体重|空腹血糖):(\d+)'
                pattern = r'(身高|脉搏|舒张压|体温|收缩压|体重|空腹血糖)[:：](\d+)'
                matches = re.findall(pattern, needData)
                my_dict = {}
                for key, value in matches:
                    if key == '脉搏':
                        my_dict['心率'] = int(value)
                    else:
                        my_dict[key] = int(value)

                # if all_previous_data:
                #     my_dict = adjust_values(my_dict, all_previous_data)
                # 提取数据后关闭
                ActionChains(driver).double_click(date_element.element).perform()

                result.append([date, my_dict])

                if require:
                    if doctor == doctor_name:
                        if str(start_date) <= str(date) <= str(end_date):
                            # logging.info(f"{date}在{start_date}-{end_date}时间范围内")
                            data_list.append(date)
                else:
                    if str(start_date) <= str(date) <= str(end_date):
                        # logging.info(f"{date}在{start_date}-{end_date}时间范围内")
                        data_list.append(date)

        # 点击下一页按钮
        if i < int(count_number[0]) - 1:  # 如果不是最后一页，则继续翻页
            FormElement('下一页', '//*[@id="ext-gen43"]').click()

            # class: .ext-el-mask
            FormElement(
                '读取中', '//div[contains(text(),"读取中")]'
            ).wait_until_disappeared()

    FormElement('第一页', 'ext-gen32').click()
    return data_list, result
