'''
Author: XDTEAM
Date: 2025-07-16 01:26:06
LastEditTime: 2025-07-16 01:41:32
LastEditors: XDTEAM
Description: 
'''
from .ql import ql_api


class qllog(ql_api):
    """
    青龙面板api日志模块

    url: 青龙面板IP地址(不包含http://)

    post: 青龙面板端口

    client_id: 青龙面板openapi登录用户名

    client_secret: 青龙面板openapi登录密码

    Usage::
        >>> ql_log = qllog(
            url="12.22.43.23",
            port=5700,
            client_id="admin",
            client_secret="abcdefg_",
        )
        ql_log.list()
    """
    def __init__(self, url: str, post: int, client_id: str, client_secret: str):
        super().__init__(url, post, client_id, client_secret)

    async def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized:
            await self.initialize()

    async def list(self):
        """获取日志文件列表

        :return: 源相应json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/logs"
        res = await self.s.get(url=url)
        return res.json()

    async def get_cron_log(self, cron_id: int | str):
        """
        获取指定定时任务的运行日志（与 curl 示例等效）

        :param cron_id: 任务 id，对应 url 里的 /crons/{id}/log
        :return: requests.Response 对象
        """
        await self._ensure_initialized()
        url = f"{self.url}/api/crons/{cron_id}/log"

        res = await self.s.get(url=url)
        return res.json()
