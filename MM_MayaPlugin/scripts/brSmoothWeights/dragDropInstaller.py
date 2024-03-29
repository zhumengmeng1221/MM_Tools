# ----------------------------------------------------------------------
# Installation script to install a module-based script or plug-in for
# Autodesk Maya.
# ----------------------------------------------------------------------

import maya.cmds as cmds
from maya.api import OpenMaya as om2

from datetime import datetime
import errno
import logging
import os
import shutil
import subprocess

logger = logging.getLogger(__name__)

INSTALL_ROOT = os.path.dirname(os.path.realpath(__file__))
MODULES_DIR = "modules"
MODULE_NAME = os.path.basename(INSTALL_ROOT)

HELP_FILE = os.path.join(INSTALL_ROOT, "installationGuide.html")
LOG_FILE = os.path.join(INSTALL_ROOT, "install.log")
LOGO_FILE = os.path.join(os.path.join(INSTALL_ROOT, "resources"), "{}.png".format(MODULE_NAME))

EULA_WIN = "EULAWin"
INSTALL_WIN = "installerWin"
INFO_TEXT = "installerInfoText"
MODULE_PATH_FIELD = "installerModulePathField"
CONTENT_PATH_FIELD = "installerContentPathField"
PROGRESS_LIST = "installProgressList"
INSTALL_BUTTON = "installInstallButton"
UNINSTALL_BUTTON = "installUninstallButton"
HELP_BUTTON = "installHelpButton"
MODULE_BUTTON = "installCreateModulesButton"

PREV_MOD_PATHS = "previousModulePaths"
PREV_CONTENT_PATHS = "previousContentPaths"
MOD_PATHS_VAR = "".join((MODULE_NAME, PREV_MOD_PATHS))
CONTENT_PATHS_VAR = "".join((MODULE_NAME, PREV_CONTENT_PATHS))


# ----------------------------------------------------------------------
# utilities
# ----------------------------------------------------------------------

def currentTimeLong():#当前时间的格式化字符串
    """Return the current time as a nice formatted string.

    :return: The current date and time.
    :rtype: str
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def getMayaVersions():#包含在模块中的插件子文件夹内的Maya版本列表
    """Return the list of Maya versions which are included in the
    module within the plug-ins sub folder.

    :return: The ordered list of available Maya versions.
    :rtype: list(str)
    """
    path = getPluginsPath(MODULE_NAME)
    path = os.path.join(path, getPlatform())
    return sorted(os.listdir(path))


def getModuleNames():#安装的模块的名称列表
    """Return the names of the modules to be installed.

    :return: The ordered list of module names.
    :rtype: list(str)
    """
    modulesFolder = os.path.join(INSTALL_ROOT, MODULES_DIR)
    files = os.listdir(modulesFolder)
    modules = []
    for f in files:
        if os.path.isdir(os.path.join(modulesFolder, f)):
            modules.append(f)
    return sorted(modules)


def getPlatform():#当前平台的标识字符串
    """Return the string identifying the current platform.

    :return: The platform string.
    :rtype: str
    """
    platform = cmds.about(os=True)
    if platform == 'mac':
        platform = 'macOS'
    return platform


def getPlugins():#安装中包含的所有插件的列表
    """Return a list with all plug-ins contained in the installation.

    :return: A list with all platform specific plug-ins.
    :rtype: list(str)
    """
    plugins = []
    version = getMayaVersions()[-1]
    for searchModule in getModuleNames():
        if hasPlugins(searchModule):
            path = os.path.join(getPluginsPath(searchModule), getPlatform())
            path = os.path.join(path, version)
            plugins.extend(os.listdir(path))
    return list(set(plugins))


def getPluginsPath(name):#返回给定模块的插件文件夹的路径
    """Return the path to the plug-ins folder of the given module to
    install.

    :param name: The name of the module.
    :type name: str

    :return: The path to the modules plug-ins folder
    :rtype: str
    """
    items = [INSTALL_ROOT, MODULES_DIR, name, "plug-ins"]
    path = ""
    for item in items:
        path = os.path.join(path, item)
    return path


def getUserPrefsPath():#当前用户首选项的路径
    """Return the path of the current user preferences.

    :return: The path of the user preferences,
    :rtype: str
    """
    prefsPath = cmds.internalVar(userPrefDir=True)
    # The preferences path is returned with an ending slash. Therefore
    # it's necessary to walk up three levels.
    return os.path.abspath(os.path.join(prefsPath, "../.."))


def hasPlugins(name):#模块包含插件，则返回True
    """Return True, if the module contains plug-ins.

    :param name: The name of the module.
    :type name: str

    :return: True, if the module contains a plug-in folder.
    :rtype: bool
    """
    return os.path.isdir(getPluginsPath(name))


def helpExists():#帮助文件存在，则返回True
    """Return True, if the help file is present.

    :return: True, if the help file exists.
    :rtype: bool
    """
    return os.path.exists(HELP_FILE)


def installExists():#检查安装的源文件是否存在于与安装脚本相同的文件夹中
    """Performs a check if the source files for the installation exist
    in the same folder as the installer script.

    :return: True, if the source file path exists.
    :rtype: bool
    """
    if not os.path.isdir(os.path.join(INSTALL_ROOT, MODULES_DIR)):
        message = "The source files for the installation cannot be found. " \
                  "Make sure that all files have been unzipped and that the " \
                  "modules folder is in the same folder as the drag and drop " \
                  "installer python file.\n\n"
        om2.MGlobal.displayError(message)
        return False
    return True


def logInfo(message=""):#将给定的消息写入日志文件中
    """Write the given message to the log file.

    :param message: The message to display.
    :type message: str
    """
    if not len(message):
        message = " "
    lines = message if isinstance(message, list) else [message]
    for i in range(len(lines)):
        lines[i] = "{} : {}".format(currentTimeLong(), lines[i])
    message = "\n".join(lines)

    try:
        with open(LOG_FILE, "a") as logObj:
            logObj.write("{}\n".format(message))
    except Exception as exception:
        om2.MGlobal.displayError("Unable to write log file {}".format(LOG_FILE))
        print(str(exception))


def unloadPlugins():#卸载即将安装的任何插件
    """Unload any plug-ins which are about to be installed.

    :return: True, if the plug-ins have been unloaded.
    :rtype: bool
    """
    loaded = False
    active = []
    for item in getPlugins():
        if cmds.pluginInfo(item, query=True, loaded=True):
            message = "Found loaded plug-in: {}".format(item)
            logInfo(message)
            addProgress(message)
            loaded = True
            active.append(item)

    if loaded:
        message = "One or more plug-ins which are about to be installed are currently loaded. " \
                  "To unload the plug-ins and continue with the installation the undo queue must be reset. " \
                  "Do you want to continue?"
        result = cmds.confirmDialog(title="Plug-ins loaded",
                                    message=message,
                                    button=("Continue", "Cancel"))
        if result == "Continue":
            cmds.flushUndo()
            for item in active:
                try:
                    cmds.unloadPlugin(item)
                    message = "Unloaded plug-in: {}".format(item)
                    logInfo(message)
                    addProgress(message)
                except Exception as exception:
                    message = "Unable to unload plug-in: {}".format(item)
                    logInfo(message)
                    addProgress(message)
                    return False
        else:
            return False

    return True


# ----------------------------------------------------------------------
# file operations
# ----------------------------------------------------------------------

def copyDir(source, destination):#将给定路径的文件夹复制到指定位置
    """Copy the folder at the given path to the given location.

    :param source: The full path of the folder to copy.
    :type source: str
    :param destination: The full path to copy the folder to.
    :type destination: str

    :return: True, if copying was successful.
    :rtype: bool
    """
    try:
        shutil.copytree(str(source), str(destination))
        logInfo("Copying: {} to: {}".format(source, destination))
    except shutil.Error as error:
        message = "Error copying: {} to: {}".format(source, destination)
        logInfo(message)
        logInfo(str(error))
        om2.MGlobal.displayError(message)
        return False
    return True


def removeDir(path):#删除给定路径的文件夹
    """Delete the folder at the given path.

    :param path: The full path of the folder to delete.
    :type path: str

    :return: True, if deleting was successful.
    :rtype: bool
    """
    try:
        shutil.rmtree(str(path))
        logInfo("Removed: {}".format(path))
    except shutil.Error as error:
        message = "Error deleting folder: {}".format(path)
        logInfo(message)
        logInfo(str(error))
        om2.MGlobal.displayError(message)
        return False
    return True


def removeFile(fileName):# 删除给定路径的文件
    """Delete the file at the given path.

    :param fileName: The full path of the file to delete.
    :type fileName: str

    :return: True, if deleting was successful.
    :rtype: bool
    """
    try:
        os.remove(fileName)
        logInfo("Deleting: {}".format(fileName))
    except OSError:
        message = "Error deleting file: {}".format(fileName)
        logInfo(message)
        om2.MGlobal.displayError(message)
        return False
    return True


def makeDirectory(path):#尝试创建指定路径的目录
    """Try to create the directory. If it already exists ignore the
    error but with any other error the result is set to false.

    Important: Only the directory is tested and created. Files are not
    supported.

    :param path: The directory to create and test.
    :type path: str

    :return: True, if the directory has been created or exists. False,
             if the path cannot be accessed.
    :rtype: bool
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            return False
    return True


# ----------------------------------------------------------------------
# file i/o
# ----------------------------------------------------------------------

def read(filePath):#读取给定文本文件的内容，并将其返回为列表形式
    """Return the content of the given text file as a list. Return an
    empty list if the file doesn't exist.

    :param filePath: The file path of the file to read.
    :type filePath: str

    :return: The file content as a list.
    :rtype: list(str)
    """
    content = []

    if os.path.exists(filePath):
        try:
            with open(filePath, "r") as fileObj:
                return list(line.rstrip() for line in fileObj)
        except OSError:
            pass
    return content


def write(filePath, data, mode):#将给定的数据写入到指定的文本文件中
    """Export the given data to the given text file.

    :param filePath: The file path of the file to write.
    :type filePath: str
    :param data: The data to write.
    :type data: str
    :param mode: The write mode.
    :type mode: str

    :return: True, if writing was successful.
    :rtype: bool
    """
    try:
        with open(filePath, mode) as fileObj:
            fileObj.write(data)
        return True
    except OSError:
        message = "Error writing: {}".format(filePath)
        logInfo(message)
    return False


# ----------------------------------------------------------------------
# checking previous installations
# ----------------------------------------------------------------------

def getExistingInstallationPaths():#它用于查找已知的模块安装路径并检索已存在的模块及其内容
    """Go through all known module paths and search for existing
    modules and their contents.
    Because older installations are located within their specific Maya
    version folder and newer installations are located on the top level
    of the Maya preferences all locations need to be checked.
    Also, because it's possible that files have been manually moved.

    Returns a tuple with:
        modules: Module files which match the modules to be installed.
        contents: Paths of the contents of the modules. These are the
                  paths which are stored in the module files.
        currentPaths: The paths which relate to the main module to be
                       installed. The first path in the list is used to
                       serve as a suggestion for the new installation.
        currentModules: The paths of the module files of the currently
                         installed main module.

    :return: A tuple with lists of paths of the currently found
             installations.
    :rtype: tuple(list(str), list(str), list(str), list(str))
    """
    # Get the list of modules paths of the current Maya session.
    modulePaths = os.environ["MAYA_MODULE_PATH"]
    # In case of Windows the path separator is different from macOS and
    # Linux.
    separator = ":"
    if getPlatform() == "win64":
        separator = ";"
    modules = []
    contents = []
    currentPaths = []
    currentModules = []
    # For every registered path, check if it exists because some paths
    # may be registered but don't exist by default.
    for modulePath in modulePaths.split(separator):
        if os.path.exists(modulePath):
            # Go through every .mod file in the current path and see if
            # it matches the ones to be installed.
            for modFile in os.listdir(modulePath):
                for searchModule in getModuleNames():
                    # In case the module is found get the contents of
                    # the module file and store the contained paths.
                    if modFile == ".".join((searchModule, "mod")):
                        filePath = os.path.join(modulePath, modFile)
                        contentPaths = getModuleContentPaths(filePath, searchModule)

                        modules.append(os.path.join(modulePath, modFile))
                        contents.extend(contentPaths)

                        # If the current module matches the main module
                        # store the paths separately to serve as a
                        # suggestion for the new installation.
                        if modFile == ".".join((MODULE_NAME, "mod")):
                            currentPaths.extend(contentPaths)
                            currentModules.append(filePath)

    # Remove any duplicate paths.
    modules = list(set(modules))
    contents = list(set(contents))

    return modules, contents, currentPaths, currentModules


def getModuleContentPaths(filePath, module):#获取模块文件中包含的路径
    """Return a list of paths which are contained in the given module
    file.

    :param filePath: The path of the module file to read.
    :type filePath: str
    :param module: The name of the module to find.
    :type module: str

    :return: The list of contained paths.
    :rtype: list(str)
    """
    content = read(filePath)
    paths = []
    for line in content:
        if " {} ".format(module) in line:
            filePath = line.split(" ")[-1]
            if os.path.exists(filePath):
                paths.append(filePath)
    return paths


# ----------------------------------------------------------------------
# installation
# ----------------------------------------------------------------------

def prepareInstallation(*args):#准备安装。它首先显示安装器窗口，然后确保所有插件都已卸载
    """Gather all information about previously installed modules and
    the location of the user preferences. Populate the path fields with
    these pre-defined paths.
    """
    # Build and show the installer window.
    showUI()

    # Make sure that all plug-ins are unloaded.
    if not unloadPlugins():
        message = "Error: Unable to perform the installation with loaded plug-ins."
        logInfo(message)
        addProgress(message)
        installationFailed()
        return

    # Get the path from installed modules.
    modules, contents, mainPaths, mainModules = getExistingInstallationPaths()

    contentPath = ""
    modulePath = ""
    if len(mainPaths):
        info = "Using the previous installation path to install the module{}.".format(multiSuffix())
        if len(mainPaths):
            contentPath = os.path.dirname(mainPaths[0])
        if len(mainModules):
            modulePath = os.path.dirname(mainModules[0])
    else:
        info = "Using the default user preferences path to install the module{}.".format(multiSuffix())
        contentPath = modulePath = os.path.join(getUserPrefsPath(), MODULES_DIR)

    cmds.text(INFO_TEXT,
              edit=True,
              label=info)
    cmds.textFieldGrp(CONTENT_PATH_FIELD,
                      edit=True,
                      text=contentPath)
    cmds.textFieldGrp(MODULE_PATH_FIELD,
                      edit=True,
                      text=modulePath)

    # Store the paths in optionVars to access these when the
    # installation is performed.
    if len(modules):
        cmds.optionVar(stringValue=(MOD_PATHS_VAR, ",".join(modules)))
        logInfo("Found existing modules:")
        for i in modules:
            logInfo("\t{}".format(i))

    if len(contents):
        cmds.optionVar(stringValue=(CONTENT_PATHS_VAR, ",".join(contents)))
        logInfo("Found existing module contents:")
        for i in contents:
            logInfo("\t{}".format(i))

    logInfo("Setting automatic paths:")
    logInfo(info)
    logInfo(contentPath)
    logInfo(modulePath)


def performUninstall(*args):#执行卸载
    """Remove any existing installation paths which have been found.
    """
    modules = []
    contents = []
    # Get the previously found paths for the modules and their contents.
    if cmds.optionVar(exists=MOD_PATHS_VAR):
        modules = cmds.optionVar(query=MOD_PATHS_VAR).split(",")
        cmds.optionVar(remove=MOD_PATHS_VAR)
    if cmds.optionVar(exists=CONTENT_PATHS_VAR):
        contents = cmds.optionVar(query=CONTENT_PATHS_VAR).split(",")
        cmds.optionVar(remove=CONTENT_PATHS_VAR)

    # Delete the existing modules.
    if len(modules):
        message = "Deleting previously installed modules."
        logInfo(message)
        addProgress(message)
        for item in modules:
            if not removeFile(item):
                installationFailed()
                addProgress("Error: Deleting: {}".format(item))
                return
            addProgress("Deleting: {}".format(item))
    elif len(args):
        message = "No previously installed modules found."
        logInfo(message)
        addProgress(message)

    # Delete the existing module contents.
    if len(contents):
        message = "Deleting previously installed module contents."
        logInfo(message)
        addProgress(message)
        for item in contents:
            if not removeDir(item):
                installationFailed()
                addProgress("Error: Deleting: {}".format(item))
                return
            addProgress("Deleting: {}".format(item))
    elif len(args):
        message = "No previously installed modules contents found."
        logInfo(message)
        addProgress(message)

    # If the method hasn't been called from the UI but from performing
    # the uninstallation return to finish it.
    if not len(args):
        return

    message = "Uninstall completed."
    logInfo(message)
    addProgress(message)


def performInstallation(*args):#执行安装
    """Perform the installation.
    """
    # Remove the previous installation.
    performUninstall()

    # Get the path where the module contents should be installed.
    contentPath = cmds.textFieldGrp(CONTENT_PATH_FIELD,
                                    query=True,
                                    text=True)

    # Copy the modules to the given location.
    message = "Installing files to: {}".format(contentPath)
    logInfo(message)
    addProgress(message)

    if not copyModuleContents(contentPath):
        installationFailed()
        return

    # Create the module files.
    performBuildModuleFiles()

    # Finish the installation.
    message = "Installation complete."
    logInfo(message)
    addProgress(message)

    finish()


def performBuildModuleFiles(*args):#执行构建模块文件操作
    """Write the module files to the defined folder.
    """
    # Get the path where the module contents are located.
    contentPath = cmds.textFieldGrp(CONTENT_PATH_FIELD,
                                    query=True,
                                    text=True)
    # Get the path where the module files should be saved.
    modulePath = cmds.textFieldGrp(MODULE_PATH_FIELD,
                                   query=True,
                                   text=True)

    message = "Creating module file{} in: {}".format(multiSuffix(), modulePath)
    logInfo(message)
    addProgress(message)

    if not writeModuleFiles(modulePath, contentPath):
        installationFailed()
        return

    # If the method hasn't been called from the UI but from performing
    # the installation return to finish it.
    if not len(args):
        return

    message = "Module file{} created.".format(multiSuffix())
    logInfo(message)
    addProgress(message)


def copyModuleContents(destination):#复制模块内容
    """Copy the module folders from the installation source to the
    given destination path.

    :param destination: The path where to copy the module folders to.
    :type destination: str

    :return: True, if copying was successful.
    :rtype: bool
    """
    for module in getModuleNames():
        source = os.path.join(os.path.join(INSTALL_ROOT, MODULES_DIR), module)
        contentPath = os.path.join(destination, module)

        # In case the destination module path exists but hasn't been
        # detected yet because the module file has been missing delete
        # the folder.
        if os.path.exists(contentPath):
            removeDir(contentPath)

        if not copyDir(source, contentPath):
            addProgress("Error: Installing {} to: {}".format(module, contentPath))
            return False
        addProgress("Installing {} to: {}".format(module, contentPath))

        # In case of Linux flatten the icons folder because currently
        # nested icon folders aren't respected with the recursive option
        # of the module file.
        # If an error occurs during flattening it doesn't interrupt the
        # installation. This is on purpose as changing the folder
        # structure might produce errors. This is currently being
        # monitored and subject to change once verified that it's
        # stable.
        if getPlatform() == "linux64":
            flattenFolder(os.path.join(contentPath, "icons"))
    return True


# ----------------------------------------------------------------------
# ui
# ----------------------------------------------------------------------

def showEULA():#显示用户许可协议窗口
    """Build and show the EULA window.
    """
    deleteExistingWindow(EULA_WIN)

    cmds.window(EULA_WIN,
                title="最终用户许可协议",
                sizeable=False)

    layout = cmds.rowColumnLayout()

    fileObj = open(os.path.join(INSTALL_ROOT, "LICENSE"), "rb")
    fileString = fileObj.read()
    fileObj.close()

    showLogo()

    cmds.scrollField(text=fileString,
                     font="plainLabelFont",
                     width=550,
                     height=300,
                     editable=False,
                     wordWrap=True)

    cmds.separator(style="none", height=10)
    cmds.rowLayout(numberOfColumns=2)
    cmds.button(label="同意",
                width=100,
                height=30,
                command=prepareInstallation)
    cmds.button(label="拒绝",
                width=100,
                height=30,
                command=dismissEULA)
    cmds.setParent(layout)
    cmds.showWindow(EULA_WIN)


def dismissEULA(*args):#当用户取消时关闭EULA窗口
    """Close the EULA window when cancelled.
    """
    logInfo("EULA被拒绝")
    logInfo("安装已取消")
    cmds.deleteUI(EULA_WIN)


def showUI():# 显示主安装程序窗口
    """Build and show the main installer window.
    """
    deleteExistingWindow(EULA_WIN)
    deleteExistingWindow(INSTALL_WIN)

    cmds.window(INSTALL_WIN,
                title="安装 {}".format(MODULE_NAME),
                width=550,
                sizeable=False,
                resizeToFitChildren=True)

    layout = cmds.rowColumnLayout()

    showLogo()

    # ------------------------------------------------------------------
    # paths
    # ------------------------------------------------------------------

    cmds.frameLayout(label="路径",
                     width=550,
                     collapsable=False,
                     collapse=False,
                     marginWidth=5,
                     marginHeight=5)
    cmds.columnLayout(columnAlign="left",
                      adjustableColumn=True)
    cmds.separator(style="none", height=5)
    cmds.text(INFO_TEXT,
              label="",
              align="center")
    cmds.separator(style="none", height=15)
    cmds.textFieldButtonGrp(CONTENT_PATH_FIELD,
                            label="安装路径",
                            buttonLabel="选择",
                            columnAttach3=("left", "both", "right"),
                            columnWidth3=(80, 405, 55),
                            columnOffset3=(5, 0, 5),
                            buttonCommand=selectContentPath)
    addFieldComment("The path where all files of the module{} will be installed.".format(multiSuffix()))
    cmds.separator(style="none", height=5)
    cmds.textFieldButtonGrp(MODULE_PATH_FIELD,
                            label="模块路径",
                            buttonLabel="选择",
                            columnAttach3=("left", "both", "right"),
                            columnWidth3=(80, 405, 55),
                            columnOffset3=(5, 0, 5),
                            buttonCommand=selectModulePath)
    addFieldComment("The path where the {}.mod file{} will be saved.".format(MODULE_NAME, multiSuffix()))
    cmds.setParent(layout)

    cmds.separator(style="none", height=10)

    # ------------------------------------------------------------------
    # progress
    # ------------------------------------------------------------------

    cmds.frameLayout(label="Progress",
                     width=550,
                     collapsable=False,
                     collapse=False,
                     marginWidth=5,
                     marginHeight=5)
    cmds.columnLayout(columnAlign="left")
    cmds.textScrollList(PROGRESS_LIST,
                        width=537,
                        height=120)
    cmds.setParent(layout)

    cmds.separator(style="none", height=10)

    # ------------------------------------------------------------------
    # buttons
    # ------------------------------------------------------------------

    form = cmds.formLayout(width=550)
    cmds.button(INSTALL_BUTTON,
                label="安装",
                width=150,
                height=30,
                command=performInstallation)
    cmds.button(UNINSTALL_BUTTON,
                label="卸载",
                width=150,
                height=30,
                command=performUninstall)
    cmds.button(HELP_BUTTON,
                label="帮助",
                width=60,
                height=30,
                command=openHelp,
                enable=helpExists())
    cmds.button(MODULE_BUTTON,
                label="Create .mod file{} only".format(multiSuffix()),
                width=150,
                height=30,
                command=performBuildModuleFiles)
    cmds.formLayout(form,
                    edit=True,
                    attachForm=[(INSTALL_BUTTON, "left", 0),
                                (INSTALL_BUTTON, "bottom", 0),
                                (UNINSTALL_BUTTON, "bottom", 0),
                                (MODULE_BUTTON, "bottom", 0),
                                (HELP_BUTTON, "right", 0),
                                (HELP_BUTTON, "bottom", 0)],
                    attachControl=[(UNINSTALL_BUTTON, "left", 5, INSTALL_BUTTON),
                                   (MODULE_BUTTON, "left", 5, UNINSTALL_BUTTON)],
                    attachNone=[(HELP_BUTTON, "left")])
    cmds.setParent(layout)

    cmds.showWindow(INSTALL_WIN)


def deleteExistingWindow(name):#如果存在指定的窗口及其偏好设置，则删除该窗口
    """Delete the given window if it exists along with it's preferences.

    :param name: The name of the window.
    :type name: str
    """
    if cmds.window(name, exists=True):
        cmds.deleteUI(name)
    if cmds.windowPref(name, query=True, exists=True):
        cmds.windowPref(name, remove=True)


def showLogo():#如果存在Logo文件，则在窗口中构建包含Logo的部分
    """Build the window section which contains the logo if it exists.
    """
    if not os.path.exists(LOGO_FILE):
        return

    cmds.image(image=LOGO_FILE)


def addFieldComment(text):#构建添加斜体注释行的元素，位于路径字段下方。
    """Build the elements for adding an italic comment line below the
    path fields.

    :param text: The information string.
    :type text: str
    """
    cmds.rowLayout(numberOfColumns=2)
    cmds.separator(style="none", width=85)
    cmds.text(label=text, font="obliqueLabelFont")
    cmds.setParent("..")


def addProgress(message):#将给定的消息字符串添加到进度滚动列表中。
    """Add the given message string to the progress scroll list.

    :param message: The message to add to the list.
    :type message: str
    """
    cmds.textScrollList(PROGRESS_LIST,
                        edit=True,
                        append=message)


def openHelp(*args):#打开安装帮助文档
    """Open the installation help document.
    """
    if not helpExists():
        return

    currentOS = getPlatform()

    if currentOS == "win64":
        os.startfile(HELP_FILE)
    else:
        cmd = "open" if currentOS == "macOS" else "xdg-open"
        subprocess.call([cmd, HELP_FILE])


def multiSuffix():#如果要安装的模块数量大于1，则返回's'以在从'file'到'files'的重命名中使用。
    """Return 's' to rename from 'file' to 'files' in case there is more
    than one module to install.
    """
    if len(getModuleNames()) > 1:
        return "s"
    return ""


# ----------------------------------------------------------------------
# path selection
# ----------------------------------------------------------------------

def selectContentPath():#获取用户定义的模块内容路径，并将其显示在路径字段中
    """Get a user defined path for the module content and display it in
    the path field.
    """
    filePath = cmds.textFieldGrp(CONTENT_PATH_FIELD,
                                 query=True,
                                 text=True)
    filePath = selectCustomPath(filePath)[0]
    cmds.textFieldGrp(CONTENT_PATH_FIELD,
                      edit=True,
                      text=filePath)


def selectModulePath():#获取用户定义的模块文件路径，并将其显示在路径字段中
    """Get a user defined path for the module file and display it in
    the path field.
    """
    filePath = cmds.textFieldGrp(MODULE_PATH_FIELD,
                                 query=True,
                                 text=True)
    filePath = selectCustomPath(filePath)[0]
    cmds.textFieldGrp(MODULE_PATH_FIELD,
                      edit=True,
                      text=filePath)


def selectCustomPath(filePath):#打开一个文件对话框，以给定的路径为起始路径，并返回用户选择的路径
    """Open a file dialog starting at the given path and return the
    chosen path.

    :param filePath: The path to start the dialog with.
    :type filePath: str

    :return: The selected path from the dialog.
    :rtype: str
    """
    return cmds.fileDialog2(caption="Select Path",
                            startingDirectory=filePath,
                            fileMode=3,
                            okCaption="Select")


# ----------------------------------------------------------------------
# module files
# ----------------------------------------------------------------------

def writeModuleFiles(destination, contentPath):#为安装中包含的每个模块编写一个模块文件
    """Write a module file for each module which is included in the
    installation.

    :param destination: The path where to write the module file to.
    :type destination: str
    :param contentPath: The path of the module contents.
    :type contentPath: str

    :return: True, if writing was successful.
    :rtype: bool
    """
    for module in getModuleNames():
        if not createModuleFile(destination, module, contentPath):
            return False
    return True


def createModuleFile(modulePath, module, contentPath):#为给定的模块生成模块文件的内容并将其写入给定的路径。
    """Generate the content of the module file for the given module and
    write it to the given path.

    :param modulePath: The path where to write the module file to.
    :type modulePath: str
    :param module: The name of the module.
    :type module: str
    :param contentPath: The path of the module contents.
    :type contentPath: str

    :return: True, if writing was successful.
    :rtype: bool
    """
    fileName = "{}.mod".format(os.path.join(modulePath, module))

    recursiveIcons = True
    if getPlatform() == "linux64":
        recursiveIcons = False

    lines = ""
    for version in getMayaVersions():
        lines += "+ MAYAVERSION:{} {} any {}/{}\n".format(version, module, contentPath, module)
        lines += buildContentSubpath(module, "plug-ins", version, getPlatform())
        lines += buildContentSubpath(module, "icons", recursive=recursiveIcons)
        lines += buildContentSubpath(module, "scripts", recursive=True)
        lines += "\n"

    if not write(fileName, lines, "w"):
        addProgress("Error: Writing module file: {}".format(fileName))
        return False

    message = "Writing module file: {}".format(fileName)
    logInfo(message)
    addProgress(message)

    return True


def buildContentSubpath(module, data, version="", platform="", recursive=False):# 生成指向给定数据内容的相对路径的模块行
    """Generate the line for the module which points to the given data
    content at a relative path.

    :param module: The name of the module.
    :type module: str
    :param data: The name of the data content.
    :type data: str
    :param version: The Maya version string.
    :type version: str
    :param platform: The platform string.
    :type platform: str
    :param recursive: True, if the path should be defined as recursive.
    :type recursive: bool

    :return: The line for the relative content of the module.
    :rtype: str
    """
    nested = ""
    if recursive:
        nested = "[r] "

    line = ""
    subdir = os.path.join(os.path.join(os.path.join(INSTALL_ROOT, MODULES_DIR), module), data)
    if os.path.exists(subdir):
        subPath = data
        if len(platform):
            subPath = "/".join((subPath, platform))
        if len(version):
            subPath = "/".join((subPath, version))
        line = "{}{}: {}\n".format(nested, data, subPath)
    return line


def flattenFolder(basePath):#将给定基础路径下的子文件夹移除，并将它们的内容放置在顶层。
    """Remove the sub folders from the given base path and place their
    contents at the top level.
    Currently necessary for installations on Linux where the recursive
    path option doesn't work for icons.

    :param basePath: The path of the folder which should be flattened.
    :type basePath: str

    :return: True, if flattening was successful.
    :rtype: bool
    """
    result = True
    for folder in os.listdir(basePath):
        folderPath = os.path.join(basePath, folder)
        if os.path.isdir(folderPath):
            for item in os.listdir(folderPath):
                if not item.startswith("."):
                    try:
                        shutil.move(os.path.join(folderPath, item), basePath)
                    except OSError:
                        result = False
            if not removeDir(folderPath):
                result = False

    if not result:
        message = "An error occurred while flattening the folder: {}".format(basePath)
        logInfo(message)
        addProgress(message)

    return result


# ----------------------------------------------------------------------
# finishing
# ----------------------------------------------------------------------

def disableButtons():#当不再需要安装按钮时，禁用安装按钮，并将按钮标签更改为“关闭”。
    """Disable the installation buttons when they are not required
    anymore.
    """
    cmds.button(INSTALL_BUTTON,
                edit=True,
                label="Close",
                command="cmds.deleteUI('{}')".format(INSTALL_WIN))
    cmds.button(UNINSTALL_BUTTON,
                edit=True,
                enable=False)
    cmds.button(MODULE_BUTTON,
                edit=True,
                enable=False)


def finish():#在安装成功完成时调用，清理并显示确认窗口，提示重新启动Maya。
    """Finish the installation by cleaning up and displaying a
    confirmation window to restart Maya.
    """
    disableButtons()

    result = cmds.confirmDialog(title="Installation successful",
                                message="You need to restart Maya for changes to take affect.",
                                button=("Close", "Quit Maya"))
    if result == "Quit Maya":
        cmds.quit(force=True)


def installationFailed():#当安装失败时调用，进行清理，并显示错误消息。
    """Finish the installation upon failure. Cleanup and displaying the
    error.
    """
    disableButtons()

    logInfo("Installation cancelled because an error has occurred.")
    om2.MGlobal.displayError("Installation failed. See install.log for details.")
    cmds.confirmDialog(title="Installation failed",
                       message="The installation has been cancelled because of an error.\nSee install.log for details.",
                       button="Close")


# ----------------------------------------------------------------------
# method which gets executed upon drag and drop
# ----------------------------------------------------------------------

def onMayaDroppedPythonFile(*args, **kwargs):#这是一个主要的函数，当用户将文件拖放到Maya中时运行。它执行安装过程，包括复制模块到用户首选项并创建模块文件。
    """Main function that runs when dragging the file into Maya.
    Installation is performed by copying the module to the user
    preferences and creating a module file.
    """
    # Don't continue if the installation files are missing.
    if not installExists():
        return

    logInfo("开始安装")

    # If a license file exists display the EULA window. Otherwise
    # continue to the installation window.
    if os.path.exists(os.path.join(INSTALL_ROOT, "LICENSE")):
        logInfo("显示 EULA")
        showEULA()
    else:
        prepareInstallation()


# ----------------------------------------------------------------------
# License
#
# Copyright (c) 2021 Ingo Clemens, brave rabbit
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Author: Ingo Clemens    www.braverabbit.com
# ----------------------------------------------------------------------
