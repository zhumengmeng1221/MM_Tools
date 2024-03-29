#/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import shutil
import getpass

def search(root, target):
  items = os.listdir(root)
  for i in items:
    Path = root + '\\' + os.path.basename(i)
    if os.path.isdir(Path)and i != target:
      temp = search(Path, target)
      if temp == None:
        pass
      else:
        return temp
    else:
      if i == target and 'zh_CN'in Path:
        print(Path)
        return Path
      else:
        pass
      pass
    pass
  return None

myDir = os.getcwd()
print(myDir)
#获得用户名，类似于admin这种
UserName = getpass.getuser()
#定义Maya工具架的位置
MayaPath = ''
#这个是我们的做好的工具架所在的地方
ToolShelfPath = myDir + '\\' + 'shelf_Polygons.mel'
print(ToolShelfPath)
#这行代码属于无奈之举，我只能默认安装在C盘，当然如果安装在D盘或者别的盘，
#也可以根据具体情况总结规律进行定位查找（不定位随意查会遇到无数权限报错）
path_C = 'C:\\Users\\'+ UserName +'\\Documents\\maya'
#这几行代码是为了搜索到Maya工具架所在的文件夹，定位Maya的工具架位置，
listDir = os.listdir(path_C)
for i in listDir:
  if os.path.isdir(path_C + '\\' + i):
    root = path_C + '\\' + i
    os.chdir(root)
    target = 'shelf_Polygons.mel'
    s = search(root, target)
    print(s)
    if s == None:
      s = ''
    else:
      MayaPath = s
  else:
    pass
print(MayaPath)

#找到了工具架位置，就可以欢快地把准备好的工具复制过去了
if os.path.exists(MayaPath):
  os.remove(MayaPath)
  shutil.copy(ToolShelfPath, MayaPath[:-19])
else:
  shutil.copy(ToolShelfPath, MayaPath)
