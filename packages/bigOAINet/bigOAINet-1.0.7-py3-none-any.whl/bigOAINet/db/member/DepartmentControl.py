import mxupy as mu
import bigOAINet as bigo

class DepartmentControl(mu.EntityXControl):
    class Meta:
        model_class = bigo.Department
        
        
        
        
        
        
        
if __name__ == '__main__':
    
    print(DepartmentControl.inst().table_name)