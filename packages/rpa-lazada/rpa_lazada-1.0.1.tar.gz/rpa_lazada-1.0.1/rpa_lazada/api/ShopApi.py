from rpa_common import Env
from rpa_common.library import Request
from rpa_common.service import ExecuteService
from rpa_common.request import TaskRequest

env = Env()
request = Request()
executeService = ExecuteService()
taskRequest = TaskRequest()

class ShopApi():
    def __init__(self):
        super().__init__()
        self.host = env.get().get('api','')

    def getInfoList(self, driver, options):
        '''
        @Desc    : 获取店铺信息
        @Author  : 洪润涛
        @Time    : 2024/07/21 18:15:22
        '''
        # 获取用户信息
        url = 'https://gsp.lazada.com/api/account/manage/query.do?_timezone=-8&tab=account'
        driver.get(url)
        response = executeService.request(driver, url, method="GET")
        return response

