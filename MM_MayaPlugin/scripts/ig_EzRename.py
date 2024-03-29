#--------------------------------------------------------------------------------#
# QIONGTWO汉化 <脚本基于Python3，支持Maya2020以上版本>
# 先看看作者的版权信息，然后有使用说明。
#
#             ig_EzRename.py 
#             version 1.3, last modified 04/10/2022
#             版权所有Copyright (C) 2022 Igor Silva
#             Email: igorsilva.design@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# 本程序是免费软件：您可以重新分发它和/或修改
# 基于 GNU 通用公共许可证的条款发布，
# FSF自由软件基金会许可证的第 3 版或任何更高版本（根据您的选择）。
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# 分发该程序是希望它能提供帮助，
# 但对于适销性、特定用途的适用性不做任何保证;包括任何默示的保证
# 请参阅的GNU 通用公共许可证了解更多详情。
# 

# See http://www.gnu.org/licenses/gpl.html for a copy of the GNU General 
# Public License.
# GNU通用公共许可证网址：http://www.gnu.org/licenses/gpl.html
# 
# version 1.3
# Upgrade to Python3
 

#--------------------------------------------------------------------------------#

# 使用说明：
# 拷贝全部代码粘贴至maya脚本编辑器的python框中。
# 保存脚本为ig_EzRename.py到 MyDocuments\Maya\scripts\ 目录下。
# 在maya脚本编辑器的python框中输入以下内容：
'''

from importlib import reload
import ig_EzRename
reload(ig_EzRename)
ig_EzRename.UI()

'''
# 然后把这段代码中键拖到工具架，点击运行即可。
#
# 
# 以下为原本的指引内容。
#                    I N S T A L L A T I O N:
# Copy the "ig_EzRename.py" to your Maya scripts directory:
#     MyDocuments\Maya\scripts\
#         use this text as a python script within Maya:
'''
from importlib import reload
import ig_EzRename
reload(ig_EzRename)
ig_EzRename.UI()
'''
# this text can be entered from the script editor and can be made into a button
#

import maya.cmds as cmds

def UI():
	
	global SelectName
	global RenameText

	global StartValue
	global PaddingValue
	global NumberCheck

	global RemoveFirst
	global RemoveEnd

	global PrefixText
	global SuffixText

	global SearchText
	global ReplaceText
	global SRCheck
	
	#UI Width
	sizeX = 260
	version = "v1.0"
	if cmds.window("igEzRenameWin", exists=True):
		cmds.deleteUI("igEzRenameWin", window=True)
	
	#Creating UI
	igEzRenamWin = cmds.window("igEzRenameWin", title="ig重命名工具 "+version, width=sizeX+6, height=385, mnb = True, mxb = False, sizeable = False)
	
	#Creating interface elements
	mainLayout = cmds.columnLayout("mainColumnLayout", width = sizeX, adjustableColumn=False, co = ["both",2])

	#Select All Button
	cmds.separator(w = sizeX, h=15, style = "in", parent = mainLayout)
	cmds.separator(h=5, style = "none", parent = mainLayout)
	cmds.button(label = "选择全部", w=sizeX, h=25, c=SelectAll, ann = "选中场景中全部目标")
	cmds.separator(h=5, style = "none", parent = mainLayout)

	#Select by Name
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 25), (2, 60)], cs = [(5,5), (5,5)])
	cmds.button(label = "按名称选择", w=sizeX/3, h=25, c=SelectName, align = "Center", ann="搜索名称并选中")
	SelectName = cmds.textField(w = sizeX*0.646, ann="按名称选择 \n 可以用 * 加上前缀或后缀，选择相同前后缀的目标 \n 比如: *_high")
	cmds.separator(w = sizeX, h=15, style = "in", parent = mainLayout)
	
	#Rename and Number
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)])
	#Rename Field
	cmds.text(label="  批重命名: ", font = "boldLabelFont", w = sizeX/4, align="left", ann="给所选目标重命名")
	RenameText = cmds.textField(w = sizeX*0.75, ann="给所选目标重命名")
	
	#Start Field
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)])
	cmds.text(label="  起始编号:", font = "boldLabelFont", w = sizeX/4, align="left")
	StartValue = cmds.textField(w = sizeX/4, tx="1", ann="序列起始编号")
	#Padding Field
	cmds.text(label="  编号位数:", font = "boldLabelFont", w = sizeX/4, align="left")
	PaddingValue = cmds.textField(w = sizeX/4, tx="3", ann="编号有几位数，比如2是01；3是001")
	#Number Letters
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)])
	cmds.text(label="", font = "boldLabelFont", w = sizeX/4-2, align="left")
	NumberCheck = cmds.radioButtonGrp(labelArray2=[ '按数字编号', '按字母编号'], numberOfRadioButtons=2, w=sizeX, h=20, sl=1, cw = ([1,100]))
	#ButtonRename and Number
	cmds.separator(h=5, style = "none", parent = mainLayout)
	cmds.button(label = "重命名并编号", ann="MAYA大纲内容不能重名，必须选择一种编号方式", w=sizeX, h=25, c=RenameNumber, align = "Center", parent = mainLayout)
	cmds.separator(w = sizeX, h=15, style = "in", parent = mainLayout)

	#RemoveCharacter
	#Remove First/Last
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 25), (2, 60)], cs = [(5,5)])
	cmds.text(label="  删除所选的:", font = "boldLabelFont", w = sizeX/3-12, align="left")
	cmds.button(label = "开头字母->", w=sizeX/3, h=25, c="ig_EzRename.Remove(True)", align = "Center")
	cmds.button(label = "<-结尾字母", w=sizeX/3, h=25, c="ig_EzRename.Remove(False)", align = "Center")
	cmds.separator(h=5, style = "none", parent = mainLayout)
	cmds.separator(w = sizeX, h=15, style = "in", parent = mainLayout)

	#Remove pasted__
	#cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 25), (2, 60)], cs = [(90,90)])
	#cmds.text(label="  ", font = "boldLabelFont", w = sizeX/3-12, align="left")
	#cmds.button(label = "粘贴内容__", w=sizeX/3, h=25, c=RemovePasted, align = "Center")

	#Remove UI
	#cmds.separator(h=5, style = "none", parent = mainLayout)
	#cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 25), (2, 60)], cs = [(8.5,8.5)])
	#RemoveFirst = cmds.textField(w = sizeX/5, tx="0", ann="输入想要删除的字母数量")
	#cmds.button(label = "-", w=25, h=25, c="ig_EzRename.RemoveChar('begin')", align = "Center", ann="删除几个开头字母")
	#cmds.button(label = "删除", w=sizeX/4, h=25, c="ig_EzRename.RemoveChar('all')", align = "Center", ann="删除开头和结尾的字母")
	#cmds.button(label = "-", w=25, h=25, c="ig_EzRename.RemoveChar('end')", align = "Center", ann="删除几个结尾字母")
	#RemoveEnd = cmds.textField(w = sizeX/5, tx="3", ann="Write the amount of characters you want to delete on text ending")
	#cmds.separator(w = sizeX, h=15, style = "in", parent = mainLayout)
	
	#Suffix
	#Control Suffix
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)], cs = [(5,5)])
	cmds.text(label="  添加前缀:", font = "boldLabelFont", w = sizeX/4-5, align="left")
	PrefixText = cmds.textField(w = sizeX/2.5+33, tx="SM_", ann="输入前缀")
	cmds.button(label = "添加", w=sizeX/4-10, h=25, c="ig_EzRename.PrefixSuffix(False)", align = "Center")
	cmds.separator(h=5, style = "none", parent = mainLayout)

	#Group Suffix
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)], cs = [(5,5)])
	cmds.text(label="  添加后缀:", font = "boldLabelFont", w = sizeX/4-5, align="left")
	SuffixText = cmds.textField(w = sizeX/2.5+33, tx="_001", ann="输入后缀")
	cmds.button(label = "添加", w=sizeX/4-10, h=25, c="ig_EzRename.PrefixSuffix(True)", align = "Center")
	cmds.separator(w = sizeX, h=15, style = "in", parent = mainLayout)

	#Prefix
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)], cs = [(5,5)])
	cmds.text(label="  后缀预设:", font = "boldLabelFont", w = sizeX/3-15, align="left", ann="后缀预设")
	cmds.button(label = "_high", w=sizeX/3, h=25, c="ig_EzRename.Suffix('_high')", align = "Center", ann = "高模后缀") 
	cmds.button(label = "_low", w=sizeX/3, h=25, c="ig_EzRename.Suffix('_low')", align = "Center", ann = "低模后缀")
	#cmds.button(label = "_Ctrl", w=sizeX/5-4, h=25, c="ig_EzRename.Suffix('_Ctrl')", align = "Center", ann = "Add Ctrl suffix")
	#cmds.button(label = "_Jnt", w=sizeX/5-4, h=25, c="ig_EzRename.Suffix('_Jnt')", align = "Center", ann = "Add Jnt suffix")
	#cmds.button(label = "_Drv", w=sizeX/5-4, h=25, c="ig_EzRename.Suffix('_Drv')", align = "Center", ann = "Add Drv suffix")
	cmds.separator(w = sizeX, h=15, style = "in", parent = mainLayout)
	
	#Search and Replace
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)], cs = [(5,5)])
	cmds.text(label="  搜索:", font = "boldLabelFont", w = sizeX/4-10, align="left", ann="搜索需要替换的文字")
	SearchText = cmds.textField(w = sizeX/2+100, ann="Write the text to search")
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)], cs = [(5,5)])
	cmds.text(label="  替换:", font = "boldLabelFont", w = sizeX/4-10, align="left", ann="替换所搜文字")
	ReplaceText = cmds.textField(w = sizeX/2+100, ann="Write the text to replace")
	cmds.rowColumnLayout( numberOfRows=1, w=sizeX, parent=mainLayout, rowHeight=[(1, 20), (2, 60)], cs = [(5,5)])
	SRCheck = cmds.radioButtonGrp(labelArray3=[ '已选的目标', '已选的组内', '全部'], numberOfRadioButtons=3, w=sizeX, h=20, sl=1, cw = ([1,95],[2,95],[3,95]))
	cmds.separator(h=10, style = "none", parent = mainLayout)
	cmds.button(label = "确认替换", w=sizeX, h=25, c=SearchReplace, align = "Center", parent = mainLayout)
	cmds.separator(h=5, style = "none", parent = mainLayout)
	cmds.separator(w = sizeX, h=15, style = "in", parent = mainLayout)
	
	#Show UI:
	cmds.showWindow(igEzRenamWin)

def SelectAll(*args):
	cmds.select(ado=True, hi = True)
	selection = cmds.ls(selection=True, sn=True)
	selectionAdd = []

	#Old select all code version
	"""for objs in selection:
		children = cmds.listRelatives(objs, c=True, f =True)
		print "Children01:", children
		shapes = cmds.listRelatives(objs, s=True, f = True)
		print "Shapes:", shapes
		
		if not children == None:
			if not shapes == None:
				for s in shapes:
					children.remove(s)
			
			for chi in children:
				
				children2 = cmds.listRelatives(chi, c=True, f = True)
				print "CHildren02:", children2

				if not children2 == None:
					for chi2 in children2:
						children.append(chi2)
				
				selectionAdd.append(chi)

		

	for objs in selectionAdd:
		cmds.select(objs, add=True)"""

def SelectName(*args):
	cmds.select(cl=True)
	name = cmds.textField(SelectName, text = 1, q=True)
	try:
		selection = cmds.ls(name, l = True)
	except:
		cmds.warning("Object Don't Exist")

	for objs in selection:
		cmds.select(objs, add=True)

def RenameNumber(*args):
	#获取起始编号
	number = cmds.textField(StartValue, text = 1, q=True)
	number = int(number)
	#编号的填充位数
	padding = cmds.textField(PaddingValue, text = 1, q=True)
	padding = int(padding)

	NumberLetters = cmds.radioButtonGrp(NumberCheck, q=True, select=True)
	
	newName = cmds.textField(RenameText, text = 1, q=True)

	selection = cmds.ls(selection=True, sn=True)
	
	lettersList = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

	#Number suffix
	y = 0
	
	for obj in selection: 
		try:
			#Teste if has duplicate mesh with the same name on the scene and return the name without parents
			trueName = testDuplicateName(obj)
			#Save the original name
			oldName = trueName

			#检查用户是否选择了使用数字进行编号
			if NumberLetters == 1:
				zeros = ""
				for x in range(int(padding)):
					if len(str(number)) <= x:
						zeros = zeros+"0"
				
				#Create the newName and rename
				name = newName+"_"+"{:0>"+str(padding)+"}"
				newNameList = name.format(number)
				cmds.rename(obj, name.format(number))

			else:
				newNameList = newName+"_"+lettersList[y]
				cmds.rename(obj, newName+"_"+lettersList[y])
				if y < len(lettersList)-1:
					y+=1
				else:
					y=0

			#For to rename all the oldNames on list to newNames
			for x in range(len(selection)):
				newParentName = selection[x].replace(oldName, newNameList)
				selection[x] = newParentName
		except:
			pass
		
		number = int(number+1)
		

def RemoveChar(Type):
	
	first = cmds.textField(RemoveFirst, text = 1, q=True)
	end = cmds.textField(RemoveEnd, text = 1, q=True)

	selection = cmds.ls(selection = True, sn=True)

	for objs in selection:
		#Teste if has duplicate mesh with the same name on the scene
		trueName = testDuplicateName(objs)

		#Save the original name
		oldName = trueName

		if Type == "all":
			name = trueName[:-int(end)]
			name = name[int(first):]

		if Type == "begin":
			name = trueName[int(first):]

		if Type == "end":
			name = trueName[:-int(end)]
		
		try:
			cmds.rename(objs, str(name))
		except:
			pass

		#For to rename all the oldNames on list to newNames
		for x in range(len(selection)):
			newParentName = selection[x].replace(oldName, name)
			selection[x] = newParentName
	

def Remove(Type):
	
	selection = cmds.ls(selection = True, sn = True)

	for objs in selection:
		#Teste if has duplicate mesh with the same name on the scene
		trueName = testDuplicateName(objs)

		#Save the original name
		oldName = trueName

		if Type:
			name = trueName[1:]
		else:
			name = trueName[:-1]

		try:
			cmds.rename(objs, name)
		except:
			pass

		#For to rename all the oldNames on list to newNames
		for x in range(len(selection)):
			newParentName = selection[x].replace(oldName, name)
			selection[x] = newParentName



def RemovePasted(*args):
	
	selection = cmds.ls("pasted__*", sn = True)
	
	for objs in selection:
		#Teste if has duplicate mesh with the same name on the scene
		trueName = testDuplicateName(objs)

		name = trueName[8:]
		try:
			cmds.rename(objs, name)
		except:
			cmds.warning("Don't Exist pasted Objects")

def PrefixSuffix(Suffix):
	prefix = cmds.textField(PrefixText, text = 1, q=True)
	suffix = cmds.textField(SuffixText, text = 1, q=True)

	selection = cmds.ls(selection = True, sn = True)

	for objs in selection:

		#Teste if has duplicate mesh with the same name on the scene
		trueName = testDuplicateName(objs)
		#Save the original name
		oldName = trueName
		
		if Suffix:
			name = str(trueName)+suffix
		else:
			name = prefix+str(trueName)

		try:
			cmds.rename(objs, name)
		except:
			pass
		
		#For to rename all the oldNames on list to newNames
		for x in range(len(selection)):
			newParentName = selection[x].replace(oldName, name)
			selection[x] = newParentName
		

def Suffix(Text):
	
	selection = cmds.ls(selection = True, sn = True)
	
	for objs in selection:
		#Test if has duplicate mesh with the same name on the scene
		trueName = testDuplicateName(objs)

		#Save the original name
		oldName = trueName

		newName = trueName+Text
		try:
			cmds.rename(objs, newName)
		except:
			pass

		#For to rename all the oldNames on list to newNames
		for x in range(len(selection)):
			newParentName = selection[x].replace(oldName, newName)
			selection[x] = newParentName

def SearchReplace(*args):
	
	search = cmds.textField(SearchText, text = 1, q=True)
	replace = cmds.textField(ReplaceText, text = 1, q=True)

	SRMethod = cmds.radioButtonGrp(SRCheck, q=True, select=True)
	
	#Selected search and Replace method
	if SRMethod == 1:
		selection = cmds.ls(selection = True, sn = True)

	#Hierarchy search and Replace method
	if SRMethod == 2:
		cmds.select(hi = True)
		selection = cmds.ls(selection = True, sn = False)
		
	#All search and Replace method
	if SRMethod == 3:
		#Select All DagObjects in scene
		selection = []
		cmds.select(ado = True, hi = True)
		selection = cmds.ls(selection = True, sn=False)

	#for to rename the objects 
	for obj in selection:
		#Teste if has duplicate mesh with the same name on the scene and return the name without parents
		trueName = testDuplicateName(obj)
		#Save the original name
		oldName = trueName
		#Search and replace to create the new name
		newName = trueName.replace(search, replace)
		
		#Rename the object
		try:
			cmds.rename(obj, newName)
		except:
			pass
	
		#For to rename all the oldNames on list to newNames
		for x in range(len(selection)):
			newParentName = selection[x].replace(oldName, newName)
			selection[x] = newParentName

		print("Slecao: ", selection)

		
	
def testDuplicateName(Obj):

	try:
		trueName =  Obj.split("|")
		return trueName[len(trueName)-1]
	except:
		return Obj