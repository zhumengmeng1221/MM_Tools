import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
import re, math
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as oma
import maya.api.OpenMayaUI as omuia


mel.eval('source "dagMenuProc"')

def O1():
    global storeEdge
    global currentArcCurve
    if mc.objExists('arcCurve*'):
        arcCurveList = mc.ls( "arcCurve*", transforms =1  )
        a = arcCurveList[0]
        for a in arcCurveList:
            if 'BaseWire' not in a:
                shapeNode = mc.listRelatives(a, fullPath=True )
                hist = mc.listConnections(mc.listConnections(shapeNode[0],sh=1, d=1 ) ,d=1 ,sh=1)
                mc.delete(hist,ch=1)
        mc.delete('arcCurve*')
    if len(currentArcCurve)>0:
        if mc.objExists(currentArcCurve):
            shapeNode = mc.listRelatives(currentArcCurve, fullPath=True )
            hist = mc.listConnections(mc.listConnections(shapeNode[0],sh=1, d=1 ) ,d=1 ,sh=1)
            mc.delete(hist,ch=1)
    if mc.objExists(currentArcCurve):
        mc.select(currentArcCurve)
    mc.select(storeEdge,add=1)
    if mc.objExists(currentArcCurve + 'BaseWire'):
        mc.delete(currentArcCurve + 'BaseWire')

def O2():
    global storeEdge
    global currentArcCurve
    currentDropOff = mc.floatSliderGrp('dropOffSlider' ,q=1,v=1)
    snapCheck = mc.checkBox('snapCurve',q = 1 ,v = 1)
    goEven = mc.checkBox('evenSpace', q=1 ,v = 1)
    conP = mc.intSliderGrp('CPSlider',q=1 , v = True )
    curveT = mc.radioButtonGrp('curveType', q=1, sl=1)
    goArc = mc.checkBox('makeArc', q=1 ,v = 1)
    cClean = mc.checkBox('cleanCurve', q=1 ,v = 1)
    selEdge = mc.filterExpand(expand=True ,sm=32)
    selCurve = mc.filterExpand(expand=True ,sm=9)
    if selCurve:
        if len(selEdge)>0 and len(selCurve)== 1:
            storeEdge = selEdge
            mc.select(selCurve,d=1)
            selMeshForDeformer = mc.ls(sl=1,o=1)
            getCircleState,listVtx = O78()
            newCurve = mc.duplicate(selCurve[0], rr=1)
            mc.rename(newCurve[0],'newsnapCurve')
            currentArcCurve = 'newsnapCurve'
            mc.rebuildCurve(currentArcCurve,ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s = 100, d=1, tol=0.01)
            #check tip order
            curveTip = mc.pointOnCurve(currentArcCurve , pr = 0, p=1)
            tipA = mc.pointPosition(listVtx[0],w=1)
            tipB = mc.pointPosition(listVtx[-1],w=1)
            distA = math.sqrt( ((tipA[0] - curveTip[0])**2)  + ((tipA[1] - curveTip[1])**2)  + ((tipA[2] - curveTip[2])**2) )
            distB = math.sqrt( ((tipB[0] - curveTip[0])**2)  + ((tipB[1] - curveTip[1])**2)  + ((tipB[2] - curveTip[2])**2) )
            if distA > distB:
                listVtx.reverse()
            #snap to curve
            if goEven == 1:
                for q in range(len(selEdge)+1):
                    if q == 0:
                        pp = mc.pointOnCurve(currentArcCurve , pr = 0, p=1)
                        mc.move( pp[0], pp[1], pp[2],listVtx[q] , a =True, ws=True)
                    else:
                        pp = mc.pointOnCurve(currentArcCurve , pr = (1.0/len(selEdge)*q), p=1)
                        mc.move( pp[0], pp[1], pp[2],listVtx[q] , a =True, ws=True)
            else:
                sum = 0
                totalEdgeLoopLength = 0
                Llist = []
                uList = []
                pList = []
                for i in range(len(listVtx)-1):
                    pA = mc.pointPosition(listVtx[i], w =1)
                    pB = mc.pointPosition(listVtx[i+1], w =1)
                    checkDistance = math.sqrt( ((pA[0] - pB[0])**2)  + ((pA[1] - pB[1])**2)  + ((pA[2] - pB[2])**2) )
                    Llist.append(checkDistance)
                    totalEdgeLoopLength = totalEdgeLoopLength + checkDistance

                for j in Llist:
                    sum = sum + j
                    uList.append(sum)
                for k in uList:
                    p = k / totalEdgeLoopLength
                    pList.append(p)

                for q in range(len(selEdge)+1):
                    if q == 0:
                        pp = mc.pointOnCurve(currentArcCurve , pr = 0, p=1)
                        mc.move( pp[0], pp[1], pp[2],listVtx[q] , a =True, ws=True)
                    else:
                        pp = mc.pointOnCurve(currentArcCurve , pr = pList[q-1], p=1)
                        mc.move( pp[0], pp[1], pp[2],listVtx[q] , a =True, ws=True)
            mc.delete('newsnapCurve')
            deformerNames  = mc.wire(selMeshForDeformer, gw=0, en = 1, ce = 0, li= 0, dds = [(0,1)], dt=1, w = selCurve[0])
            mc.connectControl("dropOffSlider", (deformerNames[0]+".dropoffDistance[0]"))
            if snapCheck == 0:
                mc.setAttr((deformerNames[0] + '.dropoffDistance[0]'),1)
            else:
                mc.setAttr((deformerNames[0] + '.dropoffDistance[0]'),currentDropOff)
            currentArcCurve = selCurve[0]
            mc.select(selCurve[0])
    else:
        if selEdge:
            storeEdge = selEdge
            if cClean == 0:
                if mc.objExists('arcCurve*'):
                    O1()
            selMeshForDeformer = mc.ls(sl=1,o=1)
            getCircleState,listVtx = O78()
            deformerNames = []
            #make nurbs curve
            if getCircleState == 0: #Arc
                if goArc == 1:
                    midP = int(len(listVtx)/2)
                    mc.move(0.01, 0, 0,selEdge[midP],r=1, cs=1 ,ls=1, wd =1)
                    p1 = mc.pointPosition(listVtx[0], w =1)
                    p2 = mc.pointPosition(listVtx[midP], w =1)
                    p3 = mc.pointPosition(listVtx[-1], w =1)
                    newNode = mc.createNode('makeThreePointCircularArc')
                    mc.setAttr((newNode + '.pt1'), p1[0],  p1[1] , p1[2])
                    mc.setAttr((newNode + '.pt2'), p2[0],  p2[1] , p2[2])
                    mc.setAttr((newNode + '.pt3'), p3[0],  p3[1] , p3[2])
                    mc.setAttr((newNode + '.d'), 3)
                    mc.setAttr((newNode + '.s'), len(listVtx))
                    newCurve = mc.createNode('nurbsCurve')
                    mc.connectAttr((newNode+'.oc'), (newCurve+'.cr'))
                    mc.delete(ch=1)
                    transformNode = mc.listRelatives(newCurve, fullPath=True , parent=True )
                    mc.select(transformNode)
                    mc.rename(transformNode,'arcCurve0')
                    getNewNode = mc.ls(sl=1)
                    currentArcCurve = getNewNode[0]
                    numberP = 0
                    if curveT == 2:#nubs curve
                        numberP = int(conP) - 3
                        if numberP < 1:
                            numberP = 1
                    else:
                        numberP = int(conP) -1
                    mc.rebuildCurve(currentArcCurve,ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s= numberP, d=3, tol=0.01)
                else:
                    p1 = mc.pointPosition(listVtx[0], w =1)
                    mc.curve(d= 1, p=p1)
                    mc.rename('arcCurve0')
                    getNewNode = mc.ls(sl=1)
                    currentArcCurve = getNewNode[0]
                    for l in range(1,len(listVtx)):
                        p2 = mc.pointPosition(listVtx[l], w =1)
                        mc.curve(currentArcCurve, a= 1, d= 1, p=p2)
                    numberP = int(conP) -1
                    mc.rebuildCurve(currentArcCurve,ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s= numberP, d=1, tol=0.01)
            else: #circle
                p1 = mc.pointPosition(listVtx[0], w =1)
                mc.curve(d= 1, p=p1)
                mc.rename('arcCurve0')
                getNewNode = mc.ls(sl=1)
                currentArcCurve = getNewNode[0]
                for l in range(1,len(listVtx)):
                    p2 = mc.pointPosition(listVtx[l], w =1)
                    mc.curve(currentArcCurve, a= 1, d= 1, p=p2)
                mc.curve(currentArcCurve, a= 1, d= 1, p=p1)
                mc.closeCurve(currentArcCurve,ch=0, ps=2, rpo=1, bb= 0.5, bki=0, p=0.1)
                conP = mc.intSliderGrp('CPSlider',q=1 , v = True )
                numberP = int(conP)
                if numberP < 4:
                    numberP = 4
                    mc.intSliderGrp('CPSlider',e=1 , v = 4 )
                mc.rebuildCurve(currentArcCurve,ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s = numberP, d=3, tol=0.01)
                ###########################################################################
            mc.delete(currentArcCurve ,ch=1)
            totalEdgeLoopLength = 0;
            sum = 0
            Llist = []
            uList = []
            pList = []
            #mc.select(selEdge)
            for i in range(len(listVtx)-1):
                pA = mc.pointPosition(listVtx[i], w =1)
                pB = mc.pointPosition(listVtx[i+1], w =1)
                checkDistance = math.sqrt( ((pA[0] - pB[0])**2)  + ((pA[1] - pB[1])**2)  + ((pA[2] - pB[2])**2) )
                Llist.append(checkDistance)
                totalEdgeLoopLength = totalEdgeLoopLength + checkDistance
            if goEven == 1:
                avg = totalEdgeLoopLength / (len(selEdge))
                for j in range(len(selEdge)):
                    sum = ((j+1)*avg)
                    uList.append(sum)
            else:
                for j in Llist:
                    sum = sum + j
                    uList.append(sum)
            for k in uList:
                p = k / totalEdgeLoopLength
                pList.append(p)
            #snap to curve
            if snapCheck == 1:
                for q in range(len(pList)):
                    if q+1 == len(listVtx):
                        pp = mc.pointOnCurve(currentArcCurve, pr = 0, p=1)
                        mc.move( pp[0], pp[1], pp[2],listVtx[0] , a =True, ws=True)
                    else:
                        pp = mc.pointOnCurve(currentArcCurve , pr = pList[q], p=1)
                        mc.move( pp[0], pp[1], pp[2],listVtx[q+1] , a =True, ws=True)
            #convert to Bezier Curve
            mc.delete(currentArcCurve ,ch=1)
            mc.select(currentArcCurve)
            if curveT == 1:
                mc.nurbsCurveToBezier()
                if getCircleState == 1: #circle need to fix bug
                    mc.closeCurve(currentArcCurve,ch=0, ps=2, rpo=1, bb= 0.5, bki=0, p=0.1)
                    mc.closeCurve(currentArcCurve,ch=0, ps=2, rpo=1, bb= 0.5, bki=0, p=0.1)
            #wireWrap
            deformerNames  = mc.wire( selMeshForDeformer, gw=0, en = 1, ce = 0, li= 0, dds = [(0,1)], dt=1, w = currentArcCurve)
            #select controllers
            if getCircleState == 0:
                mc.setToolTo('moveSuperContext')
                degree = mc.getAttr(currentArcCurve + '.degree')
                spans = mc.getAttr(currentArcCurve + '.spans')
                numberCVs = degree + spans
                collect = []
                for x in range(int(numberCVs/3)-1):
                    g = currentArcCurve + '.cv[' + str((x+1)*3) + ']'
                    collect.append(g)
                mc.select(collect ,r=1)

            else:
                mc.select(currentArcCurve + '.cv[*]')
            cmd = 'doMenuNURBComponentSelection("' + currentArcCurve + '", "controlVertex");'
            mel.eval(cmd)
            mc.connectControl("dropOffSlider", (deformerNames[0]+".dropoffDistance[0]"))
            if snapCheck == 0:
                mc.setAttr((deformerNames[0] + '.dropoffDistance[0]'),1)
            else:
                mc.setAttr((deformerNames[0] + '.dropoffDistance[0]'),currentDropOff)
            #add to viewport even in isolate mode
            for x in range(1,5):
                mc.isolateSelect(('modelPanel' + str(x)), ado= currentArcCurve )

def O3():
    goArc = mc.checkBox('makeArc', q=1 ,v = 1)
    curveT = mc.radioButtonGrp('curveType', q=1, sl=1)
    if goArc == 0:
        mc.intSliderGrp('CPSlider', e=1, min= 4, v = 4 , fmx = 500)
    else:
        if curveT == 1:
            mc.intSliderGrp('CPSlider', e=1, min= 2, v = 3, fmx = 500)
        else:
            mc.intSliderGrp('CPSlider', e=1, min= 4, v = 4, fmx = 500)

def O4():
    snapCheck = mc.checkBox('snapCurve',q = 1 ,v = 1)
    if snapCheck == 0 :
        mc.checkBox('evenSpace', e=1 ,en=0)
    else:
        mc.checkBox('evenSpace', e=1 ,en=1)

def O5():
    curveT = mc.radioButtonGrp('curveType', q=1, sl=1)
    getCurrentV = mc.intSliderGrp('CPSlider', q=1 ,v = 1 )
    if curveT == 2:
        mc.intSliderGrp('CPSlider', e=1, min= 4 )
        if getCurrentV < 4:
            mc.intSliderGrp('CPSlider', e=1, v= 4 )
    else:
        mc.intSliderGrp('CPSlider', e=1, min= 2 )
        
def O6():
    check  = mc.checkBox("evenRoundPivotSnap", q=1, value=1)
    if check == 1:
        mc.radioButtonGrp("PivotSnapType", e=1, en=1)
    else:
        mc.radioButtonGrp("PivotSnapType", e=1, en=0)
def O7(type):
    edgeRingList = mc.ls(sl=1,fl=1)
    targetL = mc.floatField('equalizerLength', q=1, value = 1)
    unwantRing = mc.ls(mc.polySelectSp(edgeRingList, q=1,ring=1),fl=1)
    mc.ConvertSelectionToFaces()
    mc.ConvertSelectionToEdgePerimeter()
    mc.select(unwantRing,d=1)
    testLoopAB = O8l()
    if len(testLoopAB) == 2:
        ringPA = mc.ls(mc.polyListComponentConversion(testLoopAB[0], tv=1),fl=1)
        ringPB = mc.ls(mc.polyListComponentConversion(testLoopAB[1], tv=1),fl=1)  
        for d in edgeRingList:
            listVtx = mc.ls(mc.polyListComponentConversion(d, tv=1),fl=1)
            pACheck = listVtx[0]
            pBCheck = listVtx[1]
            if pACheck in ringPA:
                pass
            else:
                pACheck = listVtx[1]
                pBCheck = listVtx[0]
            pA = mc.pointPosition(pACheck, w=1)
            pB = mc.pointPosition(pBCheck, w=1)
            checkDistance = math.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2 + (pA[2] - pB[2]) ** 2)
            if type == "A":
                mc.scale((targetL/checkDistance) ,(targetL/checkDistance),(targetL/checkDistance), listVtx[0], p=[pA[0],pA[1],pA[2]],r=1)
            elif type == "B":
                mc.scale((targetL/checkDistance) ,(targetL/checkDistance),(targetL/checkDistance), listVtx[1], p=[pB[0],pB[1],pB[2]],r=1)
            else:
                mc.scale((targetL/checkDistance) ,(targetL/checkDistance),(targetL/checkDistance), listVtx[0], p=[((pA[0]+pB[0])/2),((pA[1]+pB[1])/2),((pA[2]+pB[2])/2)],r=1)
                mc.scale((targetL/checkDistance) ,(targetL/checkDistance),(targetL/checkDistance), listVtx[1], p=[((pA[0]+pB[0])/2),((pA[1]+pB[1])/2),((pA[2]+pB[2])/2)],r=1)
            mc.select(edgeRingList)     
def O8():
    selEdge = mc.ls(sl=1,fl=1)
    length = O2l(selEdge[0])
    output = round(length, 3)
    mc.floatField('equalizerLength', e=True, v=output)
    
def O9():
    if mc.objExists('edgeSave'):
        mc.delete('edgeSav*')
    currentV = mc.floatSliderGrp('lockEdgeSlider', q=True, v=True)
    type = mc.radioButtonGrp('lockEdgeType', q=True, sl=True)
    if type == 1:
        O11()
    else:
        O13()
    mc.floatSliderGrp('lockEdgeSlider', e=True, v=currentV)

def O10():
    if mc.objExists('edgeSave'):
        mc.delete('edgeSav*')
    currentV = mc.floatSliderGrp('lockEdgeSlider', q=True, v=True)
    type = mc.radioButtonGrp('lockEdgeType', q=True, sl=True)
    if type == 1:
        O14()
    else:
        Ol6()
    mc.floatSliderGrp('lockEdgeSlider', e=True, v=currentV)

def O11():
    lockLength = mc.floatField('lastLockEdgelength', q=True, v=True)
    O14()
    O12(lockLength)
    mc.select(d=True)

def O12(targetEdgeLength):
    global polySRA
    global polySRB
    global AEdge
    global BEdge
    ADis = O2l(AEdge[0])
    currentW = mc.getAttr(polySRA[0] +".weight")
    newW = currentW * targetEdgeLength / ADis
    mc.floatSliderGrp('lockEdgeSlider', e=True, v=currentW)
    mc.setAttr((polySRA[0] + ".weight"), newW)
    ADis = O2l(AEdge[0])
    BDis = O2l(BEdge[0])
    currentW = mc.getAttr(polySRB[0] + ".weight")
    newW = 1 - (ADis * (1.0 - currentW) / BDis)
    mc.setAttr((polySRB[0]+".weight"), newW)
    mc.floatField('lastLockEdgelength', e=True, v = targetEdgeLength)

def O13():
    global myLockEdge
    myLockEdge = []
    selectedgelock = mc.ls(sl=True)
    selectGeo = mc.ls(hl=True)
    mc.bakePartialHistory(all=True)
    lockLength = mc.floatField('lastLockEdgelength', q=True, v=True)
    length = O2l(selectedgelock[0])
    halfL = length / 2.0
    checkN = lockLength / halfL
    lockL = 1.0 - checkN
    if lockL > 0:
        mc.sets(name="edgeSave", text="edgeSave")
        mc.select(selectedgelock[0], r=True)
        mc.polySelectSp(ring=True)
        mc.polySplitRing(ch=0, splitType=2, divisions=1)
        locknodeLst = mc.polyDuplicateEdge(of=lockL, ch=True)
        mc.rename(locknodeLst[0], "lockEdges")
        mc.polyDelEdge(cv=True)
        mc.select('edgeSave', r=True)
        O20('min')
        myLockEdge = mc.ls(sl=True, fl=True)
        mc.delete('edgeSave')
        mc.select(d=True)
        mc.connectControl('lockEdgeSlider', 'lockEdges.of')
    else:
        mc.select(selectedgelock[0], r=True)
        O15()
        print("length longer than current egde!") 

def O14():
    mc.floatSliderGrp('lockEdgeSlider', e=True, en=1)
    global myLockEdge
    global polySRA
    global polySRB
    global AEdge
    global BEdge
    myLockEdge = []
    polySRA = []
    polySRB = []
    AEdge = []
    BEdge = []
    mc.bakePartialHistory(all=True) 
    mc.polySelectSp(ring=True)
    O20('min')
    mc.sets(name="edgeSave", text="edgeSave")
    edgeData = Ol8()
    mc.polySelectSp(ring=True)
    polySRA = mc.polySplitRing(ch=True, splitType=0, weight=0.01, smoothingAngle=30, fixQuads=True, insertWithEdgeFlow=False, direction=1, rootEdge=int(edgeData[1]))
    mc.select('edgeSave', r=True)
    O20('max')
    edgeData = Ol8()
    mc.polySelectSp(ring=True)
    polySRB = mc.polySplitRing(ch=True, splitType=0, weight=0.99, smoothingAngle=30, fixQuads=True, insertWithEdgeFlow=False, direction=0, rootEdge=int(edgeData[1]))
    mc.select('edgeSave', r=True)
    O20('max')
    midEdge = mc.ls(sl=True, fl=True)
    mc.select('edgeSave', r=True)
    mc.select(midEdge, d=True)
    O20('max')
    AEdge = mc.ls(sl=True, fl=True)
    myLockEdge = mc.ls(sl=True, fl=True)
    mc.select('edgeSave', r=True)
    mc.select(midEdge, d=True)
    mc.select(AEdge, d=True)
    BEdge = mc.ls(sl=True, fl=True)
    mc.delete('edgeSave')
    mc.select(d=True)
    O19()


def O15():
    mc.ConvertSelectionToEdges()
    current = mc.ls(sl=True)
    if current:
        tokens = current[0].split(".")
        mc.selectType(edge=True)
        mc.select(tokens[0], r=True, ne=True)
        mc.select(current, r=True)
        cmd  = 'doMenuComponentSelectionExt("' + tokens[0] + '", "edge", 0);'
        mel.eval(cmd)

def Ol6():
    global myLockEdge
    myLockEdge = []
    selectedgelock = mc.ls(sl=True)
    selectGeo = mc.ls(hl=True)
    mc.sets(name="edgeSave", text="edgeSave")
    mc.bakePartialHistory(all=True)
    Lock = mc.floatSliderGrp('lockEdgeSlider', q=True, v=True)
    length = O2l(selectedgelock[0])
    mc.polySelectSp(ring=True)
    mc.polySplitRing(ch=0, splitType=2, divisions=1)
    locknodeLst = mc.polyDuplicateEdge(of=Lock, ch=True)
    mc.rename(locknodeLst[0], "lockEdges")
    mc.polyDelEdge(cv=True)
    mc.select(selectGeo[0], r=True)
    O15()
    mc.InvertSelection()
    mc.select('edgeSave', r=True)
    O20('min')
    myLockEdge = mc.ls(sl=True, fl=True)
    mc.delete('edgeSave')
    mc.select(d=True)
    mc.connectControl('lockEdgeSlider', 'lockEdges.of')
    
def Ol7():
    global myLockEdge
    length = O2l(myLockEdge[0])
    output = round(length, 3)
    mc.floatField('lastLockEdgelength', e=True, v=output)

def Ol8():
    startEdge = mc.ls(sl=True, fl=True)
    buffer = startEdge[0].split(".")
    Edgebuffer = buffer[1].split("[")
    getNumber = Edgebuffer[1].split("]")
    return buffer[0], getNumber[0]

def O19():
    type = mc.radioButtonGrp('lockEdgeType', q=True, sl=True)
    if type == 1:
        Lock = mc.floatSliderGrp('lockEdgeSlider', q=True, v=True)
        global polySRA
        global polySRB
        global AEdge
        global BEdge
        errorCheck = (1 - Lock) / 2.0
        if 0.001 < errorCheck < 0.4999:
            mc.setAttr((polySRA[0]+".weight"), errorCheck)
            currentW = mc.getAttr(polySRB[0] + ".weight")
            ADis = O2l(AEdge[0])
            BDis = O2l(BEdge[0])
            newW = 1 - (ADis * (1.0 - currentW) / BDis)
            mc.setAttr((polySRB[0]+".weight"), newW)
    Ol7()

def O20(minmax):
    value = 0 if minmax == "max" else float('inf')
    selection = mc.ls(sl=True, fl=True)
    edges = mc.filterExpand(selection, ex=True, sm=32)
    if not edges:
        raise ValueError("No valid Edges selected!")
    targetEdge = None
    for edge in edges:
        checkEdgeLength = O2l(edge)
        if minmax == "max" and checkEdgeLength > value:
            value = checkEdgeLength
            targetEdge = edge
        elif minmax == "min" and checkEdgeLength < value:
            value = checkEdgeLength
            targetEdge = edge
    
    if targetEdge:
        mc.select(targetEdge)
    else:
        raise ValueError("No edge found matching the criteria.")

def O2l(edge):
    vertices = mc.polyListComponentConversion(edge, toVertex=True)
    vertices = mc.filterExpand(vertices, sm=31)
    length = O22(vertices[0], vertices[1])
    return length

def O22(vertex1, vertex2):
    v1 = mc.pointPosition(vertex1, w=True)
    v2 = mc.pointPosition(vertex2, w=True)
    distance = math.sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)
    return distance

def O23():
    keepCheckBox = mc.checkBox('keepSpliteNumber', q=True, v=True)
    keepInsertNumber = mc.floatSliderGrp('multiInsertNo', q=True, v=True)
    selectedEdges = mc.ls(sl=True, fl=True)
    polySplitRingNodes = mc.ls(type='polySplitRing')
    mc.floatSliderGrp('multiInsertNo', e=True, v=1)
    polySRList = []
    obj = mc.ls(hl=True)
    if polySplitRingNodes:
        mc.select(obj)
        mc.delete(ch=True)
    if len(selectedEdges) == 1:
        mc.select(selectedEdges)
        mc.polySelectSp(ring=True)
        nodeLst = mc.polySplitRing(ch=True, splitType=2, divisions=1, useEqualMultiplier=True, smoothingAngle=30, fixQuads=False)
        mc.connectControl('multiInsertNo', nodeLst[0] + ".div")
        if keepCheckBox:
            mc.setAttr(nodeLst[0] + ".div", keepInsertNumber)
            mc.floatSliderGrp('multiInsertNo', e=True, v=keepInsertNumber)
    elif len(selectedEdges) > 1:
        confirmString = mc.confirmDialog(title="Confirm", message="Warning!! More than one edge selected?", button=["Continues", "Abort"], defaultButton="Abort", cancelButton="Abort", dismissString="Abort")
        if confirmString == "Continues":
            for s in selectedEdges:
                mc.select(s)
                mc.polySelectSp(ring=True)
                nodeLst = mc.polySplitRing(ch=True, splitType=2, divisions=1, useEqualMultiplier=True, smoothingAngle=30, fixQuads=False)
                polySRList.append(nodeLst[0] + ".div")
            collectList = ['"{}"'.format(p) for p in polySRList]
            getList = ','.join(collectList)
            cmd = "mc.connectControl('multiInsertNo', {})".format(getList)
            eval(cmd)
            if keepCheckBox:
                mc.floatSliderGrp('multiInsertNo', e=True, v=keepInsertNumber)
                for p in polySRList:
                    mc.setAttr(p, keepInsertNumber)
        mc.select(cl=True)
    if obj:
        cmd = 'doMenuComponentSelection("' + obj[0]  +'", "edge");'
        mel.eval(cmd)
        
def O24(location, curveObject):
    curve = curveObject
    tempList = om.MSelectionList()
    tempList.add(curve)
    curveObj = om.MObject()
    tempList.getDependNode(0, curveObj)
    dagpath = om.MDagPath()
    tempList.getDagPath(0, dagpath)
    curveMF = om.MFnNurbsCurve(dagpath)
    point = om.MPoint( location[0], location[1], location[2])
    prm = om.MScriptUtil()
    pointer = prm.asDoublePtr()
    om.MScriptUtil.setDouble (pointer, 0.0)
    tolerance = .001
    space = om.MSpace.kObject
    result = om.MPoint()
    result = curveMF.closestPoint (point, pointer,  0.0, space)
    parameter = om.MScriptUtil.getDouble (pointer)
    return [parameter, (result.x), (result.y), (result.z)]
    
def O25(SX, SY):
    pos = om.MPoint()
    dir = om.MVector()
    hitpoint = om.MFloatPoint()
    omui.M3dView().active3dView().viewToWorld(int(SX), int(SY), pos, dir)
    pos2 = om.MFloatPoint(pos.x, pos.y, pos.z)
    checkCam = O30()
    finalX = []
    finalY = []
    finalZ = []
    checkList = []
    checkList.append('refPlane')
    for mesh in checkList:
        selectionList = om.MSelectionList()
        selectionList.add(mesh)
        dagPath = om.MDagPath()
        selectionList.getDagPath(0, dagPath)
        fnMesh = om.MFnMesh(dagPath)
        intersection = fnMesh.closestIntersection(om.MFloatPoint(pos2), om.MFloatVector(dir), None, None, False, om.MSpace.kWorld, 99999, False, None, hitpoint, None, None, None, None, None)
        if intersection:
            finalX = hitpoint.x
            finalY = hitpoint.y
            finalZ = hitpoint.z
    return (finalX, finalY, finalZ)
    
def O26(pointName):
    view = omuia.M3dView.active3dView()
    posInView = []
    ppos = mc.pointPosition(pointName, w=1)
    posInView.append(view.worldToView(oma.MPoint(ppos)))
    vpos = view.worldToView(oma.MPoint(ppos))
    wx, wy, wz = O25(vpos[0], vpos[1])
    return (wx, wy, wz)
    
def O27(cameraName, worldPoint):
    resWidth, resHeight = O28()
    selList = om.MSelectionList()
    selList.add(cameraName)
    dagPath = om.MDagPath()
    selList.getDagPath(0, dagPath)
    dagPath.extendToShape()
    camInvMtx = dagPath.inclusiveMatrix().inverse()
    fnCam = om.MFnCamera(dagPath)
    mFloatMtx = fnCam.projectionMatrix()
    projMtx = om.MMatrix(mFloatMtx.matrix)
    mPoint = om.MPoint(worldPoint[0], worldPoint[1], worldPoint[2]) * camInvMtx * projMtx
    x = (mPoint[0] / mPoint[3] / 2 + 0.5) * resWidth
    y = (mPoint[1] / mPoint[3] / 2 + 0.5) * resHeight
    return [x, y]
    
def O28():
    windowUnder = mc.getPanel(withFocus=True)
    if 'modelPanel' not in windowUnder:
        windowUnder = 'modelPanel4'
    viewNow = omui.M3dView.active3dView()
    omui.M3dView.getM3dViewFromModelEditor(windowUnder, viewNow)
    screenW = omui.M3dView.portWidth(viewNow)
    screenH = omui.M3dView.portHeight(viewNow)
    return (screenW, screenH)
    
def O29(tX, tY, tZ):
    checkCam = O30()
    resWidth, resHeight = O28()
    ratio = mc.getAttr('defaultResolution.deviceAspectRatio')
    mc.polyPlane(w=ratio, h=1, sx=40, sy=20, ax=(0, 0, 1), cuv=2, ch=1)
    mc.rename('refPlane')
    mc.setAttr('refPlane.visibility', 0)
    mc.parentConstraint(checkCam, 'refPlane', weight=1)
    mc.delete(constraints=True)
    mc.setAttr('refPlane.translateX', tX)
    mc.setAttr('refPlane.translateY', tY)
    mc.setAttr('refPlane.translateZ', tZ)
    head3d = mc.pointPosition('refPlane.vtx[0]')
    tail3d = mc.pointPosition('refPlane.vtx[860]')
    head2D = O27(checkCam, (head3d[0], head3d[1], head3d[2]))
    tail2d = O27(checkCam, (tail3d[0], tail3d[1], tail3d[2]))
    distanceX = tail2d[0] - head2D[0]
    distanceY = tail2d[1] - head2D[1]
    mc.setAttr('refPlane.scaleX', resWidth / distanceX * 2)
    mc.setAttr('refPlane.scaleY', resHeight / distanceY * 2)
    
def O30():
    view = omui.M3dView.active3dView()
    cam = om.MDagPath()
    view.getCamera(cam)
    camPath = cam.fullPathName()
    cameraTrans = mc.listRelatives(camPath, type='transform', p=True)
    cameraPosition = mc.xform(cameraTrans, q=1, ws=1, rp=1)
    return cameraTrans[0]
    
def O3l(edgeList):
    listEvenVtx = O76(edgeList)
    if mc.objExists('tempEvenCurve'):
        mc.delete('tempEvenCurve')
    mc.select(edgeList)
    mc.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=1)
    mc.rename('tempEvenCurve')
    curveCVs =mc.ls('tempEvenCurve.cv[*]',fl=1)
    posCurve = mc.xform(curveCVs[0], a=1,ws=1, q=1, t=1)
    posEdge = mc.xform(listEvenVtx[0], a=1,ws=1, q=1, t=1)
    if posCurve == posEdge:
        pass
    else:
        listEvenVtx = listEvenVtx[::-1]
    mc.rebuildCurve('tempEvenCurve',ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s = 0 , d=1, tol=0)
    mc.rebuildCurve('tempEvenCurve',ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s = 0 , d=1, tol=0)
    if len(curveCVs)< 4:
        mc.delete( 'tempEvenCurve.cv[1]', 'tempEvenCurve.cv[3]')
        curveCVs =mc.ls('tempEvenCurve.cv[*]',fl=1)
    for i in range(len(curveCVs)):
        pos = mc.xform(curveCVs[i], a=1,ws=1, q=1, t=1)
        mc.xform(listEvenVtx[i], a=1, ws=1, t = (pos[0],pos[1],pos[2]) )
    mc.delete('tempEvenCurve')
    
def O32():
    edgeLoopSel = mc.ls(sl=1,fl=1)
    sortGrp = O8l()
    for e in sortGrp:
        O33(e)
    meshName = edgeLoopSel[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(edgeLoopSel)

def O33(flatList):
    O38()
    listVtx = O76(flatList)
    xA, yA, zA = mc.pointPosition(listVtx[0], w=1)
    xB, yB, zB = mc.pointPosition(listVtx[-1], w=1)
    mc.select(flatList)
    mc.polyToCurve(form=0, degree=1, conformToSmoothMeshPreview=1)
    mc.rename('newguildcurve')
    mc.duplicate(smartTransform=1)
    mc.rename('newDeformcurve')
    spans = mc.getAttr('newguildcurve.spans')
    mc.select('newDeformcurve.cv['+str(spans)+']','newDeformcurve.cv[0]')
    mc.InvertSelection()
    mc.delete()
    mc.rebuildCurve('newDeformcurve', ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=spans, d=1, tol=0)
    mc.blendShape( 'newDeformcurve', 'newguildcurve' ,en=0.1, w=(0,1))
    xA =  round(xA,3)
    yA =  round(yA,3)
    zA =  round(zA,3)
    xC, yC, zC = mc.pointPosition('newDeformcurve.cv[0]',w=1)
    xC =  round(xC,3)
    yC =  round(yC,3)
    zC =  round(zC,3)
    if xA == xC and yA == yC and zA == zC:
       pass
    else:
        listVtx.reverse()
    mc.delete('newguildcurve',ch=1)
    for i in range(1,len(listVtx)-1):
        xD, yD, zD = mc.pointPosition('newguildcurve.cv['+str(i)+']',w=1)
        mc.move(xD, yD, zD,listVtx[i] , a =True, ws=True)
    O38()

def O34(mode):
    if mode == 3:
        mc.iconTextButton('button2DIcon' ,e=1 ,bgc =  [0.18,0.18,0.18] )
        mc.iconTextButton('button3DIcon' ,e=1 ,bgc =  [0.5, 0.21, 0] )
    elif mode ==2:
        mc.iconTextButton('button2DIcon' ,e=1 ,bgc =  [0.5, 0.21, 0] )
        mc.iconTextButton('button3DIcon' ,e=1 ,bgc =  [0.18,0.18,0.18] )

def O35(level):
    checkMode = mc.iconTextButton('button2DIcon' ,q=1 ,bgc = 1 )
    if checkMode[2] > 0:
        O39(level)
    else:
        O36(level)

def O36(level):
    edgeLoopSel = mc.ls(sl=1,fl=1)
    sortGrp = O8l()
    for e in sortGrp:
        O37(e,level)
    meshName = edgeLoopSel[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(edgeLoopSel)

def O37(flatList,level):
    numberPoint = level
    O38()
    listVtx = O76(flatList)
    checkCam = O30()
    closetP2Cam = []
    shortDistance = 10000000000
    cameraPosition = mc.xform(checkCam, q=1, ws=1, rp=1)
    for g in listVtx:
        x, y, z = mc.pointPosition(g, w=1)
        distanceBetween = math.sqrt((float(cameraPosition[0]) - x) ** 2 + (float(cameraPosition[1]) - y) ** 2 + (float(cameraPosition[2]) - z) ** 2)
        if distanceBetween < shortDistance:
            shortDistance = distanceBetween
            closetP2Cam = g
    tX, tY, tZ = mc.pointPosition(closetP2Cam, w=1)
    O29(tX, tY, tZ)
    pointDict = []
    for g in listVtx:
        pos = O26(g)
        pointDict.append(pos)
    mc.curve(d=1, p=[(pointDict[0][0], pointDict[0][1], pointDict[0][2]), (pointDict[-1][0], pointDict[-1][1], pointDict[-1][2])])
    mc.rename('newguildcurve')
    if numberPoint == 1:
        mc.rebuildCurve('newguildcurve', ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=1, d=3, tol=0)
        gap = int(len(listVtx) * 0.5)
        mc.select('newguildcurve.cv[1]', 'newguildcurve.cv[2]')
        nodeCluster = mc.cluster(n= 'midGrp')
        mc.move(pointDict[gap][0], pointDict[gap][1], pointDict[gap][2], nodeCluster[1], rpr=True)
    elif numberPoint == 2:
        mc.rebuildCurve('newguildcurve', ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=2, tol=0)
        gapA = int(len(listVtx) * 0.33333)
        gapB = int(len(listVtx) * 0.66666)
        mc.move(pointDict[gapA][0], pointDict[gapA][1], pointDict[gapA][2], 'newguildcurve.cv[1]', rpr=True)
        mc.move(pointDict[gapB][0], pointDict[gapB][1], pointDict[gapB][2], 'newguildcurve.cv[2]', rpr=True)
    elif numberPoint == 3:
        mc.rebuildCurve('newguildcurve', ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=3, d=2, tol=0)
        gapA = int(len(listVtx) * 0.25)
        gapB = int(len(listVtx) * 0.5)
        gapC = int(len(listVtx) * 0.75)
        mc.move(pointDict[gapA][0], pointDict[gapA][1], pointDict[gapA][2], 'newguildcurve.cv[1]', rpr=True)
        mc.move(pointDict[gapB][0], pointDict[gapB][1], pointDict[gapB][2], 'newguildcurve.cv[2]', rpr=True)
        mc.move(pointDict[gapC][0], pointDict[gapC][1], pointDict[gapC][2], 'newguildcurve.cv[3]', rpr=True)
    mc.delete('newguildcurve', ch=1)
    mc.move(cameraPosition[0], cameraPosition[1], cameraPosition[2], 'newguildcurve.scalePivot', 'newguildcurve.rotatePivot')
    mc.duplicate('newguildcurve')
    mc.setAttr('newguildcurve.scaleX', 0.5)
    mc.setAttr('newguildcurve.scaleY', 0.5)
    mc.setAttr('newguildcurve.scaleZ', 0.5)
    mc.setAttr('newguildcurve1.scaleX', 2)
    mc.setAttr('newguildcurve1.scaleY', 2)
    mc.setAttr('newguildcurve1.scaleZ', 2)
    mc.nurbsToPolygonsPref(polyType=1, format=3, uType=3, uNumber=1, vType=3, vNumber=1)
    loftNode = mc.loft('newguildcurve1', 'newguildcurve', ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, po=1, rsn=True)
    mc.rename('guildMesh')
    mc.polySmooth('guildMesh', mth=0, sdt=2, ovb=1, ofb=3, ofc=0, ost=0, ocr=0, dv=2, bnr=1, c=1, kb=1, ksb=1, khe=0, kt=1, kmb=1, suv=1, peh=0, sl=1, dpe=1, ps=0.1, ro=1, ch=0)
    mc.transferAttributes('guildMesh', listVtx, transferPositions=1, searchMethod=3)
    shapesNode = mc.listRelatives(listVtx[0], shapes=True, ap=True)
    mc.delete(shapesNode, ch=1)
    O38()
def O38():
    cleanSceneList = {'refPlan*','newguildcurv*','newguildcurv*','guildMes*','baseLo*','newDeformcurv*'}
    for c in cleanSceneList:
        if mc.objExists(c):
            mc.delete(c)
def O39(level):
    edgeLoopSel = mc.ls(sl=1,fl=1)
    sortGrp = O8l()
    for e in sortGrp:
        O4O(e,level)
    meshName = edgeLoopSel[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(edgeLoopSel)
def O4O(flatList,level):
    checkEven = mc.checkBox('evenCurveEdgeLength', q=1,v=1)
    O38()
    listVtx = O76(flatList)
    numberPoint = level
    distList = []
    totalDist = 0
    xA, yA, zA = mc.pointPosition(listVtx[0], w=1)
    xB, yB, zB = mc.pointPosition(listVtx[-1], w=1)
    mc.curve(d=1, p=[(xA, yA, zA),(xB, yB, zB)])
    mc.rename('newguildcurve')
    for i in range(len(listVtx)-1):
        xA, yA, zA = mc.pointPosition(listVtx[i], w=1)
        xB, yB, zB = mc.pointPosition(listVtx[i+1], w=1)
        distanceBetween = math.sqrt((xA - xB) * (xA - xB) + (yA - yB) * (yA - yB) + (zA - zB) * (zA - zB))
        distList.append(distanceBetween)
        totalDist = totalDist + distanceBetween
    if numberPoint == 1:
        mc.rebuildCurve('newguildcurve', ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=1, d=3, tol=0)
        gapA = int(len(listVtx) * 0.5)
        xA, yA, zA = mc.pointPosition(listVtx[gapA], w=1)
        mc.select('newguildcurve.cv[1]','newguildcurve.cv[2]')
        nodeCluster = mc.cluster(n= 'midGrp')
        mc.spaceLocator(n='baseLoc')
        mc.select('baseLoc',nodeCluster[1])
        mc.matchTransform()
        mc.move( xA, yA, zA, nodeCluster[1], rpr =1)
        mc.select(nodeCluster[1],'baseLoc')
        mc.parent()
        mc.setAttr("baseLoc.scale", 1.33, 1.33, 1.33)
    elif numberPoint == 2:
        mc.rebuildCurve('newguildcurve', ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=2, d=2, tol=0)
        gapA = int(len(listVtx) * 0.33333)
        gapB = int(len(listVtx) * 0.66666)
        xA, yA, zA = mc.pointPosition(listVtx[gapA], w=1)
        xB, yB, zB = mc.pointPosition(listVtx[gapB ], w=1)
        mc.move( xA, yA, zA, 'newguildcurve.cv[1]', a =True, ws=True)
        mc.move( xB, yB, zB, 'newguildcurve.cv[2]', a =True, ws=True)
    elif numberPoint == 3:
        mc.rebuildCurve('newguildcurve', ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=3, d=2, tol=0)
        gapA = int(len(listVtx) * 0.25)
        gapB = int(len(listVtx) * 0.5)
        gapC = int(len(listVtx) * 0.75)
        xA, yA, zA = mc.pointPosition(listVtx[gapA], w=1)
        xB, yB, zB = mc.pointPosition(listVtx[gapB ], w=1)
        xC, yC, zC = mc.pointPosition(listVtx[gapC ], w=1)
        mc.move( xA, yA, zA, 'newguildcurve.cv[1]', a =True, ws=True)
        mc.move( xB, yB, zB, 'newguildcurve.cv[2]', a =True, ws=True)
        mc.move( xC, yC, zC, 'newguildcurve.cv[3]', a =True, ws=True)
    mc.rebuildCurve('newguildcurve', ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=100, d=3, tol=0)
    currentU = 0
    prV = 0
    gapDist = 1.0/(len(listVtx)-1)
    scaleV = 1/totalDist
    for j in range(len(listVtx)-2):
        if checkEven == 1:
            prV = currentU + gapDist
        else:
            prV = currentU + (scaleV * distList[j])
        currentU = prV
        xj, yj, zj = mc.pointOnCurve('newguildcurve', pr= currentU, p=1)
        mc.move(xj, yj, zj,listVtx[j+1] , a =True, ws=True)

    O38()

def O41(dir,startMode):
    global edgeCurlRunMoveCV
    global edgeCurlRunSel
    global edgeCurlRunDistList
    global startModeRecord
    startModeRecord = startMode
    modifiers = 0
    if startMode == 0:
        modifiers = mc.getModifiers()
    elif startMode == 1:
        modifiers = 1
    elif startMode == 4:
        modifiers = 4
    elif startMode == 100:
        modifiers = 0
    edgeCurlRunDistList = []
    edgeCurlRunSel = []
    edgeCurlRunMoveCV = []
    checkEndCV = []
    distList = []
    edgeSel = mc.ls(sl=1,fl=1)
    if len(edgeSel) == 1:
        mc.ConvertSelectionToVertices()
        selectsCV = mc.ls(sl=1,fl=1)
        mc.select(edgeSel)
        mc.SelectEdgeLoopSp()
        mc.ConvertSelectionToVertices()
        loopCVList = mc.ls(sl=1,fl=1)
        mc.select(selectsCV)
        mc.ConvertSelectionToEdges()
        mc.ConvertSelectionToVertices()
        surroundCV = mc.ls(sl=1,fl=1)
        commonList = list(set(surroundCV) & set(loopCVList))
        mc.select(commonList)
        mc.ConvertSelectionToContainedEdges()
        checkConnerEdge = mc.ls(sl=1,fl=1)
        if len(checkConnerEdge) == 3:
            mc.ConvertSelectionToFaces()
            checkConnerFace = mc.ls(sl=1,fl=1)
            if len(checkConnerFace)==2:
                mc.select(edgeSel)
                mc.GrowLoopPolygonSelectionRegion()
            elif len(checkConnerFace) > 2:
                mc.select(checkConnerEdge)
    else:
        mc.setToolTo( 'moveSuperContext' )
    getCircleState,listVtx = O78()
    if getCircleState == 0:
        edgeCurlRunSel = edgeSel
        cleanList = ('tempGuid*','arcCurv*','upperLo*','aimLo*','baseLo*','makeThreePointCircularAr*','tempGuideLin*')
        for c in cleanList:
            if mc.objExists(c):
                mc.delete(c)
        leftCV = ''
        rightCV = ''
        view = omui.M3dView.active3dView()
        cam = om.MDagPath()
        view.getCamera(cam)
        camPath = cam.fullPathName()
        cameraTrans = mc.listRelatives(camPath,type='transform',p=True)
        CurrentCam = cameraTrans[0]
        xA, yA, zA = mc.pointPosition(listVtx[0], w=1)
        A2D = O27(cameraTrans[0], (xA,yA,zA))
        xB, yB, zB = mc.pointPosition(listVtx[-1], w=1)
        B2D = O27(cameraTrans[0], (xB,yB,zB))
        if A2D[0] < B2D[0]:
            leftCV = listVtx[0]
            rightCV = listVtx[-1]
        else:
            rightCV = listVtx[0]
            leftCV = listVtx[-1]
        if leftCV == listVtx[-1]:
            listVtx.reverse()
        if dir == 'L':
            listVtx.reverse()
        if len(edgeSel) == 1:
            xA, yA, zA = mc.pointPosition(listVtx[-1], w=1)
            xB, yB, zB = mc.pointPosition(listVtx[-2], w=1)
            distanceBetween = math.sqrt((xA - xB) * (xA - xB) + (yA - yB) * (yA - yB) + (zA - zB) * (zA - zB))
            distList.append(distanceBetween)
        elif len(edgeSel) > 2:
            distList = []
            for i in range(len(listVtx)-1):
                xA, yA, zA = mc.pointPosition(listVtx[i], w=1)
                xB, yB, zB = mc.pointPosition(listVtx[i+1], w=1)
                distanceBetween = math.sqrt((xA - xB) * (xA - xB) + (yA - yB) * (yA - yB) + (zA - zB) * (zA - zB))
                distList.append(distanceBetween)
        edgeCurlRunDistList = distList
        firstCV = listVtx[0]
        secCV = listVtx[1]
        thirdCV = ''
        if len(edgeSel) == 1:
            thirdCV = listVtx[2]
        else:
            thirdCV = listVtx[-1]
        edgeCurlRunMoveCV = listVtx
        if startMode != 100:
            p1 = mc.pointPosition(firstCV, w=1)
            p2 = mc.pointPosition(secCV, w=1)
            p3 = mc.pointPosition(thirdCV, w=1)
            newNode = mc.createNode('makeThreePointCircularArc')
            mc.setAttr(newNode + '.pt1', p1[0], p1[1], p1[2])
            mc.setAttr(newNode + '.pt2', p2[0], p2[1], p2[2])
            mc.setAttr(newNode + '.pt3', p3[0], p3[1], p3[2])
            mc.setAttr(newNode + '.d', 3)
            mc.setAttr(newNode + '.s', 4)
            newCurve = mc.createNode('nurbsCurve')
            mc.select(cl=1)
            mc.connectAttr(newNode + '.oc', newCurve + '.cr')
            transformNode = mc.listRelatives(newCurve, fullPath=True, parent=True)
            mc.rename(transformNode, 'arcCurve')
            cmd = 'doMenuComponentSelection("' + edgeCurlRunMoveCV[0].split('.')[0] +'", "edge");'
            mel.eval(cmd)
            mc.select(edgeSel)
            mc.refresh(f=True)
            cPos = mc.getAttr( newNode +'.center')
            mc.move( cPos[0][0],  cPos[0][1],  cPos[0][2],'arcCurve.scalePivot' ,'arcCurve.rotatePivot' , a =True, ws=True)
            mc.delete(ch=1)
            circleR =  math.sqrt((p1[0] - cPos[0][0]) * (p1[0]  - cPos[0][0]) + (p1[1]  - cPos[0][1]) * (p1[1]  - cPos[0][1]) + (p1[2]  - cPos[0][2]) * (p1[2]  - cPos[0][2]))
            mc.spaceLocator(n='upperLoc')
            mc.spaceLocator(n='aimLoc')
            mc.spaceLocator(n='baseLoc')
            mc.select('upperLoc','aimLoc','baseLoc')
            mc.CenterPivot()
            mc.setAttr(('upperLoc.scale'),0.01,0.01,0.01)
            mc.setAttr(('aimLoc.scale'),0.01,0.01,0.01)
            mc.setAttr(('aimLoc.translate'),0, 1,-1)
            mc.setAttr(('upperLoc.translate'),0, 1,1)
            consNode = mc.aimConstraint('aimLoc','baseLoc',offset=[0,0,0], weight=1, aimVector=[1,0,0], upVector=[0,1,0], worldUpType='object', worldUpObject='upperLoc')
            mc.setAttr(('baseLoc.translate'),cPos[0][0], cPos[0][1], cPos[0][2])
            mc.setAttr(('aimLoc.translate'),p3[0], p3[1], p3[2])
            mc.setAttr(('upperLoc.translate'),p1[0], p1[1], p1[2])
            mc.circle( nr=(0, 0, 1), c=(0, 0, 0),r= circleR,n='tempGuide')
            mc.displaySmoothness(divisionsU=3, divisionsV=3, pointsWire=16, pointsShaded=4, polygonObject=3)
            mc.setAttr("tempGuideShape.overrideEnabled", 1)
            mc.setAttr("tempGuideShape.overrideColor",31)
            mc.select('tempGuide','baseLoc')
            mc.matchTransform()
            mc.select('baseLoc',d=1)
            mc.makeIdentity('tempGuide', apply=1, t=1,r=1,s=1)
            mc.ReverseCurve()
            mc.delete(ch=1)
            mc.move(  p2[0],   p2[1],   p2[2],'tempGuide.scalePivot' ,'tempGuide.rotatePivot' , a =True, ws=True)
        else:
            if len(edgeSel) == 1:
                mc.select(edgeSel)
            else:
                mc.select(edgeCurlRunMoveCV[0],edgeCurlRunMoveCV[1])
                mc.ConvertSelectionToContainedEdges()
            mc.polyToCurve(form=0, degree=1, conformToSmoothMeshPreview=1)
            mc.rename('tempGuide')
            mc.CenterPivot()
            mc.ReverseCurve()
            mc.delete(ch=1)
            mc.setAttr("tempGuide.scale",50,50,50)
            mc.makeIdentity('tempGuide', apply=1, t=1,r=1,s=1)
        checkLock = mc.checkBox('lockCurveEdgeLength', q=1,v=1)
        checkEven = mc.checkBox('evenCurveEdgeLength', q=1,v=1)
        if startMode == 100:
            xA, yA, zA = mc.pointPosition('tempGuide.cv[0]', w=1)
            A2D = O27(cameraTrans[0], (xA,yA,zA))
            xB, yB, zB = mc.pointPosition('tempGuide.cv[1]', w=1)
            B2D = O27(cameraTrans[0], (xB,yB,zB))
            if A2D[0] > B2D[0]:
                mc.select('tempGuide')
                mc.ReverseCurve()
            if dir == 'L':
                mc.select('tempGuide')
                mc.ReverseCurve()
            if checkEven == 1 and len(edgeSel) > 1:
                O3l(edgeSel)
            if checkLock == 0:
                selectionList = om.MSelectionList()
                selectionList.add('tempGuide')
                dagPath = om.MDagPath()
                selectionList.getDagPath(0, dagPath)
                omCurveOut = om.MFnNurbsCurve(dagPath)
                for m in range(1,len(edgeCurlRunMoveCV)) :
                    xK, yK, zK = mc.pointPosition(edgeCurlRunMoveCV[m], w=1)
                    pointInSpace = om.MPoint(xK,yK,zK)
                    closestPoint = om.MPoint()
                    closestPoint = omCurveOut.closestPoint(pointInSpace)
                    mc.move( closestPoint[0], closestPoint[1], closestPoint[2],edgeCurlRunMoveCV[m] , a =True, ws=True)
            else:
                circleLength = mc.arclen( 'tempGuide' )
                maxU = mc.getAttr('tempGuide.maxValue')
                UScaleV = circleLength  / maxU
                if len(edgeSel) == 1:
                    xK, yK, zK = mc.pointPosition(edgeCurlRunMoveCV[-2], w=1)
                    getU = O24([xK, yK, zK], 'tempGuide')[0]
                    movingDist = distList[0]
                    moveV = movingDist / UScaleV
                    newU = getU + moveV
                    xj, yj, zj = mc.pointOnCurve('tempGuide', pr= newU, p=1)
                    mc.move(xj, yj, zj, edgeCurlRunMoveCV[-1] , a =True, ws=True)
                else:
                    for m in range(1,len(edgeCurlRunMoveCV)) :
                        xK, yK, zK = mc.pointPosition(edgeCurlRunMoveCV[m-1], w=1)
                        getU = O24([xK, yK, zK], 'tempGuide')[0]
                        movingDist = distList[m-1]
                        moveV = movingDist / UScaleV
                        newU = getU + moveV
                        xj, yj, zj = mc.pointOnCurve('tempGuide', pr= newU, p=1)
                        mc.move(xj, yj, zj, edgeCurlRunMoveCV[m] , a =True, ws=True)
        else:
            if checkLock == 0:
                selectionList = om.MSelectionList()
                selectionList.add('tempGuide')
                dagPath = om.MDagPath()
                selectionList.getDagPath(0, dagPath)
                omCurveOut = om.MFnNurbsCurve(dagPath)
                if checkEven == 1:
                    O3l(edgeSel)
                for m in range(1,len(edgeCurlRunMoveCV)) :
                    xK, yK, zK = mc.pointPosition(edgeCurlRunMoveCV[m], w=1)
                    pointInSpace = om.MPoint(xK,yK,zK)
                    closestPoint = om.MPoint()
                    closestPoint = omCurveOut.closestPoint(pointInSpace)
                    mc.move(closestPoint[0], closestPoint[1], closestPoint[2], edgeCurlRunMoveCV[m] , a =True, ws=True)
            else:
                circleLength = mc.arclen( 'tempGuide' )
                maxU = mc.getAttr('tempGuide.maxValue')
                UScaleV = circleLength  / maxU
                if len(edgeSel) == 1:
                    xK, yK, zK = mc.pointPosition(edgeCurlRunMoveCV[-2], w=1)
                    getU = O24([xK, yK, zK], 'tempGuide')[0]
                    movingDist = distList[0]
                    moveV = movingDist / UScaleV
                    newU = getU + moveV
                    xj, yj, zj = mc.pointOnCurve('tempGuide', pr= newU, p=1)
                    mc.move(xj, yj, zj, edgeCurlRunMoveCV[-1] , a =True, ws=True)
                else:
                    for m in range(1,len(edgeCurlRunMoveCV)) :
                        xK, yK, zK = mc.pointPosition(edgeCurlRunMoveCV[m-1], w=1)
                        getU = O24([xK, yK, zK], 'tempGuide')[0]
                        movingDist = distList[m-1]
                        moveV = movingDist / UScaleV
                        newU = getU + moveV
                        xj, yj, zj = mc.pointOnCurve('tempGuide', pr= newU, p=1)
                        mc.move(xj, yj, zj, edgeCurlRunMoveCV[m] , a =True, ws=True)
        cleanList = []
        if len(edgeSel) == 1:
            mc.select(edgeCurlRunMoveCV[-2],edgeCurlRunMoveCV[-1])
            mc.ConvertSelectionToContainedEdges()
            selNew=mc.ls(sl=1)
            cmd = 'doMenuComponentSelection("' + edgeSel[0].split('.')[0] +'", "edge");'
            mel.eval(cmd)
            mc.select(selNew)
            cleanList = ('tempGuid*','arcCurv*','upperLo*','aimLo*','baseLo*','makeThreePointCircularAr*','tempGuideLin*')
        else:
            if startMode!= 100:
                global ctx
                ctx = 'edgeCurlRun'
                if mc.draggerContext(ctx, exists=True):
                    mc.deleteUI(ctx)
                mc.draggerContext(ctx, pressCommand = O45, rc = O42, dragCommand = O43, fnz = O44, name=ctx, cursor='crossHair',undoMode='step')
                mc.setToolTo(ctx)
                cleanList = ('arcCurv*','upperLo*','aimLo*','baseLo*','makeThreePointCircularAr*','tempGuideLin*')
            else:
                cleanList = ('tempGuid*','arcCurv*','upperLo*','aimLo*','baseLo*','makeThreePointCircularAr*','tempGuideLin*')
            mc.select(edgeSel)
            cmd = 'doMenuComponentSelection("' + edgeSel[0].split('.')[0] +'", "edge");'
            mel.eval(cmd)
            mc.select(edgeCurlRunSel)
        for c in cleanList:
            if mc.objExists(c):
                mc.delete(c)

def O42():
    lineList = ('tempGuide','tempGuideLine')
    for l in lineList:
        if mc.objExists(l):
            mc.setAttr((l + ".visibility"),0)

def O43():
    global edgeCurlRunMoveCV
    global edgeCurlRunSel
    global screenX,screenY
    global ctx
    global currentScaleRecord
    global edgeCurlRunDistList
    global startModeRecord
    currentRotRecord = 0
    currentEnRecord = 0
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
    screenX = vpX
    screenY = vpY
    selectionList = om.MSelectionList()
    selectionList.add('tempGuide')
    dagPath = om.MDagPath()
    selectionList.getDagPath(0, dagPath)
    omCurveOut = om.MFnNurbsCurve(dagPath)
    if currentScaleRecord > vpX:
        mc.setAttr('tempGuide.scale',1.02,1.02,1.02)
    else:
        mc.setAttr('tempGuide.scale',0.98,0.98,0.98)
    currentScaleRecord = vpX
    mc.makeIdentity('tempGuide', apply=1, t=1,r=1,s=1)
    checkLock = mc.checkBox('lockCurveEdgeLength', q=1,v=1)
    if(checkLock == 1):
        mc.setAttr("tempGuide.visibility",1)
        circleLength = mc.arclen( 'tempGuide' )
        maxU = mc.getAttr('tempGuide.maxValue')
        UScaleV = circleLength  / maxU
        for m in range(1,len(edgeCurlRunMoveCV)) :
            xK, yK, zK = mc.pointPosition(edgeCurlRunMoveCV[m-1], w=1)
            getU = O24([xK, yK, zK], 'tempGuide')[0]
            movingDist = edgeCurlRunDistList[m-1]
            moveV = movingDist / UScaleV
            newU = getU + moveV
            xj, yj, zj = mc.pointOnCurve('tempGuide', pr= newU, p=1)
            mc.move(xj, yj, zj, edgeCurlRunMoveCV[m] , a =True, ws=True)
    else:
        mc.setAttr("tempGuide.visibility",1)
        for m in range(1,len(edgeCurlRunMoveCV)) :
            xK, yK, zK = mc.pointPosition(edgeCurlRunMoveCV[m], w=1)
            pointInSpace = om.MPoint(xK,yK,zK)
            closestPoint = om.MPoint()
            closestPoint = omCurveOut.closestPoint(pointInSpace)
            mc.move(closestPoint[0], closestPoint[1], closestPoint[2], edgeCurlRunMoveCV[m] , a =True, ws=True)
    mc.refresh(f=True)

def O44():
    cleanList = ('tempGuid*','arcCurv*','upperLo*','aimLo*','baseLo*','makeThreePointCircularAr*','tempGuideLin*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)

def O45():
    global edgeCurlRunMoveCV
    global edgeCurlRunSel
    global screenX,screenY
    global ctx
    global currentScaleRecord
    currentScaleRecord = 0
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY

def O46():
    mc.checkBox('lockCurveEdgeLength', e=1,v=1)
    mc.checkBox('evenCurveEdgeLength', e=1,v=0)
    mc.setToolTo( 'moveSuperContext' )

def O47():
    mc.checkBox('lockCurveEdgeLength', e=1,v=0)
    mc.setToolTo( 'moveSuperContext' )

def O48():
    mc.checkBox('lockCurveEdgeLength', e=1,v=0)
    mc.checkBox('evenCurveEdgeLength', e=1,v=1)
    mc.setToolTo( 'moveSuperContext' )

def O49():
    mc.checkBox('evenCurveEdgeLength', e=1,v=0)
    mc.setToolTo( 'moveSuperContext' )

def O50():
    global curveGrp
    global totalLenGrp
    global ctx
    global listVtxFGrp
    global radiusBestFitGrp
    global arcGrp
    global radiusGrp
    global blendNodeList
    global ulistGrp
    global sectionNumber
    listVtxFGrp = []
    totalLenGrp = []
    ulistGrp = []
    curveGrp = []
    arcGrp = []
    radiusGrp = []
    radiusBestFitGrp = []
    blendNodeList = []
    selEdge = mc.filterExpand(expand=True, sm=32)
    if selEdge:
        if mc.objExists('saveSelSemi'):
            mc.delete('saveSelSemi')
        mc.sets(name='saveSelSemi', text='saveSelSemi')
        sortGrp = O8l()
        for e in sortGrp:
            listVtx = O76(e)
            firstN = listVtx[0].split('[')[1].split(']')[0]
            secN = listVtx[1].split('[')[1].split(']')[0]
            if int(firstN) > int(secN):
                listVtx.reverse()
            listVtxFGrp.append(listVtx)
            positionListA = []
            for n in listVtx:
                getPo = mc.pointPosition(n, w=1)
                positionListA.append(getPo)
            p1 = mc.pointPosition(listVtx[0], w=1)
            p2 = mc.pointPosition(listVtx[-1], w=1)
            radius = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2) / 2
            p3 = mc.pointPosition(listVtx[int(len(listVtx) / 2)], w=1)
            p4 = [(p2[0] + p1[0]) / 2, (p2[1] + p1[1]) / 2, (p2[2] + p1[2]) / 2]
            distanceBC = math.sqrt((p4[0] - p3[0]) ** 2 + (p4[1] - p3[1]) ** 2 + (p4[2] - p3[2]) ** 2) / 2
            if distanceBC < 0.001:
                distanceBC = 0.001
            distanceBD = radius / 2.0
            OD = (distanceBC ** 2 + distanceBD ** 2) / (2 * distanceBC)
            newR = radius + OD
            radiusBestFitGrp.append(newR)
            radiusGrp.append(radius)
            newNode = mc.createNode('makeTwoPointCircularArc')
            arcGrp.append(newNode)
            mc.setAttr(newNode + '.pt1', p1[0], p1[1], p1[2])
            mc.setAttr(newNode + '.pt2', p2[0], p2[1], p2[2])
            mc.setAttr(newNode + '.tac', 0)
            mc.setAttr(newNode + '.r', newR)
            mc.setAttr(newNode + '.d', 3)
            sectionNumber = len(e)
            mc.setAttr(newNode + '.s', sectionNumber)
            newCurve = mc.createNode('nurbsCurve')
            mc.connectAttr(newNode + '.oc', newCurve + '.cr')
            transformNode = mc.listRelatives(newCurve, fullPath=True, parent=True)
            curveName = mc.listRelatives(parent=True)
            curveGrp.append(curveName[0])
            mc.setAttr(curveName[0] + '.visibility', 0)
            cvList = []
            cvList.append(listVtx[0])
            cvList.append(listVtx[int(len(listVtx) / 2)])
            cvList.append(listVtx[-1])
            points = []
            for cv in cvList:
                x, y, z = mc.pointPosition(cv, w=1)
                this_point = om.MPoint(x, y, z)
                points.append(this_point)
            vectors = [ points[i + 1] - points[i] for i in range(len(points) - 1) ]
            if vectors[0] == vectors[1]:
                mc.move(0.001, 0, 0, e[1:-1], r=1, cs=1, ls=1, wd=1)
                points = []
                for cv in cvList:
                    x, y, z = mc.pointPosition(cv, w=1)
                    this_point = om.MPoint(x, y, z)
                    points.append(this_point)
                vectors = [ points[i + 1] - points[i] for i in range(len(points) - 1) ]
            Nx = vectors[0][1] * vectors[1][2] - vectors[0][2] * vectors[1][1]
            Ny = vectors[0][2] * vectors[1][0] - vectors[0][0] * vectors[1][2]
            Nz = vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0]
            mc.setAttr(newNode + '.directionVectorX', Nx)
            mc.setAttr(newNode + '.directionVectorY', Ny)
            mc.setAttr(newNode + '.directionVectorZ', Nz)
            mc.group(em=True, name=curveName[0] + '_offsetSemi')
            mc.group(em=True, name=curveName[0] + '_aim')
            mc.setAttr(curveName[0] + '_offsetSemi.translateX', p1[0])
            mc.setAttr(curveName[0] + '_offsetSemi.translateY', p1[1])
            mc.setAttr(curveName[0] + '_offsetSemi.translateZ', p1[2])
            mc.setAttr(curveName[0] + '_aim.translateX', p2[0])
            mc.setAttr(curveName[0] + '_aim.translateY', p2[1])
            mc.setAttr(curveName[0] + '_aim.translateZ', p2[2])
            const = mc.aimConstraint(curveName[0] + '_aim', curveName[0] + '_offsetSemi')
            mc.delete(const, curveName[0] + '_aim')
            mc.parent(curveName[0], curveName[0] + '_offsetSemi')
            mc.FreezeTransformations()
            mc.move(p1[0], p1[1], p1[2], curveName[0] + '.scalePivot', curveName[0] + '.rotatePivot', a=1)
            totalEdgeLoopLength = 0
            sum = 0
            Llist = []
            uList = []
            pList = []
            for i in range(len(listVtx) - 1):
                pA = mc.pointPosition(listVtx[i], w=1)
                pB = mc.pointPosition(listVtx[i + 1], w=1)
                checkDistance = math.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2 + (pA[2] - pB[2]) ** 2)
                Llist.append(checkDistance)
                totalEdgeLoopLength = totalEdgeLoopLength + checkDistance
            totalLenGrp.append(totalEdgeLoopLength)
            goEven = mc.checkBox('evenCurveEdgeLength', q=1, v=1)
            if goEven == 1:
                avg = totalEdgeLoopLength / len(e)
                for j in range(len(e)):
                    sum = (j + 1) * avg
                    uList.append(sum)
            else:
                for j in Llist:
                    sum = sum + j
                    uList.append(sum)

            ulistGrp.append(uList)
            for k in uList:
                p = k / totalEdgeLoopLength * sectionNumber
                pList.append(p)

            for q in range(len(pList) - 1):
                pp = mc.pointOnCurve(curveName[0], pr=pList[q], p=1)
                mc.move(pp[0], pp[1], pp[2], listVtx[q + 1], a=True, ws=True)
            backupCurve = mc.duplicate(curveName[0])
            p1A = mc.pointPosition(listVtx[1], w=1)
            p2A = mc.pointPosition(listVtx[-2], w=1)
            mid1x = (p1A[0] - p1[0]) / 2 + p1[0]
            mid1y = (p1A[1] - p1[1]) / 2 + p1[1]
            mid1z = (p1A[2] - p1[2]) / 2 + p1[2]
            mid2x = (p2A[0] - p2[0]) / 2 + p2[0]
            mid2y = (p2A[1] - p2[1]) / 2 + p2[1]
            mid2z = (p2A[2] - p2[2]) / 2 + p2[2]
            positionListA.insert(1, [mid1x, mid1y, mid1z])
            positionListA.insert(len(positionListA) - 1, [mid2x, mid2y, mid2z])
            for x in range(len(positionListA)):
                mc.move(positionListA[x][0], positionListA[x][1], positionListA[x][2], backupCurve[0] + '.cv[' + str(x) + ']', a=1)
            blendName = mc.blendShape(backupCurve[0], curveName[0], w=[(0, 1)], en=0)
            blendNodeList.append(blendName[0])
        meshName = selEdge[0].split('.')[0]
        cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
        mel.eval(cmd)
        mc.select(selEdge)
        ctx = 'unBevelCtx'
        if mc.draggerContext(ctx, exists=True):
            mc.deleteUI(ctx)
        mc.draggerContext(ctx, pressCommand=O53, rc=O52, dragCommand=O54, fnz=O5l, name=ctx, cursor='crossHair', undoMode='step')
        mc.setToolTo(ctx)
def O5l():
    mc.setToolTo('selectSuperContext')
    cleanList = ('makeTwoPointCircularAr*','*Semi*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
def O52():
    mc.setToolTo('selectSuperContext')
    cleanList = ('makeTwoPointCircularAr*','*Semi*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
def O53():
    global currentRotRecord
    global currentEnRecord
    global screenX
    global screenY
    currentRotRecord = 0
    currentEnRecord = 0
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
    t = radiusGrp[0] / radiusBestFitGrp[0]
    screenX = (vpX + t) / 1.9
def O54():
    global currentRotRecord
    global currentEnRecord
    modifiers = mc.getModifiers()
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
    distanceA = (vpX - screenX) / 100
    t = distanceA
    fu = 1 / (1 + t ** 5 / 100)
    if modifiers == 4:
        for c in curveGrp:
            mc.setAttr(c + '.rotateX', 0)
    elif modifiers == 1:
        rotateRun = mc.getAttr(curveGrp[0] + '.rotateX')
        if currentRotRecord > vpX:
            rotateRun = rotateRun + 2
        else:
            rotateRun = rotateRun - 2
        for c in curveGrp:
            mc.setAttr(c + '.rotateX', rotateRun)
        currentRotRecord = vpX
    elif modifiers == 8:
        evRun = mc.getAttr(blendNodeList[0] + '.envelope')
        if currentEnRecord > vpX:
            evRun = evRun + 0.05
        else:
            evRun = evRun - 0.05
        if evRun > 1:
            evRun = 1
        elif evRun < 0:
            evRun = 0
        for f in blendNodeList:
            mc.setAttr(f + '.envelope', evRun)
        currentEnRecord = vpX
    else:
        for f in blendNodeList:
            mc.setAttr(f + '.envelope', 0)

        for a in range(len(arcGrp)):
            newR = radiusGrp[a] * (1 + fu * 5)
            mc.setAttr(arcGrp[a] + '.radius', newR)
    for i in range(len(arcGrp)):
        pList = []
        uList = ulistGrp[i]
        for k in uList:
            p = k / totalLenGrp[i] * sectionNumber
            pList.append(p)
        listVtx = listVtxFGrp[i]
        for q in range(len(pList) - 1):
            pp = mc.pointOnCurve(curveGrp[i], pr=pList[q], p=1)
            mc.move(pp[0], pp[1], pp[2], listVtx[q + 1], a=True, ws=True)
    mc.refresh(f=True)
def O55():
    global selEdge
    global selMeshForDeformer
    global ctx
    selEdge = mc.filterExpand(expand=True, sm=32)
    currentDropOff = 1
    snapCheck = 1
    goEven = mc.checkBox('evenCurveEdgeLength', q=1, v=1)
    conP = 2
    curveT = 1
    goArc = 1
    selMeshForDeformer = mc.ls(sl=1, o=1)
    getCircleState, listVtx = O78()
    deformerNames = []
    midP = int(len(listVtx) / 2)
    mc.move(0.01, 0, 0, selEdge[midP], r=1, cs=1, ls=1, wd=1)
    p1 = mc.pointPosition(listVtx[0], w=1)
    p2 = mc.pointPosition(listVtx[midP], w=1)
    p3 = mc.pointPosition(listVtx[-1], w=1)
    newNode = mc.createNode('makeThreePointCircularArc')
    mc.setAttr(newNode + '.pt1', p1[0], p1[1], p1[2])
    mc.setAttr(newNode + '.pt2', p2[0], p2[1], p2[2])
    mc.setAttr(newNode + '.pt3', p3[0], p3[1], p3[2])
    mc.setAttr(newNode + '.d', 3)
    mc.setAttr(newNode + '.s', len(listVtx))
    newCurve = mc.createNode('nurbsCurve')
    mc.connectAttr(newNode + '.oc', newCurve + '.cr')
    mc.delete(ch=1)
    transformNode = mc.listRelatives(newCurve, fullPath=True, parent=True)
    mc.rename(transformNode, 'arcCurve')
    numberP = 0
    numberP = int(conP) - 1
    mc.rebuildCurve('arcCurve', ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=numberP, d=3, tol=0.01)
    mc.delete('arcCurve', ch=1)
    totalEdgeLoopLength = 0
    sum = 0
    Llist = []
    uList = []
    pList = []
    for i in selEdge:
        e2v = mc.polyListComponentConversion(i, fe=1, tv=1)
        e2v = mc.ls(e2v, fl=1)
        pA = mc.pointPosition(e2v[0], w=1)
        pB = mc.pointPosition(e2v[1], w=1)
        checkDistance = math.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2 + (pA[2] - pB[2]) ** 2)
        Llist.append(checkDistance)
        totalEdgeLoopLength = totalEdgeLoopLength + checkDistance
    if goEven == 1:
        avg = totalEdgeLoopLength / len(selEdge)
        for j in range(len(selEdge)):
            sum = (j + 1) * avg
            uList.append(sum)
    else:
        for j in Llist:
            sum = sum + j
            uList.append(sum)
    for k in uList:
        p = k / totalEdgeLoopLength
        pList.append(p)
    for q in range(len(pList)):
        if q + 1 == len(listVtx):
            pp = mc.pointOnCurve('arcCurve', pr=0, p=1)
            mc.move(pp[0], pp[1], pp[2], listVtx[0], a=True, ws=True)
        else:
            pp = mc.pointOnCurve('arcCurve', pr=pList[q], p=1)
            mc.move(pp[0], pp[1], pp[2], listVtx[q + 1], a=True, ws=True)
    mc.delete('arcCurve', ch=1)
    mc.select('arcCurve')
    mc.nurbsCurveToBezier()
    try:
        deformerNames = mc.wire(selMeshForDeformer, gw=0, en=1, ce=0, li=0, w='arcCurve', uct=0)
    except:
        deformerNames = mc.wire(selMeshForDeformer, gw=0, en=1, ce=0, li=0, w='arcCurve')
    mc.setAttr(deformerNames[0] + '.dropoffDistance[0]', 0.1)
    cA = mc.pointPosition('arcCurve.cv[0]', w=1)
    cD = mc.pointPosition('arcCurve.cv[3]', w=1)
    try:
        mc.select('arcCurve.cv[1]')
        mc.cluster(useComponentTags=0)
        checkSel = mc.ls(sl=1)
        mc.rename(checkSel[0], 'ccBHandle')
    except:
        mc.cluster('arcCurve.cv[1]', name='ccB')

    mc.move(cA[0], cA[1], cA[2], 'ccBHandle.scalePivot', 'ccBHandle.rotatePivot', a=True, ws=True)
    try:
        mc.select('arcCurve.cv[2]')
        mc.cluster(useComponentTags=0)
        checkSel = mc.ls(sl=1)
        mc.rename(checkSel[0], 'ccCHandle')
    except:
        mc.cluster('arcCurve.cv[2]', name='ccC')
    mc.move(cD[0], cD[1], cD[2], 'ccCHandle.scalePivot', 'ccCHandle.rotatePivot', a=True, ws=True)
    mc.setAttr('arcCurve.visibility', 0)
    mc.setAttr('ccBHandle.visibility', 0)
    mc.setAttr('ccCHandle.visibility', 0)
    meshName = selEdge[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(selEdge)
    hideList = ['arcCurve','arcCurveBaseWire','ccBHandle','ccCHandle']
    for h in hideList:
        mc.setAttr((h + '.hiddenInOutliner'), 1)
    ctx = 'tensionCtx'
    if mc.draggerContext(ctx, exists=True):
        mc.deleteUI(ctx)
    mc.draggerContext(ctx, pressCommand=O58, rc=O57, dragCommand=O59, fnz=O56, name=ctx, cursor='crossHair', undoMode='step')
    mc.setToolTo(ctx)
def O56():
    mc.delete(selMeshForDeformer, ch=1)
    mc.setToolTo('selectSuperContext')
    cleanList = ('arc*','cc*Handl*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
def O57():
    pass
def O58():
    global screenX
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, anchorPoint=True)
    screenX = vpX
def O59():
    modifiers = mc.getModifiers()
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
    distanceA = (screenX - vpX) / 100
    t = 1 + distanceA
    if modifiers == 4:
        mc.setAttr('ccBHandle.scaleX', t)
        mc.setAttr('ccBHandle.scaleY', t)
        mc.setAttr('ccBHandle.scaleZ', t)
    elif modifiers == 1:
        mc.setAttr('ccCHandle.scaleX', t)
        mc.setAttr('ccCHandle.scaleY', t)
        mc.setAttr('ccCHandle.scaleZ', t)
    elif modifiers == 8:
        mc.setAttr('ccBHandle.scaleX', 1)
        mc.setAttr('ccBHandle.scaleY', 1)
        mc.setAttr('ccBHandle.scaleZ', 1)
        mc.setAttr('ccCHandle.scaleX', 1)
        mc.setAttr('ccCHandle.scaleY', 1)
        mc.setAttr('ccCHandle.scaleZ', 1)
    else:
        mc.setAttr('ccBHandle.scaleX', t)
        mc.setAttr('ccBHandle.scaleY', t)
        mc.setAttr('ccBHandle.scaleZ', t)
        mc.setAttr('ccCHandle.scaleX', t)
        mc.setAttr('ccCHandle.scaleY', t)
        mc.setAttr('ccCHandle.scaleZ', t)
    mc.refresh(f=True)
def O6o():
    global vLData
    global cLData
    global ctx
    global ppData
    checCurrentkHUD = mc.headsUpDisplay(lh=1)
    if checCurrentkHUD is not None:
        for t in checCurrentkHUD:
            mc.headsUpDisplay(t, rem=1)
    ppData = []
    vLData = []
    cLData = []
    selEdge = mc.filterExpand(expand=True, sm=32)
    if selEdge:
        if mc.objExists('saveSel'):
            mc.delete('saveSel')
        mc.sets(name='saveSel', text='saveSel')
        sortGrp = O8l()
        for e in sortGrp:
            pPoint, vList, cList = O66(e)
            ppData.append(pPoint)
            vLData.append(vList)
            cLData.append(cList)

        mc.select(selEdge)
        ctx = 'unBevelCtx'
        if mc.draggerContext(ctx, exists=True):
            mc.deleteUI(ctx)
        mc.draggerContext(ctx, pressCommand=O63, rc=O6l, dragCommand=O64, name=ctx, cursor='crossHair', undoMode='step')
        mc.setToolTo(ctx)
    return
def O6l():
    mc.headsUpDisplay('HUDunBevelStep', rem=True)
    flattenList = []
    for v in vLData:
        for x in range(len(v)):
            flattenList.append(v[x])
    mc.polyMergeVertex(flattenList, d=0.001, am=0, ch=0)
    mc.select('saveSel')
    meshName = flattenList[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.setToolTo('selectSuperContext')
    if mc.objExists('saveSel'):
        mc.delete('saveSel')
def O62():
    if viewPortCount >= 1:
        getPercent = viewPortCount / 100.0
    elif viewPortCount < 1 and viewPortCount > 0:
        getPercent = 0.1
    elif viewPortCount == 0:
        getPercent = 0
    getNumber = '%.2f' % getPercent
    return getNumber
def O63():
    global storeCount
    global screenX
    global screenY
    global viewPortCount
    global lockCount
    viewPortCount = 0
    lockCount = 50
    storeCount = 0
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, anchorPoint=True)
    screenX = vpX
    screenY = vpY
    lockX = vpX
    mc.headsUpDisplay('HUDunBevelStep', section=1, block=0, blockSize='large', label='unBevel', labelFontSize='large', command=currentStep, atr=1)
def O64():
    global storeCount
    global screenX
    global viewPortCount
    global lockCount
    movePN = 0
    modifiers = mc.getModifiers()
    vpX, vpY, _ = mc.draggerContext(ctx, query=True, dragPoint=True)
    if modifiers == 1:
        for i in range(len(ppData)):
            mc.scale(0, 0, 0, vLData[i], cs=1, r=1, p=(ppData[i][0], ppData[i][1], ppData[i][2]))
        viewPortCount = 0
    elif modifiers == 8:
        if screenX > vpX:
            lockCount = lockCount - 1
        else:
            lockCount = lockCount + 1
        screenX = vpX
        if lockCount > 0:
            getX = int(lockCount / 10) * 10
            if storeCount != getX:
                storeCount = getX
                for i in range(len(ppData)):
                    for v in range(len(vLData[i])):
                        moveX = ppData[i][0] - cLData[i][v][0] * lockCount
                        moveY = ppData[i][1] - cLData[i][v][1] * lockCount
                        moveZ = ppData[i][2] - cLData[i][v][2] * lockCount
                        mc.move(moveX, moveY, moveZ, vLData[i][v], absolute=1, ws=1)
            viewPortCount = storeCount
        else:
            viewPortCount = 0.1
    else:
        if screenX > vpX:
            lockCount = lockCount - 5
        else:
            lockCount = lockCount + 5
        screenX = vpX
        if lockCount > 0:
            for i in range(len(ppData)):
                for v in range(len(vLData[i])):
                    moveX = ppData[i][0] - cLData[i][v][0] * lockCount
                    moveY = ppData[i][1] - cLData[i][v][1] * lockCount
                    moveZ = ppData[i][2] - cLData[i][v][2] * lockCount
                    mc.move(moveX, moveY, moveZ, vLData[i][v], absolute=1, ws=1)
            viewPortCount = lockCount
        else:
            viewPortCount = 0.1
    mc.refresh(f=True)

def O65():
    selEdge = mc.filterExpand(expand=True, sm=32)
    if selEdge:
        if mc.objExists('saveSel'):
            mc.delete('saveSel')
        mc.sets(name='saveSel', text='saveSel')
        sortGrp = O8l()
        for e in sortGrp:
            O66(e)
        mc.select(selEdge)
        mc.ConvertSelectionToVertices()
        mc.polyMergeVertex(d=0.001, am=0, ch=1)
        mc.select('saveSel')
        mc.delete('saveSel')

def O66(edgelist):
    listVtx = O76(edgelist)
    checkA = O80(listVtx[1], listVtx[0], listVtx[-1])
    angleA = math.degrees(checkA)
    checkB = O80(listVtx[-2], listVtx[-1], listVtx[0])
    angleB = math.degrees(checkB)
    angleC = 180 - angleA - angleB
    distanceC = O79(listVtx[0], listVtx[-1])
    distanceA = distanceC / math.sin(math.radians(angleC)) * math.sin(math.radians(angleA))
    distanceB = distanceC / math.sin(math.radians(angleC)) * math.sin(math.radians(angleB))
    oldDistA = O79(listVtx[-2], listVtx[-1])
    oldDistB = O79(listVtx[0], listVtx[1])
    scalarB = distanceB / oldDistB
    pA = mc.pointPosition(listVtx[0], w=1)
    pB = mc.pointPosition(listVtx[1], w=1)
    newP = [0, 0, 0]
    newP[0] = (pB[0] - pA[0]) * scalarB + pA[0]
    newP[1] = (pB[1] - pA[1]) * scalarB + pA[1]
    newP[2] = (pB[2] - pA[2]) * scalarB + pA[2]
    listVtx = listVtx[1:-1]
    storeDist = []
    for l in listVtx:
        sotreXYZ = [0, 0, 0]
        p = mc.xform(l, q=True, t=True, ws=True)
        sotreXYZ[0] = (newP[0] - p[0]) / 100
        sotreXYZ[1] = (newP[1] - p[1]) / 100
        sotreXYZ[2] = (newP[2] - p[2]) / 100
        storeDist.append(sotreXYZ)
    return (newP, listVtx, storeDist)
def O67():
    goEven = mc.checkBox('evenRoundEdgeLength', q=1, v=1)
    edgeLoopSel = mc.ls(sl=1,fl=1)
    sortGrp = O8l()
    for e in sortGrp:
        check = []
        check.append(e[0])
        check.append(e[-1])
        e2v = mc.ls(mc.polyListComponentConversion(check,tv=1),fl=1)
        if len(e2v) != 3:
            O68(e)
            if goEven == 1:
                O3l(e)
                O68(e)
    meshName = edgeLoopSel[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(edgeLoopSel)
def O68(flatList):
    cleanList = ('newCircleGuid*','tempGuid*','arcCurv*','upperLo*','aimLo*','tempCircleGuide*','baseLo*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
    edgeSel = flatList
    listVtx = O76(edgeSel)
    pointA = listVtx[0]
    pointB = listVtx[-1]
    xA, yA, zA = mc.pointPosition(pointA, w=1)
    xB, yB, zB = mc.pointPosition(pointB , w=1)
    avgX = 0
    avgY = 0
    avgZ = 0
    for i in range(1, len(listVtx)-1):
        xP, yP, zP = mc.pointPosition(listVtx[i], w=1)
        avgX = avgX + xP
        avgY = avgY + yP
        avgZ = avgZ + zP
    xMid = avgX / (len(listVtx)-2)
    yMid = avgY / (len(listVtx)-2)
    zMid = avgZ / (len(listVtx)-2)
    distanceBetween = math.sqrt((xA - xB) * (xA - xB) + (yA - yB) * (yA - yB) + (zA - zB) * (zA - zB))
    circleR = distanceBetween / math.sqrt( 2 )
    mc.circle( nr=(0, 0 ,circleR), c=(0, 0, 0),r= circleR,n='tempCircleGuideA')
    mc.spaceLocator(n='upperLoc')
    mc.spaceLocator(n='aimLoc')
    mc.spaceLocator(n='baseLoc')
    mc.select('upperLoc','aimLoc','baseLoc')
    mc.CenterPivot()
    mc.setAttr(('upperLoc.scale'),0.01,0.01,0.01)
    mc.setAttr(('aimLoc.scale'),0.01,0.01,0.01)
    mc.setAttr(('aimLoc.translate'),0, 1,-1)
    mc.setAttr(('upperLoc.translate'),0, 1,1)
    consNode = mc.aimConstraint('aimLoc','baseLoc',offset=[0,0,0], weight=1, aimVector=[1,0,0], upVector=[0,1,0], worldUpType='object', worldUpObject='upperLoc')
    mc.setAttr(('baseLoc.translate'),xA, yA, zA)
    mc.setAttr(('aimLoc.translate'),xB, yB, zB )
    mc.setAttr(('upperLoc.translate'),xMid,yMid,zMid)
    mc.select('tempCircleGuideA','baseLoc')
    mc.matchTransform()
    mc.duplicate('tempCircleGuideA',smartTransform=1,n='newCircleGuide')
    mc.setAttr(('newCircleGuide.translate'),xB, yB, zB)
    intersectC = mc.curveIntersect('tempCircleGuideA','newCircleGuide')
    sPosX, sPosY,sPosZ = mc.pointOnCurve('tempCircleGuideA' , pr = float(intersectC[0]), p=1)
    cPosX, cPosY,cPosZ = mc.pointOnCurve('tempCircleGuideA' , pr = float(intersectC[2]), p=1)
    distA = math.sqrt((xMid - sPosX) * (xMid - sPosX) + (yMid - sPosY) * (yMid - sPosY) + (zMid - sPosZ) * (zMid - sPosZ))
    distB = math.sqrt((xMid - cPosX) * (xMid - cPosX) + (yMid - cPosY) * (yMid - cPosY) + (zMid - cPosZ) * (zMid - cPosZ))
    newCenter = []
    if distA > distB:
        newCenter = [sPosX, sPosY,sPosZ ]
    else:
        newCenter = [cPosX, cPosY,cPosZ ]
    mc.setAttr(('newCircleGuide.translate'),newCenter[0], newCenter[1], newCenter[2])
    mc.makeIdentity('newCircleGuide', apply=1, t=1,r=1,s=1)
    selectionList = om.MSelectionList()
    selectionList.add('newCircleGuide')
    dagPath = om.MDagPath()
    selectionList.getDagPath(0, dagPath)
    omCurveOut = om.MFnNurbsCurve(dagPath)
    for m in range(1,len(listVtx)) :
        xK, yK, zK = mc.pointPosition(listVtx[m], w=1)
        pointInSpace = om.MPoint(xK,yK,zK)
        closestPoint = om.MPoint()
        closestPoint = omCurveOut.closestPoint(pointInSpace)
        mc.move(closestPoint[0], closestPoint[1], closestPoint[2], listVtx[m] , a =True, ws=True)
    cleanList = ('newCircleGuid*','tempGuid*','arcCurv*','upperLo*','aimLo*','tempCircleGuide*','baseLo*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
def O69():
    goEven = mc.checkBox('evenRoundEdgeLength', q=1, v=1)
    edgeLoopSel = mc.ls(sl=1,fl=1)
    sortGrp = O8l()
    for e in sortGrp:
        check = []
        check.append(e[0])
        check.append(e[-1])
        e2v = mc.ls(mc.polyListComponentConversion(check,tv=1),fl=1)
        if len(e2v) != 3:
            O70(e)
            if goEven == 1:
                O3l(e)
                O70(e)
    meshName = edgeLoopSel[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(edgeLoopSel)
def O70(flatList):
    cleanList = ('newCircleGuid*','tempGuid*','arcCurv*','upperLo*','aimLo*','tempCircleGuide*','baseLo*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
    listVtx = O76(flatList)
    pointA = listVtx[0]
    pointB = listVtx[-1]
    xA, yA, zA = mc.pointPosition(pointA, w=1)
    xB, yB, zB = mc.pointPosition(pointB , w=1)
    avgX = 0
    avgY = 0
    avgZ = 0
    for i in range(1, len(listVtx)-1):
        xP, yP, zP = mc.pointPosition(listVtx[i], w=1)
        avgX = avgX + xP
        avgY = avgY + yP
        avgZ = avgZ + zP
    xMid = avgX / (len(listVtx)-2)
    yMid = avgY / (len(listVtx)-2)
    zMid = avgZ / (len(listVtx)-2)
    distanceBetween = math.sqrt((xA - xB) * (xA - xB) + (yA - yB) * (yA - yB) + (zA - zB) * (zA - zB))
    circleR = distanceBetween / 2
    mc.circle( nr=(0, 0 ,circleR), c=(0, 0, 0),r= circleR,n='newCircleGuide')
    mc.spaceLocator(n='upperLoc')
    mc.spaceLocator(n='aimLoc')
    mc.spaceLocator(n='baseLoc')
    mc.select('upperLoc','aimLoc','baseLoc')
    mc.CenterPivot()
    mc.setAttr(('upperLoc.scale'),0.01,0.01,0.01)
    mc.setAttr(('aimLoc.scale'),0.01,0.01,0.01)
    mc.setAttr(('aimLoc.translate'),0, 1,-1)
    mc.setAttr(('upperLoc.translate'),0, 1,1)
    consNode = mc.aimConstraint('aimLoc','baseLoc',offset=[0,0,0], weight=1, aimVector=[1,0,0], upVector=[0,1,0], worldUpType='object', worldUpObject='upperLoc')
    mc.setAttr(('baseLoc.translate'),xA, yA, zA)
    mc.setAttr(('aimLoc.translate'),xB, yB, zB )
    mc.setAttr(('upperLoc.translate'),xMid,yMid,zMid)
    mc.select('newCircleGuide','baseLoc')
    mc.matchTransform()
    xC = (xA - xB)/2 + xB
    yC = (yA - yB)/2 + yB
    zC = (zA - zB)/2 + zB
    mc.setAttr(('newCircleGuide.translate'),xC, yC, zC)
    mc.makeIdentity('newCircleGuide', apply=1, t=1,r=1,s=1)
    selectionList = om.MSelectionList()
    selectionList.add('newCircleGuide')
    dagPath = om.MDagPath()
    selectionList.getDagPath(0, dagPath)
    omCurveOut = om.MFnNurbsCurve(dagPath)
    for m in range(1,len(listVtx)) :
        xK, yK, zK = mc.pointPosition(listVtx[m], w=1)
        pointInSpace = om.MPoint(xK,yK,zK)
        closestPoint = om.MPoint()
        closestPoint = omCurveOut.closestPoint(pointInSpace)
        mc.move(closestPoint[0], closestPoint[1], closestPoint[2], listVtx[m] , a =True, ws=True)
    cleanList = ('newCircleGuid*','tempGuid*','arcCurv*','upperLo*','aimLo*','tempCircleGuide*','baseLo*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
def O71():
    checkEven = mc.checkBox('evenRoundEdgeLength', q=1,v=1)
    pivotSnapSwitch = mc.checkBox('evenRoundPivotSnap', q=1,v=1)
    getFaceList = mc.filterExpand(ex=1, sm=34)
    if getFaceList:
        mc.ConvertSelectionToEdgePerimeter()
    edgeLoopSel = mc.ls(sl=1,fl=1)
    mc.polyCircularizeEdge(constructionHistory=0, alignment=0, radialOffset=0, normalOffset=0, normalOrientation=0, smoothingAngle=30, evenlyDistribute = checkEven, divisions=0, supportingEdges=0, twist=0, relaxInterior=1)
    sortGrp = O8l()
    meshName = edgeLoopSel[0].split('.')[0]
    mc.delete(meshName,ch =1)
    if pivotSnapSwitch == 1:
        if len(sortGrp) > 1:
            O72()
def O72():
    pivotSnapTypeCheck = mc.radioButtonGrp('PivotSnapType', q=1,sl=1)
    cleanList = ('baseCircleCurv*','tempCenterCurve*','xxxx','tempCircleCenterLin*','upperLo*','aimLo*','baseLo*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
    baseLoopNumber = 0
    edgeLoopSel = mc.ls(sl=1,fl=1)
    sortGrp = O8l()
    curveList = []
    targetLoop = ''
    vCheck = 10000000
    if pivotSnapTypeCheck == 2:
        vCheck = 0
    for e in sortGrp:
        bbox =mc.xform(e, q=1, ws=1, bb=1)
        xSide = (bbox[3]-bbox[0])*(bbox[4]-bbox[1])
        ySide = (bbox[5]-bbox[2])*(bbox[3]-bbox[0])
        zSide = (bbox[4]-bbox[1])*(bbox[5]-bbox[2])
        if xSide == 0:
            xSide = 1
        if ySide == 0:
            ySide = 1
        if zSide == 0:
            zSide = 1
        bboxV =  math.sqrt(xSide*ySide*zSide)
        if pivotSnapTypeCheck == 1:
            if bboxV < vCheck:
                vCheck = bboxV
                targetLoop = e
        else:
            if bboxV > vCheck:
                vCheck = bboxV
                targetLoop = e
    mc.select(targetLoop)
    cirvleNode = mc.polyToCurve(ch=0,form=2, degree=1, conformToSmoothMeshPreview=1,n='baseCircleCurve')
    mc.CenterPivot()
    mc.select(targetLoop)
    mc.ConvertSelectionToVertices()
    edgeSel = mc.ls(sl=1,fl=1)
    baseLoopNumber = len(edgeSel)
    pointA = edgeSel[0]
    pointB = edgeSel[-1]
    pointC = edgeSel[int(len(edgeSel)/2)]
    xA, yA, zA = mc.pointPosition(pointA, w=1)
    xB, yB, zB = mc.pointPosition(pointB , w=1)
    xC, yC, zC = mc.pointPosition(pointC , w=1)
    mc.spaceLocator(n='upperLoc')
    mc.spaceLocator(n='aimLoc')
    mc.spaceLocator(n='baseLoc')
    mc.select('upperLoc','aimLoc','baseLoc')
    mc.CenterPivot()
    mc.setAttr(('upperLoc.scale'),0.01,0.01,0.01)
    mc.setAttr(('aimLoc.scale'),0.01,0.01,0.01)
    mc.setAttr(('aimLoc.translate'),0, 1,-1)
    mc.setAttr(('upperLoc.translate'),0, 1,1)
    consNode = mc.aimConstraint('aimLoc','baseLoc',offset=[0,0,0], weight=1, aimVector=[1,0,0], upVector=[0,1,0], worldUpType='object', worldUpObject='upperLoc')
    mc.setAttr(('baseLoc.translate'),xA, yA, zA)
    mc.setAttr(('aimLoc.translate'),xB, yB, zB )
    mc.setAttr(('upperLoc.translate'),xC, yC, zC)
    mc.curve(d=1, p=[(0,0,0),(0,0,-10)], k=[0,1],name = 'tempCircleCenterLine')
    mc.CenterPivot()
    mc.select('tempCircleCenterLine','baseLoc')
    mc.matchTransform(rot=1)
    mc.select('tempCircleCenterLine','baseCircleCurve')
    mc.matchTransform(pos=1)
    mc.makeIdentity('tempCircleCenterLine', apply=1, t=1,r=1,s=1)
    selectionList = om.MSelectionList()
    selectionList.add('tempCircleCenterLine')
    dagPath = om.MDagPath()
    selectionList.getDagPath(0, dagPath)
    omCurveOut = om.MFnNurbsCurve(dagPath)
    matchList =  list(set(edgeLoopSel)-set(targetLoop))
    mc.select(matchList)
    sortGrp = O8l()
    mc.spaceLocator(n='xxxx')
    meshName = edgeLoopSel[0].split('.')[0]
    for e in sortGrp:
        mc.select(e)
        cirvleNode = mc.polyToCurve(ch=0,form=2, degree=1, conformToSmoothMeshPreview=1,name='tempCenterCurve01')
        mc.CenterPivot()
        mc.select('baseCircleCurve',cirvleNode[0])
        mc.matchTransform()
        mc.makeIdentity('baseCircleCurve', apply=1, t=1,r=1,s=1)
        baseLength = mc.arclen( 'baseCircleCurve' )
        targetLength = mc.arclen( cirvleNode[0] )
        scaleV = targetLength / baseLength
        mc.setAttr(('baseCircleCurve.scale'),scaleV,scaleV,scaleV)
        compareCVList = mc.ls(('baseCircleCurve.cv[*]'),fl=1)
        bboxPiv =mc.xform('baseCircleCurve', q=1, ws=1, piv=1)
        pointInSpace = om.MPoint(bboxPiv[0],bboxPiv[1],bboxPiv[2])
        closestPoint = om.MPoint()
        closestPoint = omCurveOut.closestPoint(pointInSpace)
        mc.move(closestPoint[0], closestPoint[1], closestPoint[2], 'xxxx', a =True, ws=True)
        mc.select('baseCircleCurve','xxxx')
        mc.matchTransform(pos=1)
        mc.select(e)
        mc.ConvertSelectionToVertices()
        listVtx = mc.ls(sl=1,fl=1)
        mc.setToolTo('moveSuperContext')
        centerP = mc.manipMoveContext("Move", q=1,p=1)
        nodeCluster = mc.cluster(n= 'centerGrp')
        pointInSpace = om.MPoint(centerP[0],centerP[1],centerP[2])
        closestPoint = om.MPoint()
        closestPoint = omCurveOut.closestPoint(pointInSpace)
        mc.move(closestPoint[0], closestPoint[1], closestPoint[2], nodeCluster[1], rpr=1)
        mc.delete(meshName,ch =1)
        if baseLoopNumber == len(listVtx):
            for m in listVtx :
                xK, yK, zK = mc.pointPosition(m, w=1)
                checkDist = 100000
                getCV = []
                toRemove = ''
                for c in compareCVList:
                    xN, yN, zN = mc.pointPosition(c, w=1)
                    dist = math.sqrt((xK - xN) * (xK - xN) + (yK - yN) * (yK - yN) + (zK - zN) * (zK - zN))
                    if dist < checkDist:
                        checkDist = dist
                        getCV = [xN,yN,zN]
                        toRemove = c
                mc.move( getCV[0], getCV[1], getCV[2], m , a =True, ws=True)
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(edgeLoopSel)
    cleanList = ('baseCircleCurv*','tempCenterCurve*','xxxx','tempCircleCenterLin*','upperLo*','aimLo*','baseLo*')
    for c in cleanList:
        if mc.objExists(c):
            mc.delete(c)
def O73():
    goEven = mc.checkBox('evenCurveEdgeLength', q=1, v=1)
    edgeLoopSel = mc.ls(sl=1,fl=1)
    sortGrp = O8l()
    for e in sortGrp:
        O74(e)
        if goEven == 1:
            O3l(e)
    meshName = edgeLoopSel[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(edgeLoopSel)
def O74(flatList):
    if mc.objExists('tempCenterLin*'):
        mc.delete('tempCenterLin*')
    edgeSel = flatList
    listVtx = O76(edgeSel)
    xA, yA, zA = mc.pointPosition(listVtx[0], w=1)
    xB, yB, zB = mc.pointPosition(listVtx[-1], w=1)
    mc.curve(d=1, p=[(xA, yA, zA),(xB, yB, zB)], k=[0,1],name = 'tempCenterLine')
    selectionList = om.MSelectionList()
    selectionList.add('tempCenterLine')
    dagPath = om.MDagPath()
    selectionList.getDagPath(0, dagPath)
    omCurveOut = om.MFnNurbsCurve(dagPath)
    for m in listVtx :
        xK, yK, zK = mc.pointPosition(m, w=1)
        pointInSpace = om.MPoint(xK,yK,zK)
        closestPoint = om.MPoint()
        closestPoint = omCurveOut.closestPoint(pointInSpace)
        mc.move( closestPoint[0], closestPoint[1], closestPoint[2],m, a =True, ws=True)
    if mc.objExists('tempCenterLin*'):
        mc.delete('tempCenterLin*')
def O75():
    edgeLoopSel = mc.ls(sl=1,fl=1)
    sortGrp = O8l()
    for e in sortGrp:
        check = []
        check.append(e[0])
        check.append(e[-1])
        e2v = mc.ls(mc.polyListComponentConversion(check,tv=1),fl=1)
        if len(e2v) != 3:
            O3l(e)
    meshName = edgeLoopSel[0].split('.')[0]
    cmd = 'doMenuNURBComponentSelection("' + meshName + '", "edge");'
    mel.eval(cmd)
    mc.select(edgeLoopSel)
def O76(edgelist):
    if edgelist:
        selEdges = edgelist
        shapeNode = mc.listRelatives(selEdges[0], fullPath=True , parent=True )
        transformNode = mc.listRelatives(shapeNode[0], fullPath=True , parent=True )
        edgeNumberList = []
        for a in selEdges:
            checkNumber = ((a.split('.')[1]).split('\n')[0]).split(' ')
            for c in checkNumber:
                findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
                if findNumber:
                    edgeNumberList.append(findNumber)
        getNumber = []
        for s in selEdges:
            evlist = mc.polyInfo(s,ev=True)
            checkNumber = ((evlist[0].split(':')[1]).split('\n')[0]).split(' ')
            for c in checkNumber:
                findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
                if findNumber:
                    getNumber.append(findNumber)
        dup = set([x for x in getNumber if getNumber.count(x) > 1])
        getHeadTail = list(set(getNumber) - dup)
        vftOrder = []
        finalList = []
        if len(getHeadTail)>0:
            vftOrder.append(getHeadTail[0])
            count = 0
            while len(dup)> 0 and count < 100:
                checkVtx = transformNode[0]+'.vtx['+ vftOrder[-1] + ']'
                velist = mc.polyInfo(checkVtx,ve=True)
                getNumber = []
                checkNumber = ((velist[0].split(':')[1]).split('\n')[0]).split(' ')
                for c in checkNumber:
                    findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
                    if findNumber:
                        getNumber.append(findNumber)
                findNextEdge = []
                for g in getNumber:
                    if g in edgeNumberList:
                        findNextEdge = g
                edgeNumberList.remove(findNextEdge)
                checkVtx = transformNode[0]+'.e['+ findNextEdge + ']'
                findVtx = mc.polyInfo(checkVtx,ev=True)
                getNumber = []
                checkNumber = ((findVtx[0].split(':')[1]).split('\n')[0]).split(' ')
                for c in checkNumber:
                    findNumber = ''.join([n for n in c.split('|')[-1] if n.isdigit()])
                    if findNumber:
                        getNumber.append(findNumber)
                gotNextVtx = []
                for g in getNumber:
                    if g in dup:
                        gotNextVtx = g
                if len(gotNextVtx)> 0:
                    dup.remove(gotNextVtx)
                    vftOrder.append(gotNextVtx)
                    count +=  1
            if len(getHeadTail)>1:
                vftOrder.append(getHeadTail[1])
                for v in vftOrder:
                    finalList.append(transformNode[0]+'.vtx['+ v + ']' )
        return finalList
def O77(selEdges):
    if selEdges:
        trans = selEdges[0].split(".")[0]
        e2vInfos = mc.polyInfo(selEdges, ev=True)
        e2vDict = {}
        fEdges = []
        for info in e2vInfos:
            evList = [ int(i) for i in re.findall('\\d+', info) ]
            e2vDict.update(dict([(evList[0], evList[1:])]))
        while True:
            try:
                startEdge, startVtxs = e2vDict.popitem()
            except:
                break
            edgesGrp = [startEdge]
            num = 0
            for vtx in startVtxs:
                curVtx = vtx
                while True:

                    nextEdges = []
                    for k in e2vDict:
                        if curVtx in e2vDict[k]:
                            nextEdges.append(k)
                    if nextEdges:
                        if len(nextEdges) == 1:
                            if num == 0:
                                edgesGrp.append(nextEdges[0])
                            else:
                                edgesGrp.insert(0, nextEdges[0])
                            nextVtxs = e2vDict[nextEdges[0]]
                            curVtx = [ vtx for vtx in nextVtxs if vtx != curVtx ][0]
                            e2vDict.pop(nextEdges[0])
                        else:
                            break
                    else:
                        break
                num += 1
            fEdges.append(edgesGrp)
        retEdges =[]
        for f in fEdges:
            collectList=[]
            for x in f:
                getCom= (trans +".e["+ str(x) +"]")
                collectList.append(getCom)
            retEdges.append(collectList)
        return retEdges

def O78():
    selEdges = mc.ls(sl=1, fl=1)
    shapeNode = mc.listRelatives(selEdges[0], fullPath=True, parent=True)
    transformNode = mc.listRelatives(shapeNode[0], fullPath=True, parent=True)
    edgeNumberList = []
    for a in selEdges:
        checkNumber = a.split('.')[1].split('\n')[0].split(' ')
        for c in checkNumber:
            findNumber = ''.join([ n for n in c.split('|')[-1] if n.isdigit() ])
            if findNumber:
                edgeNumberList.append(findNumber)
    getNumber = []
    for s in selEdges:
        evlist = mc.polyInfo(s, ev=True)
        checkNumber = evlist[0].split(':')[1].split('\n')[0].split(' ')
        for c in checkNumber:
            findNumber = ''.join([ n for n in c.split('|')[-1] if n.isdigit() ])
            if findNumber:
                getNumber.append(findNumber)
    dup = set([ x for x in getNumber if getNumber.count(x) > 1 ])
    getHeadTail = list(set(getNumber) - dup)
    checkCircleState = 0
    if not getHeadTail:
        checkCircleState = 1
        getHeadTail.append(getNumber[0])
    vftOrder = []
    vftOrder.append(getHeadTail[0])
    count = 0
    while len(dup) > 0 and count < 1000:
        checkVtx = transformNode[0] + '.vtx[' + vftOrder[-1] + ']'
        velist = mc.polyInfo(checkVtx, ve=True)
        getNumber = []
        checkNumber = velist[0].split(':')[1].split('\n')[0].split(' ')
        for c in checkNumber:
            findNumber = ''.join([ n for n in c.split('|')[-1] if n.isdigit() ])
            if findNumber:
                getNumber.append(findNumber)
        findNextEdge = []
        for g in getNumber:
            if g in edgeNumberList:
                findNextEdge = g
        edgeNumberList.remove(findNextEdge)
        checkVtx = transformNode[0] + '.e[' + findNextEdge + ']'
        findVtx = mc.polyInfo(checkVtx, ev=True)
        getNumber = []
        checkNumber = findVtx[0].split(':')[1].split('\n')[0].split(' ')
        for c in checkNumber:
            findNumber = ''.join([ n for n in c.split('|')[-1] if n.isdigit() ])
            if findNumber:
                getNumber.append(findNumber)
        gotNextVtx = []
        for g in getNumber:
            if g in dup:
                gotNextVtx = g
        dup.remove(gotNextVtx)
        vftOrder.append(gotNextVtx)
        count += 1
    if checkCircleState == 0:
        vftOrder.append(getHeadTail[1])
    elif vftOrder[0] == vftOrder[1]:
        vftOrder = vftOrder[1:]
    elif vftOrder[0] == vftOrder[-1]:
        vftOrder = vftOrder[0:-1]
    finalList = []
    for v in vftOrder:
        finalList.append(transformNode[0] + '.vtx[' + v + ']')
    return (checkCircleState, finalList)

def O79(p1, p2):
    pA = mc.pointPosition(p1, w=1)
    pB = mc.pointPosition(p2, w=1)
    dist = math.sqrt((pA[0] - pB[0]) ** 2 + (pA[1] - pB[1]) ** 2 + (pA[2] - pB[2]) ** 2)
    return dist
def O80(pA, pB, pC):
    a = mc.pointPosition(pA, w=1)
    b = mc.pointPosition(pB, w=1)
    c = mc.pointPosition(pC, w=1)
    ba = [ aa - bb for aa, bb in zip(a, b) ]
    bc = [ cc - bb for cc, bb in zip(c, b) ]
    nba = math.sqrt(sum((x ** 2.0 for x in ba)))
    ba = [ x / nba for x in ba ]
    nbc = math.sqrt(sum((x ** 2.0 for x in bc)))
    bc = [ x / nbc for x in bc ]
    scalar = sum((aa * bb for aa, bb in zip(ba, bc)))
    angle = math.acos(scalar)
    return angle
def O8l():
    selEdges = mc.ls(sl=1, fl=1)
    trans = selEdges[0].split('.')[0]
    e2vInfos = mc.polyInfo(selEdges, ev=True)
    e2vDict = {}
    fEdges = []
    for info in e2vInfos:
        evList = [ int(i) for i in re.findall('\\d+', info) ]
        e2vDict.update(dict([(evList[0], evList[1:])]))
    while True:
        try:
            startEdge, startVtxs = e2vDict.popitem()
        except:
            break
        edgesGrp = [startEdge]
        num = 0
        for vtx in startVtxs:
            curVtx = vtx
            while True:
                nextEdges = []
                for k in e2vDict:
                    if curVtx in e2vDict[k]:
                        nextEdges.append(k)

                if nextEdges:
                    if len(nextEdges) == 1:
                        if num == 0:
                            edgesGrp.append(nextEdges[0])
                        else:
                            edgesGrp.insert(0, nextEdges[0])
                        nextVtxs = e2vDict[nextEdges[0]]
                        curVtx = [ vtx for vtx in nextVtxs if vtx != curVtx ][0]
                        e2vDict.pop(nextEdges[0])
                    else:
                        break
                else:
                    break
            num += 1
        fEdges.append(edgesGrp)
    retEdges = []
    for f in fEdges:
        collectList = []
        for x in f:
            getCom = trans + '.e[' + str(x) + ']'
            collectList.append(getCom)
        retEdges.append(collectList)
    return retEdges

def O82(angle):
    currentSelp = mc.ls(sl=True, fl=True)
    mc.polySelectConstraint(m=2, w=1, pp=4, a=angle, t=0x8000)
    wholeLoop = mc.ls(sl=True, fl=True)
    mc.polySelectConstraint(m=2, w=2, t=0x8000)
    removeInnerEdges = mc.ls(sl=True, fl=True)
    if len(wholeLoop) != len(removeInnerEdges):
        mc.select(wholeLoop)
        mc.select(removeInnerEdges, d=True)
    mc.polySelectConstraint(m=0, w=0)
    mc.polySelectConstraint(disable=True)

def O83():
    mc.ConvertSelectionToEdges()
    mc.polySelectConstraint(m=2, t=0x8000, w=1)
    mc.polySelectConstraint(disable=True)

def O84():
    mc.polySlideEdgeCtx("polySlideEdgeContext", e=True, useSnapping=False)
    mc.setToolTo("polySlideEdgeContext")


def O85(PM):
    selEdge = mc.ls(sl=True, fl=True)
    mc.polySelectConstraint(disable=True)
    if PM == "minus":
        if len(selEdge) > 1:
            mc.polySelectConstraint(pp=6, t=0x8000)
            mc.polySelectConstraint(m=0, w=0) 
            mc.polySelectConstraint(disable=True) 
    else:
        mc.polySelectConstraint(m=2, w=2, t=0x8000)
        selInner = mc.ls(sl=True, fl=True)
        mc.select(selEdge, r=True)
        mc.polySelectConstraint(m=2, w=1, t=0x8000)
        selBorder = mc.ls(sl=True, fl=True)
        mc.select(selEdge, r=True)
        if len(selInner) > len(selBorder):
            mc.polySelectConstraint(pp=5, t=0x8000)
            mc.polySelectConstraint(m=0, w=0)
            mc.polySelectConstraint(disable=True)
        else:
            mc.polySelectConstraint(pp=1, m=2, w=1, t=0x8000)
            mc.polySelectConstraint(m=0, w=0)
            mc.polySelectConstraint(disable=True)


def O86():
    firstSel = mc.ls(sl=True, fl=True)
    cmd = 'polySelectEdgesEveryN "edgeRing" 1';
    mel.eval(cmd)
    growAll = mc.ls(sl=True, fl=True)
    newFace = mc.polyListComponentConversion(firstSel, fe=True, tf=True)
    newEdges = mc.ls(mc.polyListComponentConversion(newFace, ff=True, te=True),fl=1)
    commonItems = list(set(newEdges) & set(growAll))
    mc.select(commonItems)

def O87():
    firstSel = mc.ls(sl=True, fl=True)
    newVert = mc.polyListComponentConversion(firstSel, fe=True, tv=True)
    mc.select(newVert)
    mc.ConvertSelectionToContainedFaces(newVert)
    mc.ConvertSelectionToEdgePerimeter()
    newBorder = mc.ls(sl=True, fl=True)
    diffItems = list(set(firstSel) - set(newBorder))
    mc.select(diffItems)


def O88():
    edges = cmds.ls(fl=True, sl=True)
    getPoints = mc.ls( mc.polyListComponentConversion(edges, tv=True),fl=True)
    edgeLoopExt = mc.ls( mc.polySelectSp(edges, q=1, loop=1),fl=True)
    for p in getPoints:
        surEedge = mc.ls( mc.polyListComponentConversion(p, te=True),fl=True)
        nextTwoEdge = list(set(surEedge) - set(edgeLoopExt))
        surPoints = mc.ls( mc.polyListComponentConversion(nextTwoEdge, tv=True),fl=True)
        surPoints.remove(p) 
        if len(surPoints) == 2:
            ptA = mc.xform(surPoints[0], q=True, t=True, ws=True)
            ptB = mc.xform(surPoints[1], q=True, t=True, ws=True)
            midP = mc.xform(p, q=True, t=True, ws=True)
            distA = math.sqrt( ((ptA[0] - midP[0])**2)  + ((ptA[1] - midP[1])**2) + ((ptA[2] - midP[2])**2))
            distB = math.sqrt( ((ptB[0] - midP[0])**2)  + ((ptB[1] - midP[1])**2) + ((ptB[2] - midP[2])**2))
            scaleBaseP = ''
            scaleDistP = 0
            if distA > distB:
                scaleBaseP = ptA
                scaleDistP = distA
            else:
                 scaleBaseP = ptB
                 scaleDistP = distB
            avgDist = ( distA + distB )/2
            magV =  avgDist /scaleDistP
            if magV < 1: 
                vectBtwPnts= ((scaleBaseP[0] -midP[0])*-1), ((scaleBaseP[1] -midP[1])*-1), ((scaleBaseP[2] -midP[2])*-1)
                vectorToFinish = om.MFloatVector(vectBtwPnts[0],vectBtwPnts[1],vectBtwPnts[2])
                raySource = om.MFloatPoint(scaleBaseP[0],scaleBaseP[1],scaleBaseP[2])
                rayDirection = vectorToFinish
                magnitude = vectorToFinish.length()
                new_magnitude = magnitude * magV
                direction_normalized = vectorToFinish.normal()
                scaled_direction = direction_normalized * new_magnitude
                new_endpoint = raySource + scaled_direction
                mc.move(new_endpoint.x, new_endpoint.y, new_endpoint.z, p , absolute=True)
                            
def EdgeSensei():
    if mc.window("EdgeSenseiWindow", exists=True):
        mc.deleteUI("EdgeSenseiWindow", window=True)
    if mc.dockControl("EdgeSenseiDock", exists=True):
        mc.deleteUI("EdgeSenseiDock", control=True)
    edge_window = mc.window("EdgeSenseiWindow", title="EdgeSensei v1.04", widthHeight=(320, 900),s = 1 ,mxb = False, mnb = False)
    mc.columnLayout(adj=True)
    mc.frameLayout(label="Quick Tools", bv=0, w=298, cll=1, cl=0 ,bgc = (0.2,0.2,0.2))
    mc.text(l="",h=2)
    mc.rowColumnLayout(nc=9, cw=[(1, 50), (2, 20), (3, 50), (4, 10), (5, 50), (6, 10), (7, 50), (8, 10), (9, 65)])
    mc.text(l=" Quick")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Insert",rpt=1, bgc=(0.18, 0.18, 0.18), c="mc.SplitEdgeRingTool()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Slide",rpt=1, bgc=(0.18, 0.18, 0.18), c="O84()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Border",rpt=1, bgc=(0.18, 0.18, 0.18), c="O83()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Contiguous",rpt=1, bgc=(0.18, 0.18, 0.18), c="O82(30)")
    mc.setParent("..")
    mc.separator(height=5, style="in")
    mc.rowColumnLayout(nc=13, cw=[(1, 50), (2, 20), (3, 40), (4, 5), (5, 20), (6, 5), (7, 20), (8, 20), (9, 50), (10, 5), (11, 20), (12, 5), (13, 20)])
    mc.text(l=" Select")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Loop",rpt=1, bgc=(0.18, 0.18, 0.18), c="mc.SelectEdgeLoopSp()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="+", rpt=1, bgc=(0.08, 0.18, 0.38), c='O85("plus")')
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="-", rpt=1, bgc=(0.08, 0.38, 0.28), c='O85("minus")')
    mc.text(l=" |")
    mc.iconTextButton(style="textOnly", label="Ring",rpt=1, bgc=(0.18, 0.18, 0.18), c="mc.SelectEdgeRingSp()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="+", rpt=1, bgc=(0.08, 0.18, 0.38), c='O86()')
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="-", rpt=1, bgc=(0.08, 0.38, 0.28), c='O87()')
    mc.setParent("..")
    mc.rowColumnLayout(nc=7, cw=[(1, 50), (2, 20), (3, 50), (4, 20), (5, 50), (6, 20), (7, 50)])
    mc.setParent("..")
    mc.separator(height=5, style="in")
    mc.rowColumnLayout(nc=7, cw=[(1, 50), (2, 20), (3, 50), (4, 20), (5, 50), (6, 20), (7, 50)])
    mc.text(l="Average")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Smooth", rpt=1, bgc=(0.18, 0.18, 0.18), c="O32()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Even", rpt=1, bgc=(0.18, 0.18, 0.18), c="O75()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Spread",rpt=1, bgc=(0.18, 0.18, 0.18), c="O88()")
    mc.text(l="",h=2)
    mc.setParent("..")
    mc.setParent("..")
    mc.frameLayout(label="Arc", bv=0, w=298, cll=1, cl=0 ,bgc = (0.2,0.2,0.2))
    mc.text(l="",h=2)
    mc.rowColumnLayout(nc=9, cw=[(1, 50), (2, 20), (3, 50), (4, 5), (5, 50), (6, 5), (7, 50), (8, 5), (9, 50)])
    mc.text(l="      3D")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="1", rpt=1, bgc=(0.18, 0.18, 0.18), c="O39(1)")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="2", rpt=1, bgc=(0.18, 0.18, 0.18), c="O39(2)")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="3", rpt=1, bgc=(0.18, 0.18, 0.18), c="O39(3)")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="--", rpt=1, bgc=(0.18, 0.18, 0.18), c="O39(0)")
    mc.setParent("..")
    mc.rowColumnLayout(nc=9, cw=[(1, 50), (2, 20), (3, 50), (4, 5), (5, 50), (6, 5), (7, 50), (8, 5), (9, 50)])
    mc.text(l="      2D")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="1", rpt=1, bgc=(0.22, 0.22, 0.18), c="O36(1)")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="2", rpt=1, bgc=(0.22, 0.22, 0.18), c="O36(2)")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="3", rpt=1, bgc=(0.22, 0.22, 0.18), c="O36(3)")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="--", rpt=1, bgc=(0.22, 0.22, 0.18), c="O36(0)")
    mc.text(l="", h=5)
    mc.setParent("..")
    mc.rowColumnLayout(nc=9, cw=[(1, 50), (2, 20), (3, 50), (4, 5), (5, 50), (6, 5), (7, 50), (8, 5), (9, 50)])
    mc.text(l="      Edit")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Inflate", rpt=1, bgc=(0.18, 0.18, 0.18), c="O50()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Tension", rpt=1, bgc=(0.18, 0.18, 0.18), c="O55()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="UnBevel", rpt=1, bgc=(0.18, 0.18, 0.18), c="O6o()")
    mc.text(l="")
    mc.checkBox("evenCurveEdgeLength", label="Even", value=0)
    mc.text(l="",h=2)
    mc.setParent("..")
    mc.setParent("..")
    mc.frameLayout(label="Constant", bv=0, w=298, cll=1, cl=0 ,bgc = (0.2,0.2,0.2))
    mc.text(l="",h=2)
    mc.rowColumnLayout(nc=7, cw=[(1, 50), (2, 20), (3, 50), (4, 7), (5, 50), (6, 17), (7, 90)])
    mc.text(l="  Extend")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="L", rpt=1,bgc=(0.08, 0.18, 0.38), c="O41('L',100)")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="R", rpt=1,bgc=(0.08, 0.38, 0.28), c="O41('R',100)")
    mc.text(l="")
    mc.checkBox("lockCurveEdgeLength", label="Keep Length", value=0)
    mc.setParent("..")
    mc.rowColumnLayout(nc=7, cw=[(1, 50), (2, 20), (3, 50), (4, 7), (5, 50), (6, 20), (7, 50)])
    mc.text(l="     Curl")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="L", rpt=1,bgc=(0.08, 0.18, 0.38), c="O41('L',4)")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="R", rpt=1,bgc=(0.08, 0.38, 0.28), c="O41('R',4)")
    mc.setParent("..")
    mc.text(l="",h=2)
    mc.setParent("..")
    mc.setParent("..")
    mc.frameLayout(label="Round", bv=0, w=298, cll=1, cl=0 ,bgc = (0.2,0.2,0.2))
    mc.text(l="",h=2)
    mc.rowColumnLayout(nc=9, cw=[(1, 50), (2, 20), (3, 50), (4, 5), (5, 50), (6, 5), (7, 50), (8, 5), (9, 50)])
    mc.text(l="")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="90", bgc=(0.18, 0.18, 0.18), c="O67()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="180", bgc=(0.18, 0.18, 0.18), c="O69()")
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="360", bgc=(0.18, 0.18, 0.18), c="O71()")
    mc.text(l="")
    mc.checkBox("evenRoundEdgeLength", label="Even", value=1)
    mc.setParent("..")
    mc.rowColumnLayout(nc=4, cw=[(1, 50), (2, 20), (3,110), (4,130)])
    mc.text(l="")
    mc.text(l="")
    mc.checkBox("evenRoundPivotSnap", label="Pivot Snap Type", value=0, cc='O6()')
    mc.radioButtonGrp("PivotSnapType", en=0, nrb=2, sl=1, la2=("Small", "Big"), cw=[(1,50), (2, 60)] )
    mc.setParent("..")
    mc.setParent("..")
    mc.frameLayout(label="Insert", bv=0, w=298, cll=1, cl=0 ,bgc = (0.2,0.2,0.2))
    mc.text(l="",h=2)
    mc.floatSliderGrp("multiInsertNo", v=2, pre=0, min=2, max=50, fmn=2, fmx=100, cw3=[50, 35, 0], label="Number  ", field=True)
    mc.rowColumnLayout(nc=5, cw=[(1, 50),(2, 20), (3, 30),(4, 9), (5, 150)])
    mc.text(l="Repeat")
    mc.text(l="")
    mc.checkBox("keepSpliteNumber", l="", v=0)
    mc.text(l="")
    mc.iconTextButton(style="textOnly", label="Split", rpt=1, bgc=(0.18, 0.18, 0.18), c="O23()")
    mc.text(l="",h=2)
    mc.setParent("..")
    mc.setParent("..")
    mc.frameLayout(label="Edge Lock", bv=0, w=298, cll=1, cl=0 ,bgc = (0.2,0.2,0.2))
    mc.text(l="",h=2)
    mc.rowColumnLayout(nc=3, cw=[(1, 50), (2, 50), (3, 175)])
    mc.text(l="   Type")
    mc.text(l="", h=3)
    mc.radioButtonGrp("lockEdgeType", nrb=2, sl=1, la2=["Absolute", "Relative"], cw=[(1, 90), (2, 70)])
    mc.setParent("..")
    mc.floatSliderGrp("lockEdgeSlider", v=0.95, min=0.001, max=0.999, s=0.01, cw3=[50, 40, 0], label="Ratio   ", field=True, dc="O19()")
    mc.rowColumnLayout(nc=7, cw=[(1, 45), (2, 7), (3, 40), (4, 7),(5, 95), (6, 5),(7, 95)])
    mc.text(l="Length")
    mc.text(l="", h=3)
    mc.floatField("lastLockEdgelength",  v = 0.02, pre=3)
    mc.text(l="", h=3)
    mc.iconTextButton(style="textOnly",label="Ratio", rpt=1, bgc=(0.18, 0.18, 0.18),c="O10()")
    mc.text(l="", h=3)
    mc.iconTextButton(style="textOnly",label="Length", rpt=1,bgc=(0.18, 0.18, 0.18),c="O9()")
    mc.text(l="",h=2)
    mc.setParent("..")
    mc.setParent("..")
    mc.setParent("..")
    mc.frameLayout(label="Ring Equalizer", bv=0, w=298, cll=1, cl=0 ,bgc = (0.2,0.2,0.2))
    mc.text(l="",h=2)
    mc.rowColumnLayout(nc=11, cw=[(1, 45), (2, 7), (3, 40), (4, 7),(5, 40), (6, 30),(7, 35), (8, 3),(9, 35), (10, 3),(11, 35)])
    mc.text(l="Length")
    mc.text(l="",h=2)
    mc.floatField("equalizerLength", v=1 ,pre =3 )
    mc.text(l="",h=2)
    mc.iconTextButton(style="textOnly", label="check", bgc=(0.18, 0.18, 0.18), c="O8()")
    mc.text(l="  |  ",h=2)
    mc.iconTextButton(style="textOnly", label="A", bgc=(0.08, 0.18, 0.38), c="O7('A')")
    mc.text(l="",h=2)
    mc.iconTextButton(style="textOnly", label="Mid", bgc=(0.18, 0.18, 0.18), c="O7('M')")
    mc.text(l="",h=2)
    mc.iconTextButton(style="textOnly", label="B", bgc=(0.08, 0.38, 0.28), c="O7('B')")
    mc.setParent("..")
    mc.frameLayout(label="Arc Deformer", bv=0, w=298, cll=1, cl=0 ,bgc = (0.2,0.2,0.2))
    mc.rowColumnLayout(nc=3 ,cw=[(1,50),(2,50),(3,175)])
    mc.text(l ='Type')
    mc.text(l ='')
    mc.radioButtonGrp('curveType', nrb=2, sl=1, labelArray2=['Bezier', 'Nurbs'], cw = [(1,90),(2,70)],cc='O5()')
    mc.setParent( '..' )
    mc.rowColumnLayout(nc=10 ,cw=[(1,1),(2,50),(3,10),(4,50),(5,5),(6,50),(7,5),(8,50),(9,5),(10,95)])
    mc.text(l ='')
    mc.text(l ='Options')
    mc.text(l ='')
    mc.checkBox('makeArc', label= "Arc" ,v = 1, cc ='O3()')
    mc.text(l ='')
    mc.checkBox('snapCurve', label= "Snap" ,v = 1, cc = 'O4()')
    mc.text(l ='')
    mc.checkBox('evenSpace', label= "Even" ,v = 1)
    mc.text(l ='')
    mc.checkBox('cleanCurve', label= "Keep Curve" ,v = 1)
    mc.setParent( '..' )
    mc.intSliderGrp('CPSlider', cw3=[50, 30, 180], label = 'Point ',  field= 1, min= 2, max= 10, fmx = 500, v = 3 )
    mc.floatSliderGrp('dropOffSlider' , label = 'DropOff', v = 0.01, cw3=[50, 30, 180], field=1 ,pre = 2, min= 0.01, max= 10)
    mc.rowColumnLayout(nc=4 ,cw=[(1,99),(2,95),(3,5),(4,95)])
    mc.text(l ='')
    mc.iconTextButton(style="textOnly", l= 'Create',bgc=(0.18, 0.18, 0.18),  c= 'O2()')
    mc.text(l ='')
    mc.iconTextButton(style="textOnly", l= 'Done', bgc=(0.18, 0.18, 0.18), c= 'O1()')
    mc.text(l ='')
    mc.setParent( '..' )
    mc.text(l="",h=2)
    mc.showWindow(edge_window)
    mc.window("EdgeSenseiWindow", e=1, widthHeight=(320, 900))
    #allowedAreas = ['right', 'left']
    #mc.dockControl("EdgeSenseiDock", area="left", content = edge_window, width=360, allowedArea = allowedAreas,fl=1, label="EdgeSensei v1.0")


