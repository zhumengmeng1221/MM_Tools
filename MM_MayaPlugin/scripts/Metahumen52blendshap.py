# _*_ coding:utf-8 _*_
import maya.cmds as cmds
from PySide2 import QtWidgets
import maya.mel as mel

   
# 9个组名称
group_names = ['head', 'teeth', 'saliva', 'eyeLeft', 'eyeRight', 'eyeshell', "eyelashes", "cartilage", 'eyeEdge']
groups = {}
csvfile=""
class BS:
    def __init__(self):
        self.winName = '52BlendShap'
       
    def Metahumen52BSCreate(self,csv):
        if cmds.window(self.winName, exists=True):
            cmds.deleteUI(self.winName)
        # 创建窗口
        window1 = cmds.window(self.winName,title='基于Metahumen生成52BlendShap', widthHeight=(400, 400))
        # 创建布局
        layout = cmds.columnLayout(adjustableColumn=True)
        
        global csvfile
        csvfile = csv
        # 创建按钮
        text1 = cmds.text(label='提示:按照顺序进行')
        button1 = cmds.button(label='1.创建9个空组1,并复制cartilage', command=self.button1_callback)
        button2 = cmds.button(label='2.读取text表格生成各组模型', command=self.button2_callback)
        button3 = cmds.button(label='3.复制头部模型', command=self.button3_callback)
        button4 = cmds.button(label='4.生成融合变形', command=self.button4_callback)
        button5 = cmds.button(label='5.删除9个新生成的组', command=self.button5_callback)
        text1 = cmds.text(label='提示:以下为眼球得操作，为unity材质准备，将操作轴移动到固定位置')
        button7 = cmds.button(label='解除选定模型平移旋转锁定', command=self.unlock_translation_rotation_selected)
        button6 = cmds.button(label='眼球Z轴向前，执行完请烘焙枢轴', command=self.execute_mel_code)


        # 创建文本控件并设置文字内容
        text = cmds.text(label='版本:V1.0')
        cmds.text(text, edit=True, parent=layout)
        cmds.text(text1, edit=True, parent=layout)

        cmds.showWindow(window1)
    # 定义按钮的回调函数
    def button1_callback(self,*args):
        # 1.创建9个空组
        for group_name in group_names:
            group = cmds.group(empty=True, name=group_name)
            groups[group_name] = group
        # 2.对cartilage进行复制.
        if cmds.objExists("cartilage_lod2_mesh"):
            print("cartilage_lod2_mesh已经在场景中")
        else:
            # 复制 cartilage_lod1_mesh 模型并放入 head_lod2_grp 组中
            duplicate_mesh = cmds.duplicate("cartilage_lod1_mesh")[0]
            cmds.parent(duplicate_mesh, "head_lod2_grp")
            # 重命名模型为 cartilage_lod2_mesh
            cmds.rename(duplicate_mesh, "cartilage_lod2_mesh")
    def button2_callback(self,*args):
        with open(csvfile, 'r') as file:
            for line in file.readlines():
                data = line.strip().split(";")
                # 3.遍历数据复制对应得模型到组中
                blendshape_name = data[0]  # 融合变形的名称
                controller_data = data[1]  # 控制器的数据
                model_objects = data[2].split(',')

                # 分离控制器名称和平移数值
                controller_values = controller_data.split(',')
                # 保存初始控制器数值的字典
                initial_values = {}
                # 遍历每个控制器的数据
                for controller_value in controller_values:
                    controller_name, translation_value = controller_value.split('=')
                    translation_value = (translation_value.split('|'))
                    target_value = float(translation_value[0])

                    # 给控制器赋值
                    if len(translation_value) == 1:
                        # 如果控制器名称不在初始值字典中，则保存其初始值
                        if controller_name not in initial_values:
                            initial_values[controller_name] = cmds.getAttr(controller_name + ".translateY")
                        cmds.setAttr(controller_name + ".translateY", float(translation_value[0]))
                    elif len(translation_value) == 2:
                        # 如果控制器名称不在初始值字典中，则保存其初始值
                        if controller_name not in initial_values:
                            initial_values[controller_name] = [cmds.getAttr(controller_name + ".translateX"),
                                                            cmds.getAttr(controller_name + ".translateY")]
                        cmds.setAttr(controller_name + ".translateX", float(translation_value[0]))
                        cmds.setAttr(controller_name + ".translateY", float(translation_value[1]))
                # 复制模型并放入组中
                for blend_target in model_objects:
                    prefix = blend_target.split('_')[0]  # 提取前缀，类型分开存放不同的组中
                    group = groups.get(prefix)  # 获取对应的组
                    if group:
                        duplicate_mesh = cmds.duplicate(blend_target)[0]
                        cmds.parent(duplicate_mesh, group)
                        cmds.rename(duplicate_mesh, blendshape_name)
                # 恢复控制器数值为初始值
                for controller_name, initial_value in initial_values.items():
                    if isinstance(initial_value, float):
                        cmds.setAttr(controller_name + ".translateY", initial_value)
                    else:
                        cmds.setAttr(controller_name + ".translateX", initial_value[0])
                        cmds.setAttr(controller_name + ".translateY", initial_value[1])
    def button3_callback(self,*args):
        # 复制组并放到最外层
        new_group = cmds.duplicate('head_lod2_grp', name='head_groups')[0]
        cmds.parent(new_group, world=True)
    def button4_callback(self,*args):
        # 4. 遍历每个组，并添加目标形状
        def select_group_models(group_name):
            models = cmds.listRelatives(group_name, type='transform', fullPath=True)
            if models:
                cmds.select(models, replace=True)
                return True
            else:
                return False

        for group_name in group_names:
            if select_group_models(group_name):
                full_path = cmds.ls("head_groups|" +group_name + "_lod2_mesh", long=True)[0]
                print(full_path)
                cmds.select(full_path, add=True)
                # 生成融合变形
                blendshape_name = group_name
                cmds.blendShape(frontOfChain=True, origin="local", name=blendshape_name)
            else:
                print(group_name + "null")
    def button5_callback(self,*args):
        # 5.遍历每个组并删除组以及组中的所有模型
        def delete_group(group_name):
            cmds.delete(group_name)

        for group_name in group_names:
            delete_group(group_name)
    def button6_callback(self,*args):
        full_path = cmds.ls("head_groups" + "|" + "head_lod2_mesh", long=True)
        print(full_path[0])
    def execute_mel_code(self,*args):
    #移动操纵轴
        obj = "head_groups|eyeLeft_lod2_mesh"
        obj1 = "head_groups|eyeRight_lod2_mesh"
        # 指定要移动到的坐标点
        target_position = (2.932, -9.127, 151.068)
        target_position1 = (-3.033, -9.141, 151.098)
        if cmds.objExists(obj):
            # 将操作轴移动到指定坐标点
            cmds.xform(obj, worldSpace=True, pivots=target_position)
            print("操作轴移动成功 模型: {}".format(obj))
        else:
            print("模型 {} 没有，检查是否存在".format(obj))
        if cmds.objExists(obj1):
            # 将操作轴移动到指定坐标点
            cmds.xform(obj1, worldSpace=True, pivots=target_position1)
            print("操作轴移动成功 模型: {}".format(obj1))
        else:
            print("模型 {} 没有，检查是否存在".format(obj1))
    #旋转操纵轴
        full_path1 = cmds.ls("head_groups|eyeLeft_lod2_mesh", long=True)[0]
        full_path2 = cmds.ls("head_groups|eyeRight_lod2_mesh", long=True)[0]
        cmds.select(full_path1)
        cmds.select(full_path2,add=True)
        mel_code = 'manipPivot -o 90 0 0 ;'
        mel.eval(mel_code)
    def unlock_translation_rotation_selected(*args):
        selection = cmds.ls(selection=True)
        if selection:
            for obj in selection:
                # 解除平移和旋转锁定项
                cmds.setAttr(obj + ".translateX", lock=False)
                cmds.setAttr(obj + ".translateY", lock=False)
                cmds.setAttr(obj + ".translateZ", lock=False)
                cmds.setAttr(obj + ".rotateX", lock=False)
                cmds.setAttr(obj + ".rotateY", lock=False)
                cmds.setAttr(obj + ".rotateZ", lock=False)
                print("已解锁平移旋转锁定 object: {}".format(obj))
        else:
            print("没有选中模型")


