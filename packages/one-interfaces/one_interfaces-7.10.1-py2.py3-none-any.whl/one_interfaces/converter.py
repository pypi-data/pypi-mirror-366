import re
import os
files =os.listdir()
try:
    files.remove('__pycache__')
except:
    pass
files.remove('__init__.py')
files.remove('converter.py')
exp =re.compile("import .*_pb2")

print(files)
for file in files:
    f =open(file, 'r+')
    lines =f.readlines()
    newLines =[]     
    for line in lines:
        try:
            t =re.match(exp, line).group()
            line = "from . "+ line
            newLines.append(line)
        except (AttributeError):
            newLines.append(line)          
    f.close()
    f=open(file,'w+')
    f.writelines(newLines)
    f.close()