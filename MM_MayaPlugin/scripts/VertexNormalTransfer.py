import maya.cmds as cmds
import math
#这是一款顶点法线信息复制工具，通过判断距离最近的两个点进行法线信息传递。前后选择的顶点数量必须相同。

version = 1.1
createdOn = '2023/5/20'

class VertexNormalTransfer:
    def __init__(self):
        self.vertexC = []
        self.vertexD = [] 
        self.normalC = [] 
        self.selectedObj = None 
        self.winName = 'VertexNormalCopyTool'
        
    def createUI(self):
        if cmds.window(self.winName, exists=True):
            cmds.deleteUI(self.winName)
        window = cmds.window(self.winName, title='顶点法线复制工具'+ str(version), widthHeight=(200, 90),resizeToFitChildren=False, sizeable=False,toolbox=True)
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='请选择一个或多个顶点')
        cmds.button(label='复制', command=self.onSelectVertexC)
        cmds.text(label='请选择一个或多个顶点')
        cmds.button(label='粘贴', command=self.onSelectVertexD)
        cmds.showWindow(window)

    def getPos(self, verts):
        pos = cmds.xform(verts[0], q=True, ws=True, translation=True)
        for v in verts[1:]:
            vPos = cmds.xform(v, q=True, ws=True, translation=True)
            pos = [(p+vPos[i])/2.0 for i,p in enumerate(pos)]
        return pos

    def getClosestVerts(self, verts1, verts2):
        closest = None
        minDist = float('inf')
        v1_pos = cmds.xform(verts1, q=True, ws=True, translation=True)
        for v2 in verts2:
            v2_pos = cmds.xform(v2, q=True, ws=True, translation=True)
            dist = math.sqrt((v1_pos[0]-v2_pos[0])**2+ (v1_pos[1]-v2_pos[1])**2 + (v1_pos[2]-v2_pos[2])**2)
            if dist < minDist:
                closest = (verts1, v2)
                minDist = dist
        return closest

    def onSelectVertexC(self, *args):
        if cmds.ls(selection=True):
            self.selectedObj = cmds.ls(selection=True)[0]
            self.vertexC = cmds.ls(selection=True, flatten=True)
            vertex_list = cmds.filterExpand(self.vertexC, sm=31, expand=True)
            if not vertex_list:
                cmds.error(u'请只选择一个或多个顶点')               
            else:
                self.normalC = cmds.polyNormalPerVertex(self.vertexC, query=True, xyz=True)
        else:
            cmds.error(u'请选择一个或多个顶点')

    def onSelectVertexD(self, *args):
        if cmds.ls(selection=True):
            self.selectedObj = cmds.ls(selection=True)[0]
            self.vertexD = cmds.ls(selection=True, flatten=True)
            vertex_list1 = cmds.filterExpand(self.vertexC, sm=31, expand=True)
            if not vertex_list1:
                cmds.error(u'请只选择一个或多个顶点')
            else: 
                if len(self.vertexC) != len(self.vertexD):
                    cmds.error(u'所选顶点数量不同，请重新选择')
                for i in range(len(self.vertexC)):
                    v1, v2 = self.getClosestVerts(self.vertexC[i], self.vertexD)
                    normal = cmds.polyNormalPerVertex(v1, query=True, xyz=True)
                    cmds.polyNormalPerVertex(v2, normalXYZ=(normal[0], normal[1], normal[2]))
                    self.vertexD.remove(v2)
        else:
            cmds.error(u'请选择一个或多个顶点')




