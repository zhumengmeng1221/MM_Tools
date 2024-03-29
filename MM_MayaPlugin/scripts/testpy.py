import maya.cmds as cmds

def set_joint_rotation(joint):

    # 设置旋转顺序为 XYZ 并应用旋转
    cmds.setAttr(joint + ".rotateOrder", 0)  # 0 表示 XYZ
    cmds.rotate(0, 0, 0, joint)
    print("*******")

# 选择您要设置旋转的关节
selected_joints = cmds.ls(selection=True, type='joint')

# 设置关节的旋转值
def Test1():
    for joint in selected_joints:
        set_joint_rotation(joint)
