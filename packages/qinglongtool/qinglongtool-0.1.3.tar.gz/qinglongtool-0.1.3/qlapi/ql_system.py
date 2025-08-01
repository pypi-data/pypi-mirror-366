'''
Author: XDTEAM
Date: 2025-07-16 01:26:06
LastEditTime: 2025-07-16 01:42:17
LastEditors: XDTEAM
Description: 
'''
from .ql import ql_api


class qlsystem(ql_api):
    """
    青龙面板api系统模块

    url: 青龙面板IP地址(不包含http://)

    post: 青龙面板端口

    client_id: 青龙面板openapi登录用户名

    client_secret: 青龙面板openapi登录密码

    Usage::
        >>> ql_system = qlsystem(
            url="12.22.43.23",
            port=5700,
            client_id="admin",
            client_secret="abcdefg_",
        )
        ql_system.version()
    """
    def __init__(self, url: str, post: int, client_id: str, client_secret: str):
        super().__init__(url, post, client_id, client_secret)

    async def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized:
            await self.initialize()

    async def version(self) -> dict:
        """
        获取面板版本信息

        :return: 源相应json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/system"
        res = await self.s.get(url)
        return res.json()

    async def get_log_remove(self) -> dict:
        """
        获取清除面板日志频率

        :return: 源相应json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/system/log/remove"
        res = await self.s.get(url)
        return res.json()

    async def change_log_remove(self, frequency: int) -> dict:
        """
        修改清除面板日志频率

        :param log_remove: 日志清除频率,单位天
        :return: 源相应json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/system/log/remove"
        data = {"frequency": frequency}
        res = await self.s.put(url, json=data)
        return res.json()

    async def update_check(self) -> dict:
        """
        检查面板更新

        :return: 源相应json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/system/update-check"
        res = await self.s.put(url)
        return res.json()

    async def update(self) -> dict:
        """
        更新面板

        :return: 源相应json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/system/update"
        res = await self.s.put(url)
        return res.json()
