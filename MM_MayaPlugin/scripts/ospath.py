# import sys
# import os
# def syspath():
#     temp = os.path.dirname(os.path.abspath(__file__))
#     temp =  "/".join(temp.split("\\"))
#     if temp not in sys.path:
#         sys.path.append(temp)

# -*- coding: UTF-8 -*-
import psutil
import maya.cmds as cmds

# 查找运行中的Maya进程
maya_executable_path = None
for process in psutil.process_iter(['pid', 'name']):
    try:
        if "maya.exe" in process.info['name'].lower():
            maya_process = psutil.Process(process.info['pid'])
            maya_executable_path = maya_process.exe()
            break
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

# 检查是否找到Maya的可执行文件路径
if maya_executable_path:
    # 获取Maya的版本号，可以根据需要修改
    maya_version = "2023"  # 例如，这里使用Maya 2022的版本号

    # 创建Maya菜单
    menu_name = "MyCustomMenu"
    if not cmds.menu(menu_name, exists=True):
        cmds.menu(menu_name, label="My Custom Menu", parent="MayaWindow")
        cmds.menuItem(label="MenuItem1", command="print('MenuItem1 Clicked!')")
        cmds.menuItem(label="MenuItem2", command="print('MenuItem2 Clicked!')")
    else:
        cmds.warning(f"Menu '{menu_name}' already exists.")

else:
    cmds.warning("Maya executable path not found. Please make sure Maya is running.")

