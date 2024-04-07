# -*- coding: utf-8 -*-

# 作者：石池


from importlib import reload
import inspect
import os

import maya.app.general.mayaMixin as mm
import maya.cmds as cmds

from PySide2 import QtWidgets, QtUiTools, QtGui, QtCore

import sttg_main.main as sttg
reload(sttg)


class sttg_Widget(mm.MayaQWidgetDockableMixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(sttg_Widget, self).__init__(parent=parent)

        dirPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
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
            sttg.snapToTheGrid(objs)
        else:
            if cmds.objExists(groundMesh):
                sttg.snapToTheGroundMesh(objs, groundMesh, useCenterSnap, rayOffset)



def onMayaDroppedPythonFile(obj):
    reload(sttg)

    sttg_window = sttg_Widget()
    sttg_window.show()

