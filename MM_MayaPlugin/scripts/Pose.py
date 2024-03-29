import maya.cmds as cmds

def PoseAToT():
    sel = cmds.ls(sl=True)
    
    clavicle = ["clavicle_r_drv", "clavicle_l_drv"]
    upperarm = ["upperarm_r_drv", "upperarm_l_drv"]
    lowerarm = ["lowerarm_r_drv", "lowerarm_l_drv"]
    hand = ["hand_r_drv", "hand_l_drv"]
    
    index = ["index_metacarpal_r_drv", "index_metacarpal_l_drv"]
    index_01 = ["index_01_r_drv", "index_01_l_drv"]
    index_02 = ["index_02_r_drv", "index_02_l_drv"]
    
    middle = ["middle_metacarpal_r_drv", "middle_metacarpal_l_drv"]
    middle_01 = ["middle_01_r_drv", "middle_01_l_drv"]
    middle_02 = ["middle_02_r_drv", "middle_02_l_drv"]
    
    ring = ["ring_metacarpal_r_drv", "ring_metacarpal_l_drv"]
    ring_01 = ["ring_01_r_drv", "ring_01_l_drv"]
    ring_02 = ["ring_02_r_drv", "ring_02_l_drv"]    
    
    pinky = ["pinky_metacarpal_r_drv", "pinky_metacarpal_l_drv"]
    pinky_01 = ["pinky_01_r_drv", "pinky_01_l_drv"]
    pinky_02 = ["pinky_02_r_drv", "pinky_02_l_drv"]    
    
    cmds.setAttr(clavicle[0] + ".jointOrient", -180, 90, 0, type="float3")
    cmds.setAttr(clavicle[1] + ".jointOrient", 0, 90, 0, type="float3")
    
    for joint in upperarm:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")
    for joint in lowerarm:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")
    for joint in hand:
        cmds.setAttr(joint + ".jointOrient", -90, 0, 0, type="float3")
    
    for joint in index:
        cmds.setAttr(joint + ".jointOrient", 0, 5, 0, type="float3")
    for joint in index_01:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")
    for joint in index_02:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")
    
    for joint in middle:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")
    for joint in middle_01:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")
    for joint in middle_02:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")    
    
    for joint in ring:
        cmds.setAttr(joint + ".jointOrient", 0, -5, 0, type="float3")
    for joint in ring_01:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")
    for joint in ring_02:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")        
    
    for joint in pinky:
        cmds.setAttr(joint + ".jointOrient", 0, -10, 0, type="float3")
    for joint in pinky_01:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")
    for joint in pinky_02:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")    
def PoseTToA():
    sel = cmds.ls(sl=True)
    
    clavicle = ["clavicle_r_drv", "clavicle_l_drv"]
    upperarm = ["upperarm_r_drv", "upperarm_l_drv"]
    lowerarm = ["lowerarm_r_drv", "lowerarm_l_drv"]
    hand = ["hand_r_drv", "hand_l_drv"]
    
    index = ["index_metacarpal_r_drv", "index_metacarpal_l_drv"]
    index_01 = ["index_01_r_drv", "index_01_l_drv"]
    index_02 = ["index_02_r_drv", "index_02_l_drv"]
    
    middle = ["middle_metacarpal_r_drv", "middle_metacarpal_l_drv"]
    middle_01 = ["middle_01_r_drv", "middle_01_l_drv"]
    middle_02 = ["middle_02_r_drv", "middle_02_l_drv"]
    
    ring = ["ring_metacarpal_r_drv", "ring_metacarpal_l_drv"]
    ring_01 = ["ring_01_r_drv", "ring_01_l_drv"]
    ring_02 = ["ring_02_r_drv", "ring_02_l_drv"]    
    
    pinky = ["pinky_metacarpal_r_drv", "pinky_metacarpal_l_drv"]
    pinky_01 = ["pinky_01_r_drv", "pinky_01_l_drv"]
    pinky_02 = ["pinky_02_r_drv", "pinky_02_l_drv"]    
    
    cmds.setAttr(clavicle[0] + ".jointOrient", -180, 85, 0, type="float3")
    cmds.setAttr(clavicle[1] + ".jointOrient", 0, 95, 0, type="float3")
    
    for joint in upperarm:
        cmds.setAttr(joint + ".jointOrient", 0, 45, 0, type="float3")
    for joint in lowerarm:
        cmds.setAttr(joint + ".jointOrient", 0, 0, -36, type="float3")
    for joint in hand:
        cmds.setAttr(joint + ".jointOrient", -90, 0, 0, type="float3")
    
    for joint in index:
        cmds.setAttr(joint + ".jointOrient", 0, 5, 10, type="float3")
    for joint in index_01:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 15, type="float3")
    for joint in index_02:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 15, type="float3")
    
    for joint in middle:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 10, type="float3")
    for joint in middle_01:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 15, type="float3")
    for joint in middle_02:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 15, type="float3")    
    
    for joint in ring:
        cmds.setAttr(joint + ".jointOrient", 0, -5, 10, type="float3")
    for joint in ring_01:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 15, type="float3")
    for joint in ring_02:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 15, type="float3")        
    
    for joint in pinky:
        cmds.setAttr(joint + ".jointOrient", 0, -10, 10, type="float3")
    for joint in pinky_01:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 15, type="float3")
    for joint in pinky_02:
        cmds.setAttr(joint + ".jointOrient", 0, 0, 15, type="float3")
def UEPoseAToT():
    print("ue A->T")
    sel = cmds.ls(sl=True)
    
    clavicle = ["clavicle_r", "clavicle_l"]
    upperarm = ["upperarm_r", "upperarm_l"]
    lowerarm = ["lowerarm_r", "lowerarm_l"]
    hand = ["hand_r", "hand_l"]
    
    index = ["index_metacarpal_r", "index_metacarpal_l"]
    index_01 = ["index_01_r", "index_01_l"]
    index_02 = ["index_02_r", "index_02_l"]
    
    middle = ["middle_metacarpal_r", "middle_metacarpal_l"]
    middle_01 = ["middle_01_r", "middle_01_l"]
    middle_02 = ["middle_02_r", "middle_02_l"]
    
    ring = ["ring_metacarpal_r", "ring_metacarpal_l"]
    ring_01 = ["ring_01_r", "ring_01_l"]
    ring_02 = ["ring_02_r", "ring_02_l"]    
    
    pinky = ["pinky_metacarpal_r", "pinky_metacarpal_l"]
    pinky_01 = ["pinky_01_r", "pinky_01_l"]
    pinky_02 = ["pinky_02_r", "pinky_02_l"]    
    
    # cmds.rotate(90, 90, -90, clavicle[0])
    # cmds.rotate(90, 90, 90, clavicle[1])
    cmds.setAttr(clavicle[0] + ".rotateOrder", 0)  # 0 表示 XYZ
    cmds.rotate(90, 90, -90, clavicle[0])
    cmds.setAttr(clavicle[1] + ".rotateOrder", 0)  
    cmds.rotate(90, 90, 90, clavicle[1])

    for joint in upperarm:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(0, 0, 0, joint)

    for joint in lowerarm:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(0, 0, 0, joint)

    for joint in hand:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(-70, 0, 0, joint)

   
    
    for joint in index:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(0, 0, 0, joint)
    for joint in index_01:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(-0.17, -4.5, 2.8, joint)
    for joint in index_02:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(0, 5, 0, joint)

    for joint in middle:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(0, -5, 0, joint)
    for joint in middle_01:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(-1.25, 4, 4, joint)
    for joint in middle_02:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(0, 0, 0, joint)
    
    for joint in ring:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(-0.19, -7.8,-1.4, joint)
    for joint in ring_01:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(-3, 0.45, 4.4, joint)
    for joint in ring_02:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(0, 5.5, 3.2, joint) 
    
    for joint in pinky:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(-31.1, -17.6, -0.2, joint)
    for joint in pinky_01:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(-0.05, 7.2, 9.3, joint)
    for joint in pinky_02:
        cmds.setAttr(joint + ".rotateOrder", 0)  
        cmds.rotate(0, 0, 0, joint)

  
def UEPoseTToA():
    print("ue T->A")
    sel = cmds.ls(sl=True)
    
    clavicle = ["clavicle_r", "clavicle_l"]
    upperarm = ["upperarm_r", "upperarm_l"]
    lowerarm = ["lowerarm_r", "lowerarm_l"]
    hand = ["hand_r", "hand_l"]
    
    index = ["index_metacarpal_r", "index_metacarpal_l"]
    index_01 = ["index_01_r", "index_01_l"]
    index_02 = ["index_02_r", "index_02_l"]
    
    middle = ["middle_metacarpal_r", "middle_metacarpal_l"]
    middle_01 = ["middle_01_r", "middle_01_l"]
    middle_02 = ["middle_02_r", "middle_02_l"]
    
    ring = ["ring_metacarpal_r", "ring_metacarpal_l"]
    ring_01 = ["ring_01_r", "ring_01_l"]
    ring_02 = ["ring_02_r", "ring_02_l"]    
    
    pinky = ["pinky_metacarpal_r", "pinky_metacarpal_l"]
    pinky_01 = ["pinky_01_r", "pinky_01_l"]
    pinky_02 = ["pinky_02_r", "pinky_02_l"]    
    
    cmds.rotate(90.599, 84.445, -99.51, clavicle[0])
    cmds.rotate(90.599, 84.445, 80.49, clavicle[1])
    
    for joint in upperarm:
        cmds.rotate(4.22, 54.823, -0.397, joint)
    for joint in lowerarm:
        cmds.rotate(0.203, -0.815, -16.925, joint)
    for joint in hand:
        cmds.rotate(-69.716, 9.391, 3.451, joint)
   
    
    for joint in index:
        cmds.rotate(-0.099, 0.883, -12.756, joint)
    for joint in index_01:
        cmds.rotate(-0.516, -3.548, 16.548, joint)
    for joint in index_02:
        cmds.rotate(0.184, 3.439, 6.139, joint)

    for joint in middle:
        cmds.rotate(-9.777, -1.928, -13.177, joint)
    for joint in middle_01:
        cmds.rotate(-1.027,-5.708, 20.386, joint)
    for joint in middle_02:
        cmds.rotate(0.088, 3.76, 2.691, joint)
    
    for joint in ring:
        cmds.rotate(-19.262, -10.88,-7.737, joint)
    for joint in ring_01:
        cmds.rotate(-0.06, -0.37, 18.325, joint)
    for joint in ring_02:
        cmds.rotate(1.061, 6.496, 18.532, joint) 
    
    for joint in pinky:
        cmds.rotate(-31.027, -16.338, 7.144, joint)
    for joint in pinky_01:
        cmds.rotate(0.495, 4.952, 11.412, joint)
    for joint in pinky_02:
        cmds.rotate(-0.057, -0.661, 9.857, joint)  


