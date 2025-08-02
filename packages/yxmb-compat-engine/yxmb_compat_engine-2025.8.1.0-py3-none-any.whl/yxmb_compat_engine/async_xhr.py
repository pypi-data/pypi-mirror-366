"""
后台发送异步请求获取病人ID
"""


from selenium.webdriver.support.ui import WebDriverWait
import json
import time  # For explicit waits if needed
from kapybara.shared_data import shared_data
from kapybara import WebDriver


def get_async_xhr(id_number, org_code: str) -> int:
    """
    对应界面中输入身份证号并进行查询的 JavaScript 代码

    返回值：病人在系统中的编号，通过该编号可以构造URL打开病人主页
    """
    driver: WebDriver = shared_data.driver

    # 1. Define the payload as a Python dictionary
    payload = {
        'ehrBaseFilterMap': {
            'EQ_gender': '',
            'GTE_birthDate': '',
            'LTE_birthDate': '',
            'LIKE_innerCode': '%',
            'GTE_dateCreated': '',
            'LTE_dateCreated': '',
            'EQ_signTeamCode': '',
            'LIKE_addrCode': None,
            'EQ_curContract': '',
            'EQ_individualConStatus': '',
            'EQ_creator': '',
            'EQ_idNumber': str(id_number),
            'LIKE_ehrCode': '%',
            # 'EQ_mngOrgCode': '0626',   # 对应界面中未选择“包含子机构”
            'LIKE_mngOrgCode': f'{org_code}%',  # 对应界面中选择“包含子机构”
            'LIKE_nameIndex': '%',
            'EQ_grChronicDisease': '1',
        },
        'ehrHfIndictorMap': {},
        'ehrClassifyGrFilterMap': {},
        'ehrClassifyCdFilterMap': {},
        'ehrClassifySpFilterMap': {},
        'grRelation': 'OR',
        'cdRelation': 'OR',
        'spRelation': 'OR',
        'fetchIdType': True,
        'fetchEhrDetail': True,
        'fetchHasFirstSoap': True,
        'fetchFamily': True,
    }

    # 2. Convert the dictionary to a JSON string
    json_payload = json.dumps(payload)
    dch = str(int(time.time() * 1000))

    # 3. Modify JavaScript to accept the payload and dch as arguments
    js_code = """
    var payload = arguments[0];
    var dch = arguments[1];
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/phis/app/ehr?limit=18&start=0&_dch=' + dch, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    // Define a callback function for when the request completes
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) { // Request is complete
            if (xhr.status === 200) { // Success
                window.xhrResponse = xhr.responseText; // Store the response text
                window.xhrStatus = xhr.status;
                window.xhrReady = true; // Flag to indicate completion
            } else { // Error
                window.xhrResponse = null;
                window.xhrStatus = xhr.status;
                window.xhrReady = true;
                console.error('XHR failed with status:', xhr.status);
            }
        }
    };

    xhr.send(payload);

    // Initialize flags to false, so Python knows to wait
    window.xhrReady = false;
    window.xhrResponse = null;
    window.xhrStatus = null;
    """

    # 4. Execute the JavaScript, passing the JSON string and dch as arguments
    driver.execute_script(js_code, json_payload, dch)

    # Now, wait for the XHR to complete and the response to be available
    # You can use WebDriverWait for a more robust waiting mechanism
    try:
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return window.xhrReady;') is True
        )

        response_text = driver.execute_script('return window.xhrResponse;')
        status_code = driver.execute_script('return window.xhrStatus;')

        # print(f'XHR Status: {status_code}')
        # print(f'XHR Response: {response_text}')

        # If the response is JSON, parse it
        if response_text and status_code == 200:
            try:
                json_response = json.loads(response_text)
                # print(f'Parsed JSON Response: {json_response}')
                if len(json_response['content']) > 0:
                    return json_response['content'][0]['id']
                else:
                    return -1
            except json.JSONDecodeError:
                print('Response is not valid JSON.')
            except Exception as _e:
                return -1
        else:
            return -1

    except Exception as e:
        print(f'Error waiting for XHR response: {e}')
        return -1
