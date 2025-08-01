'''
Author: XDTEAM
Date: 2025-07-15 22:24:04
LastEditTime: 2025-07-29 22:24:12
LastEditors: XDTEAM
Description: 
'''
import httpx

class ql_api:
    def __init__(self, url: str, port: int, client_id: str, client_secret: str):
        """初始化

        :param url: 面板ip地址
        :param port: 面板端口
        :param client_id: client_id
        :param client_secret: client_secret
        """
        self.url = f"http://{url}:{port}"
        self.client_id = client_id
        self.client_secret = client_secret
        self.s = httpx.AsyncClient()
        self._initialized = False

    async def initialize(self):
        """手动初始化连接和token"""
        if not self._initialized:
            await self.__get_ql_token()
            self._initialized = True

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口，确保 httpx 客户端关闭"""
        await self.s.aclose()

    @classmethod
    async def create(cls, url: str, port: int, client_id: str, client_secret: str):
        self = cls(url, port, client_id, client_secret)
        return self

    async def __get_ql_token(self):
        url = f"{self.url}/open/auth/token?client_id={self.client_id}&client_secret={self.client_secret}"
        res = await self.s.get(url)
        res_json = res.json()
        token = res_json["data"]['token']
        self.s.headers.update({"authorization": "Bearer " + str(token)})
        if res.status_code == 200:
            return "青龙登录成功！"