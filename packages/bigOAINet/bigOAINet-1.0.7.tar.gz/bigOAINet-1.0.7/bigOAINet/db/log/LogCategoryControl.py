import mxupy as mu
import bigOAINet as bigo

from mxupy import IM, TreeEntityXControl

class LogCategoryControl(TreeEntityXControl):
    
    class Meta:
        model_class = bigo.LogCategory

    def __init__(self):
        
        paths = [
            mu.TreeDataPath(
                nameFieldName="name",
                namePathFieldName="namePath",
                isAllowRepeat=False,
                isAllowRepeatOfAll=True
            ),
        ]
        
        super().__init__(td=mu.TreeData(idFieldName='logCategoryId', paths=paths))


    # def add(self, name_path):
    #     im = IM()
    #     if not name_path:
    #         return im.error("添加失败，namePath不能为空。")
        
    #     categories = name_path.split('/')
    #     pid = 0
    #     for i, name in enumerate(categories):
    #         name_path = '/'.join(categories[:i+1])
    #         try:
    #             entity = LogCategory.get(LogCategory.name_path == name_path)
    #         except DoesNotExist:
    #             entity = LogCategory.create(
    #                 name=name,
    #                 parent_category_id=pid,
    #                 add_time=datetime.now()
    #             )
    #             im.result = entity.id
    #             if im.is_error:
    #                 return im
    #             pid = entity.id
    #         else:
    #             pid = entity.id
    #     return im

    # def delete(self, id, is_exists_verify=True):
    #     im = IM()
    #     try:
    #         if LogCategory.select().where(LogCategory.parent_category_id == id).exists():
    #             return im.error("删除失败，该分类下有子分类。")
    #         if LogControl.get_instance().exists(Condition("category_id", "=", id)):
    #             return im.error("删除失败，该分类下有注册项。")
    #         return super().delete(id, is_exists_verify)
    #     except DoesNotExist:
    #         return im.error("分类不存在。")
