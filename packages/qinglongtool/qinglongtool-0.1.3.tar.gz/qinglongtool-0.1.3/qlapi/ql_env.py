import json
from typing import List, Dict, Any
from .ql import ql_api


def optimize_search_result(raw: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    以 name 为主键聚合原始数据，返回
    """
    container: Dict[str, List[Dict[str, Any]]] = {}

    for item in raw:
        name = item.get("name")
        container.setdefault(name, []).append(item)

    return container


class qlenv(ql_api):
    """
    青龙面板api环境变量模块

    url: 青龙面板IP地址(不包含http://)

    post: 青龙面板端口

    client_id: 青龙面板openapi登录用户名

    client_secret: 青龙面板openapi登录密码

    Usage::
        >>> ql_env = qlenv(
            url="12.22.43.23",
            port=5700,
            client_id="admin",
            client_secret="abcdefg_",
        )
        ql_env.list()
    """
    def __init__(self, url: str, post: int, client_id: str, client_secret: str):
        super().__init__(url, post, client_id, client_secret)

    async def _ensure_initialized(self):
        """确保已初始化"""
        if not self._initialized:
            await self.initialize()

    async def add(self, name, value, remarks=""):
        """
        添加环境变量

        :param new_env: 新环境变量名
        :param value: 新环境变量值
        :param remarks: 新环境变量值的备注信息
        :return:  响应结果json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs"
        data = [{"value": value, "name": name, "remarks":remarks}]
        res = await self.s.post(url=url, json=data)
        return res.json()

    async def delete(self, id):
        """
        删除环境变量

        :param id: 环境变量ID
        :return: 响应结果json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs"
        res = await self.s.delete(url=url, data=[id])
        return res.json()

    async def search(self, search_value: str = None, name: str = None):
        """
        获取环境变量

        :param search_value: 用于模糊搜索 name, value, remarks 字段的值
        :param name: 指定获取某个 name 下的数据
        :return: 优化后的环境变量数据，以 name 为主键分组
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs"
        if search_value:
            url += f"?searchValue={search_value}"
        
        res = await self.s.get(url=url)
        res_json = res.json()
        data = res_json.get("data", [])

        if name:
            # 如果指定了 name，则在获取的数据中进行过滤
            filtered_data = [item for item in data if item.get("name") == name]
            return optimize_search_result(filtered_data)
        
        return optimize_search_result(data)

    async def update(self, value, name, id, remarks=""):
        """
        更新环境变量

        :param value: 新值
        :param name: 新名称
        :param id: 环境变量id
        :param remarks: 新备注
        :return: 响应结果json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs"
        data = {"value": value, "name": name, "remarks": remarks, "id": id}
        res = await self.s.put(url=url, json=data)
        return res.json()

    async def list(self):
        """
        获取所有环境变量

        :param id: 环境变量ID
        :return: 响应结果json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs/"
        res = await self.s.get(url=url)
        return res.json()

    async def get_by_id(self, id):
        """
        根据环境变量ID获取环境变量

        :param id: 环境变量ID
        :return: 响应结果json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs/{id}"
        res = await self.s.get(url=url)
        return res.json()

    async def enable(self, id_list: List[int]):
        """
        启用环境变量

        :param id_list: 环境变量ID列表
        :return: 响应结果json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs/enable"
        res = await self.s.put(url=url, json=id_list)
        return res.json()

    async def disable(self, id_list: List[int]):
        """
        禁用环境变量

        :param id_list: 环境变量ID列表
        :return: 响应结果json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs/disable"
        res = await self.s.put(url=url, json=id_list)
        return res.json()

    async def rename(self, id, name):
        """
        修改环境变量名

        :param id: id
        :param name: name
        :return: 响应结果json
        """
        await self._ensure_initialized()
        url = f"{self.url}/open/envs/name"
        data = {"ids": id, "name": name}
        res = await self.s.put(url=url, json=data)
        return res.json()
