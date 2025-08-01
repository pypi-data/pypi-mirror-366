from .ql import ql_api

class qlscript(ql_api):
    """
    青龙面板api脚本管理模块

    url: 青龙面板IP地址(不包含http://)

    post: 青龙面板端口

    client_id: 青龙面板openapi登录用户名

    client_secret: 青龙面板openapi登录密码

    Usage::
        >>> ql_script = qlscript(
            url="12.22.43.23",
            port=5700,
            client_id="admin",
            client_secret="abcdefg_",
        )
        ql_script.get_all()
    """

    def __init__(self, url: str, post: int, client_id: str, client_secret: str):
        super().__init__(url, post, client_id, client_secret)
        self.script_url = f"{self.url}/open/scripts/"

    async def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized:
            await self.initialize()

    async def get_all(self):
        """
        获取所有脚本列表

        :return: 源响应json
        """
        await self._ensure_initialized()
        url = self.script_url + 'files'
        res = await self.s.get(url)
        return res.json()

    async def get_script(self, name: str):
        """
        获取脚本详情

        :param name: 脚本名称
        :return: 源响应json
        """
        await self._ensure_initialized()
        url = self.script_url + name
        res = await self.s.get(url)
        return res.json()

    async def add(self, filename: str, path: str, content: str, originFilename: str) -> dict:
        """
        添加脚本

        :param filename: 脚本名称
        :param path: 脚本路径
        :param content: 脚本内容
        :param originFilename: 脚本原始名称
        :return: 源响应json
        """
        await self._ensure_initialized()
        url = self.script_url
        data = {
            "filename": filename,
            "path": path,
            "content": content,
            "originFilename": originFilename
        }
        res = await self.s.post(url, json=data)
        return res.json()

    async def update(self, filename: str, path: str, content: str) -> dict:
        """
        更新脚本

        :param filename: 脚本名称
        :param path: 脚本路径
        :param content: 脚本内容
        :return: 源响应json
        """
        await self._ensure_initialized()
        url = self.script_url
        data = {
            "filename": filename,
            "path": path,
            "content": content
        }
        res = await self.s.put(url, json=data)
        return res.json()

    async def delete(self, path:str,filename: str) -> dict:
        """
        删除脚本

        :param path: 脚本路径
        :param filename: 脚本名称
        :return: 源响应json
        """
        await self._ensure_initialized()
        url = self.script_url
        data = {
            "path": path,
            "filename": filename
        }
        res = await self.s.delete(url,json=data)
        return res.json()

    async def download(self, filename: str) -> dict:
        """
        下载脚本

        :param filename: 脚本名称
        :return: 源响应json
        """
        await self._ensure_initialized()
        url = self.script_url + "download"
        data = {
            "filename": filename
        }
        res = await self.s.post(url,json=data)
        return res.json()

    async def run(self, path:str,filename: str) -> dict:
        """
        运行脚本

        :param path: 脚本路径
        :param filename: 脚本名称
        :return: 源响应json
        """
        await self._ensure_initialized()
        url = self.script_url + "run"
        data = {
            "filename": filename,
            "path": path
        }
        res = await self.s.put(url,json=data)
        return res.json()

    async def stop(self, path:str,filename: str) -> dict:
        """
        停止脚本

        :param path: 脚本路径
        :param filename: 脚本名称
        :return: 源响应json
        """
        await self._ensure_initialized()
        url = self.script_url + "stop"
        data = {
            "filename": filename,
            "path": path
        }
        res = await self.s.put(url,json=data)
        return res.json()
