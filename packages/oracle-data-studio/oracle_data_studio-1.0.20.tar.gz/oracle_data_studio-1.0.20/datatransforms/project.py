'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.
Copyright (c) 2023-2025, Oracle and/or its affiliates.

Provides APIs to create and manage Project in Data Transforms
'''

class Project:
    """Captures the project attributes 
    """
    def __init__(self,name,folder=None,code=None):
        self.name=name
        if folder is None:
            folder="DefaultFolder"

        self.folder=folder
        if code is not None:
            self.code=code.upper()
        else:
            self.code=name.replace(" ","").upper()
            #print("code is not none " + str(self.code) )
