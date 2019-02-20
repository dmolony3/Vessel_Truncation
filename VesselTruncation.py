import vtk
from vmtk import pypes
from vmtk import vmtkscripts
from vmtk import vtkvmtk
from ClipModel import *
from SurfaceSelection import *
from view_scene import *

class VesselTruncation():
    def __init__(self):
        self.diameter=0.15
        self.Surface=None
        self.Centerlines=None
        self.numberOfSegments=0
        self.numberOfCenterlines=0
        self.numberOfSurfacePoints=0

    def Update(self):
        centerline=self.Centerlines
        surface=self.Surface
        self.GenerateCenterlineGroupIds()
        self.BrancheUniqueId()
        for centerline_idx in range(self.numberOfCenterlines+1):
            self.SegmentGroupId(centerline_idx)
            self.ClipVessel(centerline_idx)
            self.Surface = self.MergeSurfaces()

    def GetOutput(self):
        """Returns the clipped volume surface"""
        return self.Surface

    def SetInputSurface(self, fname):
        """Reads vtk poly data"""
        readSurface = vtk.vtkXMLPolyDataReader()
        readSurface.SetFileName(fname)
        readSurface.Update()
        self.Surface=readSurface.GetOutput()
        self.numberOfSurfacePoints=int(self.Surface.GetNumberOfPoints())

    def SetInputCenterlines(self, fname):
        readCenterline = vtk.vtkXMLPolyDataReader()
        readCenterline.SetFileName(fname)
        readCenterline.Update()            
        self.Centerlines=readCenterline.GetOutput()
        self.numberOfSegments=int(self.Centerlines.GetCellData().GetArray('CenterlineIds').GetNumberOfTuples())
        self.numberOfCenterlines=int(self.Centerlines.GetCellData().GetArray('CenterlineIds').GetRange()[1])

    def SetDiameter(self, diameter):
        """Set the diameter below which vessels are clipped"""
        self.diameter=diameter

    def SelectCenterline(self, centerlineId):
        return None

    def GenerateCenterlineGroupIds(self):
        # generate tuple for centerline id and group id
        self.AssociateCenterlineWithPoint()
        self.centerlineCellGroupIds=vtk.vtkDoubleArray()
        self.centerlineCellGroupIds.SetNumberOfComponents(2)
        self.centerlineCellGroupIds.SetName('CenterlineGroupIds')
        for i in range(self.numberOfSegments):
            centerlineId=self.Centerlines.GetCellData().GetArray('CenterlineIds').GetTuple(i)
            groupId=self.Centerlines.GetCellData().GetArray('GroupIds').GetTuple(i)
            self.centerlineCellGroupIds.InsertNextTuple2(centerlineId[0], groupId[0])

        self.SortCenterlineGroupIds()

    def SegmentGroupId(self, centerline_idx):
        # only clip the correct centerline and group
        for j in range(self.numberOfCenterlines+1):
            Ids = self.uniqueGroupId.GetTuple2(j)
            if Ids[0] == centerline_idx:
                self.groupId = self.uniqueGroupId.GetTuple2(j)[1]
                print('Vessel has unique groupId:{}'.format(self.groupId))

    def SortCenterlineGroupIds(self):
        #identify unique portion of centerline for each branch/vessel
        sortData=vtk.vtkSortFieldData()
        direction=1
        column=1
        sortData.SortArrayByComponent(self.centerlineCellGroupIds, column, direction)

    def AssociateCenterlineWithPoint(self):
        # associate centerline point data with centerline id cell data
        pointCenterlineIds=vtk.vtkDoubleArray()
        pointCenterlineIds.SetNumberOfComponents(1)
        pointCenterlineIds.SetName('CenterlineIds')
        pointGroupIds=vtk.vtkDoubleArray()
        pointGroupIds.SetNumberOfComponents(1)
        pointGroupIds.SetName('GroupIds')
        idx=0
        for i in range(self.numberOfSegments):
            numberOfEdges=int(self.Centerlines.GetLines().GetData().GetTuple(idx)[0])
            centerlineId=self.Centerlines.GetCellData().GetArray('CenterlineIds').GetTuple(i)
            groupId=self.Centerlines.GetCellData().GetArray('GroupIds').GetTuple(i)
            for j in range(0, numberOfEdges):
                #print(centerline.GetCell(i).GetPoints().GetPoint(j), numberOfEdges)
                #print(centerline.GetPoint(j), centerline.GetLines().GetData().GetTuple(j))
                pointCenterlineIds.InsertNextTuple(centerlineId)
                pointGroupIds.InsertNextTuple(groupId)
            idx = idx+numberOfEdges+1

        self.Centerlines.GetPointData().AddArray(pointCenterlineIds)
        self.Centerlines.GetPointData().AddArray(pointGroupIds)

    def BrancheUniqueId(self):
        # determine unique branch id by obtaining max value in each sorted index
        self.uniqueGroupId=vtk.vtkDoubleArray()
        self.uniqueGroupId.SetNumberOfComponents(2)
        visited = []
        for i in range(self.numberOfSegments):
            if self.centerlineCellGroupIds.GetTuple2(i)[0] not in visited:
                visited.append(self.centerlineCellGroupIds.GetTuple2(i)[0])
                self.uniqueGroupId.InsertNextTuple2(self.centerlineCellGroupIds.GetTuple2(i)[0], self.centerlineCellGroupIds.GetTuple2(i)[1])
                print(self.uniqueGroupId.GetTuple2(len(visited)-1), visited)

    def GenereteIdList(self):
        ids=vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        for j in range(self.Surface.GetPoints().GetNumberOfPoints()):
            if self.Surface.GetPointData().GetArray('GroupIds').GetTuple(j)[0] == self.groupId:
                ids.InsertNextValue(j)

    def GetVolume(self):
        """Returns the volume of the vessel"""
        vesselVolume=vtk.vtkMassProperties()
        vesselVolume.SetInputData(self.Surface)
        print("Vessel Volume:{}", vesselVolume.GetVolume())

    def ClipVessel(self, centerline_idx):
        """Clips the vessel at the specified diameter"""
        modelClipper=ClipModel()
        modelClipper.SetDiameter(self.diameter)
        modelClipper.Clip(self.Surface, self.Centerlines, centerline_idx)

        # extract the clipped vessel with the correct group id
        self.clippedVessel=SurfaceSelection()
        self.clippedVessel.SetInputData(modelClipper.GetClippedOutput())
        self.clippedVessel.ReverseSelection(0)
        self.clippedVessel.SelectGroup(self.groupId)
        self.clippedVessel.Update()

        connected = vtk.vtkPolyDataConnectivityFilter()
        connected.SetInputData(self.clippedVessel.GetOutput())
        connected.Update()

    def MergeSurfaces(self):
        """Merges the old surface with the truncated branch"""
        fullVessel=SurfaceSelection()
        fullVessel.SetInputData(self.Surface)
        fullVessel.ReverseSelection(1)
        fullVessel.SelectGroup(self.groupId)
        fullVessel.Update()

        # merge with original model, excluding section with clipped group id
        appendFilter=vtk.vtkAppendPolyData()
        appendFilter.AddInputData(fullVessel.GetOutput())
        appendFilter.AddInputData(self.clippedVessel.GetOutput())
        appendFilter.Update()

        cleanAppended=vtk.vtkCleanPolyData()
        cleanAppended.SetInputData(appendFilter.GetOutput())
        cleanAppended.Update()
        return cleanAppended.GetOutput()
