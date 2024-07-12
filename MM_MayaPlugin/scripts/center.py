import maya.cmds as cmds

def reset_pivots_to_origin():
    # 获取场景中所有模型
    all_models = cmds.ls(type='transform', long=True)

    # 遍历每个模型
    for model in all_models:
        # 将模型的坐标轴（pivot）重置到原点
        cmds.xform(model, pivots=[0, 0, 0], worldSpace=True)

        # 打印信息
        print(f"Reset pivot of {model} to [0, 0, 0]")

# 调用函数
reset_pivots_to_origin()

