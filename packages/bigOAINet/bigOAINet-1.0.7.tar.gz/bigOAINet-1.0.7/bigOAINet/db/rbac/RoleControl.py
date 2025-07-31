import mxupy as mu
import bigOAINet as bigo

class RoleControl(mu.EntityXControl):
    class Meta:
        model_class = bigo.Role
        
    def get_count(self, where):
        
        a = super()
        def _do():
            
            im = a.get_count(where=where)
            if im.error:
                return im
            im = self.inst().get_list(where={'id':1})
            if im.error:
                return im
            return im

        return self.run(_do)
        
# global roleControl
# roleControl = RoleControl()
        
if __name__ == '__main__':
    
    im = RoleControl.inst().get_count(where={'id':1})
    print(im)
    
    # print(roleControl.table_name)