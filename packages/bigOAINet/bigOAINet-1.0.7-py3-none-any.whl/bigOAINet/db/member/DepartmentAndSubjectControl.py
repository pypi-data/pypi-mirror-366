import mxupy as mu
import bigOAINet as bigo

class DepartmentAndSubjectControl(mu.EntityXControl):
    class Meta:
        model_class = bigo.DepartmentAndSubject
        
        
        
        
        
        
        
if __name__ == '__main__':
    
    print(DepartmentAndSubjectControl.inst().table_name)