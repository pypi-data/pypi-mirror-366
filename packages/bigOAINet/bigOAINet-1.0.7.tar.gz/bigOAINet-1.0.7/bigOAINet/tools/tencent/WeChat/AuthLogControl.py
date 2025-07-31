import mxupy as mu

import bigOAINet as bigo
class AuthLogControl(mu.EntityXControl):
    class Meta:
        model_class = bigo.AuthLog
        
    def printTableName(self):
        print(self.table_name)
        
        
if __name__ == '__main__':
    print('authLogControl.table_name')