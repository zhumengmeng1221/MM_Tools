import maya.cmds as cmds

# 定义添加前缀的函数
def add_prefix_to_blendshapes(prefix):
    selected_objects = cmds.ls(selection=True, dag=True, type='transform')
    for obj in selected_objects:
        history = cmds.listHistory(obj)
        blend_shapes = cmds.ls(history, type='blendShape')
        for blend_shape in blend_shapes:
            targets = cmds.listAttr(blend_shape + '.w', m=True)
            for target in targets:
                new_name = prefix + target
                cmds.aliasAttr(new_name, blend_shape + '.' + target)
    cmds.text("statusText", edit=True, label="前缀已添加")

# 定义删除前缀的函数
def remove_prefix_from_blendshapes(prefix):
    selected_objects = cmds.ls(selection=True, dag=True, type='transform')
    for obj in selected_objects:
        history = cmds.listHistory(obj)
        blend_shapes = cmds.ls(history, type='blendShape')
        for blend_shape in blend_shapes:
            targets = cmds.listAttr(blend_shape + '.w', m=True)
            for target in targets:
                if target.startswith(prefix):
                    new_name = target[len(prefix):]
                    cmds.aliasAttr(new_name, blend_shape + '.' + target)
    cmds.text("statusText", edit=True, label="前缀已删除")

# 创建UI窗口
def create_bsui():
    if cmds.window("prefixWindow", exists=True):
        cmds.deleteUI("prefixWindow")
    
    window = cmds.window("prefixWindow", title="Blend Shape 前缀管理", widthHeight=(300, 150))
    cmds.columnLayout(adjustableColumn=True)
    
    cmds.text(label="输入前缀:")
    prefix_field = cmds.textField("prefixField")
    
    cmds.button(label="增加前缀", command=lambda x: add_prefix_to_blendshapes(cmds.textField(prefix_field, query=True, text=True)))
    cmds.button(label="删除前缀", command=lambda x: remove_prefix_from_blendshapes(cmds.textField(prefix_field, query=True, text=True)))
    
    cmds.text("statusText", label="", align="center")
    
    cmds.showWindow(window)


