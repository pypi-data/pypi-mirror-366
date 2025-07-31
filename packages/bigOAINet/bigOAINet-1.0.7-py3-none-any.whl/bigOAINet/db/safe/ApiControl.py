import bigOAINet as bigo
from typing import List
from mxupy import IM, EntityXControl
from functools import lru_cache

class ApiControl(EntityXControl):
    
    class Meta:
        model_class = bigo.Api
        
    def add_api(self, name: str, space: str, codes: str, sort: int = 0, desc: str = "") -> IM:
        """
        添加API
        
        Args:
            name: 名称
            space: 空间
            codes: 编码(支持正则，不能重复)
            sort: 排序
            desc: 描述
            
        Returns:
            IM: 操作结果
        """
        sup = super()
        
        def _do():
        
            im = IM()

            if not name:
                return im.set_error("添加失败，名称不能为空。")
            if not space:
                return im.set_error("添加失败，空间不能为空。")
            if not codes:
                return im.set_error("添加失败，编码不能为空。")

            # 检查编码是否已存在
            if (im := self.exists([{'space':space}, {'codes':codes}])).error:
                return im
            if im.data is True:
                return im.set_error("添加失败，编码已经存在。")

            if (im := sup.add({'name':name, 'space':space, 'codes':codes, 'desc':desc, 'sort':sort})).error:
                return im
            
            return im
        
        return self.run(_do)

    def delete_api(self, apiId: int) -> IM:
        """删除API
        
        Args:
            apiId: API ID
            is_exists_verify: 是否进行存在校验
            
        Returns:
            IM: 操作结果
        """
        sup = super()
        
        def _do():
            
            im = IM()

            # 检查API是否存在
            if (im := sup.exists({'apiId':apiId})).error:
                return im
            if im.data is False:
                return im.set_error("删除失败，该 API 不存在。")

            # 检查是否被访问规则引用
            if (im := bigo.RuleControl.inst().exists({'apiId':apiId})).error:
                return im
            if im.data is True:
                return im.set_error("删除失败，该 API 已被访问规则引用。")

            return sup.delete_by_id(apiId, False)
            
        return self.run(_do)

    @lru_cache(maxsize=10000)
    def get_ids(self, functionName: str) -> List[int]:
        """ 通过函数名获取API ID列表
        
        Args:
            functionName: 函数名称
            
        Returns:
            List[int]: API ID列表
        """
        if not functionName:
            return []

        api_ids = []

        # 第一步：获取所有API并按空间过滤
        if (im := self.get_list(order_by={'space':'asc'})).error:
            return []
        apis = im.data
        apis = [api for api in apis if functionName.startswith(api.space)]

        # 第二步：通过正则精准过滤
        for api in apis:
            # 移除空间前缀
            codes = functionName[len(api.space) + 1:] if api.space else functionName
            
            allowed_codes = [c.strip() for c in api.codes.split(",")]
            if "*" in allowed_codes or any(allowed_code in codes for allowed_code in allowed_codes):
                api_ids.append(api.apiId)
                continue

        return api_ids


