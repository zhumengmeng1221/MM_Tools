import maya.cmds as cmds
import math
import maya
import inspect
from importlib import reload
from sys import path as syspath, platform
from os import environ, path as ospath

ROOT_DIR = r"C:\Users\mengmeng_zhu\Desktop\MM_Tools\MM_Tools\MM_MayaPlugin\scripts"
ROOT_LIB_DIR = fr"{ROOT_DIR}/lib"
if platform == "win32":
    LIB_DIR = f"{ROOT_LIB_DIR}/windows"
elif platform == "linux":
    LIB_DIR = f"{ROOT_LIB_DIR}/linux"
else:
    raise OSError("OS not supported, please compile dependencies and add value to LIB_DIR")


if "MAYA_PLUG_IN_PATH" in environ:
    separator = ":" if platform == "linux" else ";"
    environ["MAYA_PLUG_IN_PATH"] = separator.join([environ["MAYA_PLUG_IN_PATH"], LIB_DIR])    
else:
    environ["MAYA_PLUG_IN_PATH"] = LIB_DIR

syspath.append(ROOT_DIR)
syspath.append(LIB_DIR)


#from Metahumen52blendshap import Metahumen52BSCreate
#from Metahumen52blendshap import *
from Metahumen52blendshap import BS
from VertexNormalTransfer import *
import ig_EzRename 
from Pose import *
from testpy import Test1 
from brSmoothWeights import dragDropInstaller
version = 1.1
createdOn = '2023/5/20'
csv_file = ROOT_DIR+r"\52BS.txt"
class Main:
    def __init__(self):
        self.vertexC = []
        
        self.selectedObj = None 
        self.winName = 'MainWindow'
        
    def createUI1(self):
        if cmds.window(self.winName, exists=True):
            cmds.deleteUI(self.winName)
        window = cmds.window(self.winName, title='MM插件'+ str(version), widthHeight=(200, 400),resizeToFitChildren=False, sizeable=False,toolbox=True)
        cmds.columnLayout(adjustableColumn=True)
        cmds.button(label='顶点法线复制', command=self.onSelectVertexC)
        cmds.button(label='导入模型法线锁定', command=self.NormalsLock)
        cmds.button(label='基于metahumen生成52表情肌', command=self.blendershap52)
        cmds.button(label='重命名插件', command=self.Rema)
        cmds.button(label='Metahumen POS A->T', command=self.AToT)
        cmds.button(label='Metahumen POS T->A', command=self.TToA)
        cmds.button(label='UE_Metahumen POS A->T', command=self.UEAToT)
        cmds.button(label='UE_Metahumen POS T->A', command=self.UETToA)
        cmds.button(label='快速平滑工具brSmoothWeights安装', command=self.Testfun)
        cmds.showWindow(window)
   
 
    def onSelectVertexC(self,*args):
        VertexNormalTransfer.createUI(self=VertexNormalTransfer())
    def NormalsLock(self, *args):
        maya.mel.eval('FBXProperty "Import|IncludeGrp|Geometry|OverrideNormalsLock" -v 1')
        print("成功")
    def blendershap52(self, *args):
        #Metahumen52BSCreate(csv_file)
        BS.Metahumen52BSCreate(BS(),csv_file)
    def Rema(self, *args):
        ig_EzRename.UI()
    def AToT(self, *args):
        PoseAToT()
    def TToA(self, *args):
        PoseTToA()
    def UEAToT(self, *args):
        UEPoseAToT()
    def UETToA(self, *args):
        UEPoseTToA()
    def Testfun(self, *args):
        if not dragDropInstaller.installExists():
            return

        dragDropInstaller.logInfo("Begin installation")

        # If a license file exists display the EULA window. Otherwise
        # continue to the installation window.
        if ospath.exists(ospath.join(dragDropInstaller.INSTALL_ROOT, "LICENSE")):
            dragDropInstaller.logInfo("Show EULA")
            dragDropInstaller.showEULA()
        else:
            dragDropInstaller.prepareInstallation()
           


myPlugin = Main()
myPlugin.createUI1()
