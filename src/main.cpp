// 作者：石池

#include <algorithm>
#include <vector>
#include <maya/MString.h>
#include <maya/MArgList.h>
#include <maya/MFnPlugin.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionlist.h>
#include <maya/MItSelectionList.h>
#include <maya/MGlobal.h>
#include <maya/MDagPath.h>
#include <maya/MFnDagNode.h>
#include <maya/MBoundingBox.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>
#include <maya/MFnMesh.h>
#include <maya/MFloatVector.h>
#include <maya/MFloatPoint.h>
#include <maya/MFloatPointArray.h>
#include <maya/MMeshIntersector.h>
// #include <maya/MPointArray.h>



class SnapToTheGrid : public MPxCommand
{
public:
    MStatus doIt(const MArgList& args);
    // MStatus parseArgs(const MArgList& args);
    static void* creator();
    // static MSyntax newSyntax();
};

MStatus SnapToTheGrid::doIt(const MArgList& args)
{
    MSelectionList slist;

    if(args.length() > 0) {
        MString argStr;

        for (unsigned int i = 0; i < args.length(); i++)
        {
            args.get(i, argStr);
            slist.add(argStr);
        }
    } else {
        MGlobal::getActiveSelectionList(slist);
    }

    MDagPath dagPath;
    MFnDagNode dagNode;
    for(MItSelectionList iter(slist); !iter.isDone(); iter.next()){
        iter.getDagPath(dagPath);
        dagNode.setObject(dagPath);

        if(dagNode.isIntermediateObject()){
            continue;
        }

        MBoundingBox bbox = dagNode.boundingBox();
        MString ystr;
        ystr += -bbox.min().y;
        MString moveCmd;
        moveCmd.format("import maya.cmds as cmds; cmds.move(0, ^1s, 0, \"^2s\", r=True)", ystr, dagPath.fullPathName());
        MGlobal::executePythonCommand(moveCmd, true, true);
    }

    return MS::kSuccess;
}

void* SnapToTheGrid::creator()
{
    return new SnapToTheGrid;
}


class SnapToTheGroundMesh : public MPxCommand
{
private:
    MString groundMesh;
    bool center;
    double rayOffset;
    MSelectionList slist;

    MFloatPointArray getBBBottomPoints(MFnDagNode &dagNode);
    MFloatPoint getBBBottomCenter(MFnDagNode &dagNode);

public:
    MStatus doIt(const MArgList& args);
    MStatus parseArgs(const MArgList& args);
    static void* creator();
    static MSyntax newSyntax();
};

MFloatPoint SnapToTheGroundMesh::getBBBottomCenter(MFnDagNode &dagNode){
    auto bb = dagNode.boundingBox();
    return MFloatPoint(bb.center().x, bb.min().y, bb.center().z);
}

MFloatPointArray SnapToTheGroundMesh::getBBBottomPoints(MFnDagNode &dagNode){
    MFloatPointArray points;
    auto bb = dagNode.boundingBox();
    points.append(MFloatPoint(bb.min()));
    points.append(MFloatPoint(bb.max().x, bb.min().y, bb.max().z));
    points.append(MFloatPoint(bb.min().x, bb.min().y, -bb.min().z));
    points.append(MFloatPoint(-bb.min().x, bb.min().y, bb.min().z));
    return points;
}

MStatus SnapToTheGroundMesh::doIt(const MArgList& args)
{
    if(parseArgs(args) != MS::kSuccess){
        return MS::kFailure;
    }

    MStatus stat;
    MString moveCmd("import maya.cmds as cmds\n");

    MSelectionList gmList;
    stat = gmList.add(groundMesh);
    if(stat != MS::kSuccess){
        MGlobal::displayError("ground mesh is not found.");
        return MS::kFailure;
    }
    MDagPath gmDagPath;
    stat = gmList.getDagPath(0, gmDagPath);

    MFnMesh gmFn(gmDagPath, &stat);
    MMeshIsectAccelParams accelParams = gmFn.autoUniformGridParams();

    MFloatVector rayDir{0.0f, -1.0f, 0.0f};
    for(MItSelectionList iter(slist); !iter.isDone(); iter.next()){
        MDagPath dagPath;
        stat = iter.getDagPath(dagPath);
        MFnDagNode nodeFn(dagPath, &stat);
        if (center){
            MFloatPoint point = getBBBottomCenter(nodeFn);
            float maxParam = point.y + rayOffset;
            MFloatPoint hitPoint;
            float hitParam, hitBary1, hitBary2;
            int hitFace;
            int hitTriangle;
            bool hit = gmFn.anyIntersection(
                point, rayDir, nullptr, nullptr, false, MSpace::kWorld, 
                maxParam, false, &accelParams, hitPoint, &hitParam, 
                &hitFace, &hitTriangle, &hitBary1, &hitBary2, 
                (float)1e-6, &stat
            );
            if (hit) {
                auto y = hitPoint.y - nodeFn.boundingBox().min().y;
                MString ystr; ystr += y;
                MString cmd;
                cmd.format("cmds.move(0.0, ^1s, 0.0, \"^2s\", r=True)\n", ystr, dagPath.fullPathName());
                moveCmd += cmd;
            }
        } else {
            std::vector<double> ys;
            MFloatPointArray points = getBBBottomPoints(nodeFn);
            for(unsigned int i = 0; i < points.length(); i++){
                MFloatPoint point = points[i];
                float maxParam = point.y + rayOffset;
                MFloatPoint hitPoint;
                float hitParam, hitBary1, hitBary2;
                int hitFace;
                int hitTriangle;
                bool hit = gmFn.anyIntersection(
                    point,rayDir, nullptr, nullptr, false, MSpace::kWorld, 
                    maxParam, false, &accelParams, hitPoint, &hitParam, 
                    &hitFace, &hitTriangle, &hitBary1, &hitBary2, 
                    (float)1e-6, &stat
                );
                if (hit) {
                    ys.push_back(hitPoint.y);
                }
            }

            auto max_y = std::max_element(ys.begin(), ys.end());
            if (max_y != ys.end()) {
                auto y = *max_y - nodeFn.boundingBox().min().y;
                MString ystr; ystr += y;
                MString cmd;
                cmd.format("cmds.move(0.0, ^1s, 0.0, \"^2s\", r=True)\n", ystr, dagPath.fullPathName());
                moveCmd += cmd;
            }
        }
    }

    MGlobal::executePythonCommand(moveCmd, true, true);

    return MS::kSuccess;
}

MStatus SnapToTheGroundMesh::parseArgs(const MArgList& args) {
    MStatus status;
    MArgDatabase argData(syntax(), args, &status);
    if(status != MS::kSuccess){
        return status;
    }

    if(argData.isFlagSet("-g"))
        argData.getFlagArgument("-g", 0, groundMesh);
    else{
        MGlobal::displayError("ground mesh is not specified.");
        return MS::kFailure;
    }
    if(argData.isFlagSet("-c"))
        argData.getFlagArgument("-c", 0, center);
    else
        center = false;
    if(argData.isFlagSet("-r"))
        argData.getFlagArgument("-r", 0, rayOffset);
    else
        rayOffset = 5.0f;

    argData.getObjects(slist);

    return MS::kSuccess;
}

void* SnapToTheGroundMesh::creator()
{
    return new SnapToTheGroundMesh;
}

MSyntax SnapToTheGroundMesh::newSyntax()
{
    MSyntax syntax;
    // syntax.addFlag("-o", "-objs", MSyntax::kSelectionItem);
    syntax.addFlag("-g", "-ground", MSyntax::kString);
    syntax.addFlag("-c", "-center", MSyntax::kBoolean);
    syntax.addFlag("-r", "-rayOffset", MSyntax::kDouble);

    syntax.useSelectionAsDefault(true);
    syntax.setObjectType(MSyntax::kSelectionList, 1);

    return syntax;
}

MStatus initializePlugin(MObject obj)
{
    // MString author("石池");
    MFnPlugin plugin(obj, "Shi Chi", "1.0", "Any");
    MStatus status = plugin.registerCommand("snapToTheGrid", SnapToTheGrid::creator);
    if(!status)
        status.perror("registerCommand: snapToTheGrid");
    status = plugin.registerCommand("snapToTheGroundMesh", SnapToTheGroundMesh::creator, SnapToTheGroundMesh::newSyntax);
    if(!status)
        status.perror("registerCommand: snapToTheGroundMesh");
    return status;
}

MStatus uninitializePlugin(MObject obj)
{
    MFnPlugin plugin(obj);
    MStatus status = plugin.deregisterCommand("snapToTheGrid");
    if(!status)
        status.perror("deregisterCommand: snapToTheGrid");
    status = plugin.deregisterCommand("snapToTheGroundMesh");
    if(!status)
        status.perror("deregisterCommand: snapToTheGroundMesh");
    return status;
}