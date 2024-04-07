# -*- coding: utf-8 -*-

# 作者：石池


import maya.api.OpenMaya as om
import maya.cmds as cmds



def getObjBB(obj: str) -> om.MBoundingBox:
    """
    获取指定对象的边界盒
    :param obj: 需要获取边界盒的对象
    :return: om.MBoundingBox
    """
    dagpath = om.MSelectionList().add(obj).getDagPath(0)
    node = om.MFnDagNode(dagpath)
    return node.boundingBox

def getObjsBBs(objs: list[str]) -> list[om.MBoundingBox]:
    """
    获取指定对象的边界盒
    :param objs: 需要获取边界盒的对象
    :return: list[om.MBoundingBox]
    """
    return [getObjBB(obj) for obj in objs]

def getBBBottomPoints(boundingBox: om.MBoundingBox) -> list[om.MPoint]:
    """
    获取边界盒的底面顶点
    :param boundingBox: om.MBoundingBox
    :return: list[om.MPoint]
    """
    minPoint = boundingBox.min
    maxPoint = boundingBox.max
    return [
        minPoint,
        om.MPoint(maxPoint.x, minPoint.y, maxPoint.z),
        om.MPoint(minPoint.x, minPoint.y, -minPoint.z),
        om.MPoint(-minPoint.x, minPoint.y, minPoint.z),
    ]

def getBBBottomCenter(boundingBox: om.MBoundingBox) -> om.MPoint:
    """
    获取边界盒的底面中心点
    :param boundingBox: om.MBoundingBox
    :return: om.MPoint
    """
    minPoint = boundingBox.min
    centerPoint = boundingBox.center
    return om.MPoint(centerPoint.x, minPoint.y, centerPoint.z)

def snapToTheGrid(objs: list[str]) -> None:
    """
    把指定的对象进行网格对齐
    :param objs: 需要对齐的对象
    :return: None
    """
    chunkName = "snapToTheGrid"
    cmds.undoInfo(openChunk=True, chunkName=chunkName)
    for obj in objs:
        bb = getObjBB(obj)
        y = -bb.min.y

        cmds.move(0.0, y, 0.0, obj, r=True)

    cmds.undoInfo(closeChunk=True, chunkName=chunkName)

# snapToTheGrid(["pCube1", "pCube2"])


def snapToTheGroundMesh(objs: list[str], groundMesh: str, centerSnap: bool = False, rayLengthOffset: float = 5.0) -> None:
    """
    把指定的对象进行网格对齐
    :param objs: 需要对齐的对象
    :param groundMesh: 需要对齐的网格
    :return: None
    """
    chunkName = "snapToTheGroundMesh"
    moveInfo = {}

    meshPath = om.MSelectionList().add(groundMesh).getDagPath(0)
    meshFn = om.MFnMesh(meshPath)

    rayDir = om.MFloatVector(0.0, -1.0, 0.0)
    for obj in objs:
        bb = getObjBB(obj)
        maxParam = abs(bb.min.y) + rayLengthOffset
        if centerSnap:
            point = om.MFloatPoint(getBBBottomCenter(bb))
            
            hitInfo = meshFn.anyIntersection(
                point,
                rayDir,
                om.MSpace.kWorld,
                maxParam,
                False,
                accelParams=meshFn.autoUniformGridParams()
            )
            if hitInfo:
                hitPoint = hitInfo[0]
                moveInfo[obj] = hitPoint.y - bb.min.y
        else:
            bottomPoints = getBBBottomPoints(bb)
            y_s = []
            for p in bottomPoints:
                point = om.MFloatPoint(p)
                hitInfo = meshFn.anyIntersection(
                    point,
                    rayDir,
                    om.MSpace.kWorld,
                    maxParam,
                    False,
                    accelParams=meshFn.autoUniformGridParams()
                )
                if hitInfo:
                    y_s.append(hitInfo[0].y)

            if y_s:
                y = max(y_s)
                moveInfo[obj] = y - bb.min.y

    cmds.undoInfo(openChunk=True, chunkName=chunkName)
    [cmds.move(0.0, moveInfo[obj], 0.0, obj, r=True) for obj in moveInfo]
    cmds.undoInfo(closeChunk=True, chunkName=chunkName)

# snapToTheGroundMesh(["pCube1", "pCube2", "pCube5"], "pPlane1", centerSnap=False)