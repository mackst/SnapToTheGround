# -*- coding: utf-8 -*-

# 作者：石池


# from importlib import reload
import inspect
import os

import maya.app.general.mayaMixin as mm
import maya.cmds as cmds

from PySide2 import QtWidgets, QtUiTools, QtCore

import sttg_main.main as sttg
# reload(sttg)


class sttg_Widget(mm.MayaQWidgetDockableMixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(sttg_Widget, self).__init__(parent=parent)

        self.__pluginLoaded = False

        dirPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        self.__pluginDir = os.path.join(dirPath, 'sttg_main', 'plugins')
        self.__widget: QtWidgets.QWidget = QtUiTools.QUiLoader().load(os.path.join(dirPath, 'sttg_main', 'sttg_widget.ui'))
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.__widget)
        self.setWindowTitle(self.__widget.windowTitle())

        self.__shortcut = QtWidgets.QShortcut(self.__widget.keySE.keySequence(), self)
        self.__shortcut.setContext(QtCore.Qt.ApplicationShortcut)

        self.__widget.gmBtn.clicked.connect(self.setGroundMesh)
        self.__widget.keySE.keySequenceChanged.connect(self.__shortcut.setKey)
        self.__widget.goBtn.clicked.connect(self.doIt)
        self.__shortcut.activated.connect(self.doIt)
        self.__widget.pluginCB.stateChanged.connect(self.usePlugin)
    def usePlugin(self, status: bool):
        if status == QtCore.Qt.Checked:
            self.loadPlugin()
            if not self.__pluginLoaded:
                self.__widget.pluginCB.setChecked(False)
        else:
            if self.__pluginLoaded: 
                cmds.unloadPlugin('SnapToTheGround.mll')
                self.__pluginLoaded = False
    def loadPlugin(self) -> None:
        name = 'SnapToTheGround.mll'
        version = cmds.about(v=1)
        ppath = os.path.join(self.__pluginDir, version, name)
        if not os.path.exists(ppath): return
        try:
            cmds.loadPlugin(ppath, quiet=True)
            self.__pluginLoaded = True
        except Exception as e:
            print(e)
            

    def setGroundMesh(self) -> None:
        objs = cmds.ls(sl=True, l=1)
        if objs:
            self.__widget.gmLineEdit.setText(objs[0])

    def doIt(self) -> None:
        useGrid = self.__widget.useGridCB.isChecked()
        groundMesh = self.__widget.gmLineEdit.text()
        useCenterSnap = self.__widget.useCenterCB.isChecked()
        rayOffset = self.__widget.rloDSB.value()

        objs = cmds.ls(sl=True, l=1)
        if not objs: return

        if useGrid:
            if self.__pluginLoaded:
                cmds.snapToTheGrid(*objs)
            else:
                sttg.snapToTheGrid(objs)
        else:
            if cmds.objExists(groundMesh):
                if self.__pluginLoaded:
                    cmds.snapToTheGroundMesh(*objs, g=groundMesh, c=useCenterSnap, r=rayOffset)
                else:
                    sttg.snapToTheGroundMesh(objs, groundMesh, useCenterSnap, rayOffset)



def onMayaDroppedPythonFile(obj):
    # reload(sttg)

    sttg_window = sttg_Widget()
    sttg_window.show()

