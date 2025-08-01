'''
Author: XDTEAM
Date: 2025-07-16 01:26:06
LastEditTime: 2025-07-16 01:40:47
LastEditors: XDTEAM
Description: 
'''
from .ql import ql_api


class qldependence(ql_api):
    """
    青龙面板api依赖管理模块

    url: 青龙面板IP地址(不包含http://)

    post: 青龙面板端口

    client_id: 青龙面板openapi登录用户名

    client_secret: 青龙面板openapi登录密码

    Usage::
        >>> ql_dependence = qldependence(
            url="12.22.43.23",
            port=5700,
            client_id="admin",
            client_secret="abcdefg_",
        )
        ql_dependence.get()
    """
    def __init__(self, url: str, post: int, client_id: str, client_secret: str):
        super().__init__(url, post, client_id, client_secret)
        self.dependence_url = f"{self.url}/open/dependence"

    async def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized:
            await self.initialize()

    async def get(self):
        """
        获取已安装依赖列表

        :return: 源响应json
        """
        await self._ensure_initialized()
        res = await self.s.get(self.dependence_url)
        return res.json()
