import vtk
from vmtk import pypes
from vmtk import vmtkscripts
from vmtk import vtkvmtk
from ClipModel import *
from SurfaceSelection import *
from view_scene import *
from SetTruncation import *

class VesselTruncation():
    def __init__(self):
        self.diameter=0.15
        self.Surface=None
        self.Centerlines=None
        self.numberOfSegments=0
        self.numberOfCenterlines=0
        self.numberOfSurfacePoints=0
        self.outputName='TruncatedModel.vtp'
        self.numberNotTruncated=0

    def Update(self):
        centerline=self.Centerlines
        surface=self.Surface
        self._GenerateCenterlineGroupIds()
        self._BrancheUniqueId()
        for centerline_idx in range(self.numberOfCenterlines+1):
            groupId = self._ObtainTerminalGroupId(centerline_idx)
            self._ClipVessel(centerline_idx, groupId)
        self.ExtractConnectedSurface()

    def GetOutput(self):
        """Returns the clipped volume surface"""
        return self.Surface

    def SetInputSurface(self, surface):
        """Set input surface"""
        self.Surface=surface

    def SetOutputFileName(self, fname):
        self.outputName=fname

    def Write(self):
        """Write the surface as xmlpolydata"""
        writer=vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(self.outputName)
        writer.SetInputData(self.Surface)
        writer.Write()

    def SetInputCenterlines(self, centerlines):          
        self.Centerlines=centerlines
        self.numberOfSegments=int(self.Centerlines.GetCellData().GetArray('CenterlineIds').GetNumberOfTuples())
        self.numberOfCenterlines=int(self.Centerlines.GetCellData().GetArray('CenterlineIds').GetRange()[1])

    def SetDiameter(self, diameter):
        """Set the diameter below which vessels are clipped"""
        self.diameter=diameter

    def SelectCenterline(self, centerlineId):
        return None

    def _GenerateCenterlineGroupIds(self):
        # generate tuple for centerline id and group id
        self._AssociateCenterlineGroupIdsWithPoints()
        self.centerlineCellGroupIds=vtk.vtkDoubleArray()
        self.centerlineCellGroupIds.SetNumberOfComponents(2)
        self.centerlineCellGroupIds.SetName('CenterlineGroupIds')
        for i in range(self.numberOfSegments):
            centerlineId=self.Centerlines.GetCellData().GetArray('CenterlineIds').GetTuple(i)
            groupId=self.Centerlines.GetCellData().GetArray('GroupIds').GetTuple(i)
            self.centerlineCellGroupIds.InsertNextTuple2(centerlineId[0], groupId[0])

        self._SortCenterlineGroupIds()

    def _ObtainTerminalGroupId(self, centerline_idx):
        # only clip the correct centerline and group
        for j in range(self.numberOfCenterlines+1):
            Ids = self.uniqueGroupId.GetTuple2(j)
            if Ids[0] == centerline_idx:
                groupId = self.uniqueGroupId.GetTuple2(j)[1]
                print('Vessel has unique terminal groupId:{}'.format(groupId))
        return groupId
    
    def _SortCenterlineGroupIds(self):
        #identify unique portion of centerline for each branch/vessel
        sortData=vtk.vtkSortFieldData()
        direction=1
        column=1
        sortData.SortArrayByComponent(self.centerlineCellGroupIds, column, direction)

    def _AssociateCenterlineGroupIdsWithPoints(self):
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

    def _BrancheUniqueId(self):
        # determine unique branch id by obtaining max value in each sorted index
        self.uniqueGroupId=vtk.vtkDoubleArray()
        self.uniqueGroupId.SetNumberOfComponents(2)
        visited = []
        for i in range(self.numberOfSegments):
            if self.centerlineCellGroupIds.GetTuple2(i)[0] not in visited:
                visited.append(self.centerlineCellGroupIds.GetTuple2(i)[0])
                self.uniqueGroupId.InsertNextTuple2(self.centerlineCellGroupIds.GetTuple2(i)[0], self.centerlineCellGroupIds.GetTuple2(i)[1])
                print(self.uniqueGroupId.GetTuple2(len(visited)-1), visited)

    def GetVolume(self):
        """Returns the volume of the vessel"""
        """
        capSurface=vtk.vtkFillHolesFilter()
        capSurface.SetInputData(self.Surface)
        capSurface.Update()"""
        capSurface=vmtkscripts.vmtkSurfaceCapper()
        capSurface.Interactive=0
        capSurface.Surface=self.Surface
        capSurface.Execute()
        vesselVolume=vtk.vtkMassProperties()
        vesselVolume.SetInputData(capSurface.Surface)
        print("Vessel Volume:{}", vesselVolume.GetVolume())
        
    def _GetTruncatedGroups(self, truncatedGroup, centerline_idx):
        """Returns the full list of groups that will be truncated"""
        truncatedGroups=[]
        for i in range(self.numberOfSegments):
            id = self.centerlineCellGroupIds.GetTuple2(i)
            if id[0] == centerline_idx:
                if id[1] >= int(truncatedGroup[0]):
                    truncatedGroups.append(id[1])
        return truncatedGroups

    def _ClipVessel(self, centerline_idx, groupId):
        """Clips the truncated vessel at the specified diameter"""
        # extract the vessel distal to the truncated id and length
        truncation=SetTruncation()
        truncation.SetDiameter(self.diameter)
        truncation.SetInputSurface(self.Surface)
        truncation.SetInputCenterlines(self.Centerlines)
        clip_candidate_idx=truncation.Traverse(centerline_idx)
        truncatedIndex=truncation.GetTruncatedIdx()
        truncatedGroup=truncation.GetTruncatedGroup()
        truncatedLength=truncation.GetTruncatedLength()
        self.numberNotTruncated+=truncation.GetTruncatedStatus()
        print("{} branches not truncated".format(self.numberNotTruncated))
        print("Truncation Id:{}; Truncation Length:{}".format(truncatedGroup, truncatedLength))
        
        truncatedGroups=self._GetTruncatedGroups(truncatedGroup, centerline_idx)
        print("GroupIds {} will form the truncation selection".format(truncatedGroups))
        
        clipSelection=SurfaceSelection()
        clipSelection.SetInputData(self.Surface)
        clipSelection.ReverseSelection(0)
        clipSelection.SelectGroup(truncatedGroups, truncatedLength)
        clipSelection.Update()     
       
        modelClipper=ClipModel()
        modelClipper.Clip(clipSelection.GetOutput(), self.Centerlines, truncatedIndex)
        
        # get reverse selection so we can combine later
        clipSelection.ReverseSelection(1)
        clipSelection.Update()    
        clippedVessel = self._MergeSurfaces(clipSelection.GetOutput(), modelClipper.GetClippedOutput())

        self.CalculateAbscissas(clippedVessel)
        #return clippedVessel

    def _MergeSurfaces(self, fullVessel, clippedVessel):
        """Merges the old surface with the truncated branch"""
        # merge with original model, excluding section with clipped group id
        appendFilter=vtk.vtkAppendPolyData()
        appendFilter.AddInputData(fullVessel)
        appendFilter.AddInputData(clippedVessel)
        appendFilter.Update()

        cleanAppended=vtk.vtkCleanPolyData()
        cleanAppended.SetInputData(appendFilter.GetOutput())
        cleanAppended.Update()
        return cleanAppended.GetOutput()
    
    def CalculateAbscissas(self, clippedVessel):
        """Calculates the abscissas metrics for input surface"""
        branchMetrics = vmtkscripts.vmtkBranchMetrics()
        branchMetrics.Surface=clippedVessel
        branchMetrics.Centerlines=self.Centerlines
        branchMetrics.ComputeAngularMetric=0
        branchMetrics.Execute()
        self.Surface = branchMetrics.Surface

    def ExtractConnectedSurface(self):
        """Extracts the single largest connected region"""
        connectedSurface=vtk.vtkPolyDataConnectivityFilter()
        connectedSurface.SetInputData(self.Surface)
        connectedSurface.Update()
        self.Surface=connectedSurface.GetOutput()        
    
    def ExcludeSections(self, excludeIds):
        """Excludes the desired segments from the surface
        excludeIds is a list of segments to exclude"""
        fullVessel=SurfaceSelection()
        fullVessel.SetInputData(self.Surface)
        fullVessel.ReverseSelection(1)
        fullVessel.SelectGroup(excludeIds)
        fullVessel.Update()
        self.Surface=fullVessel.GetOutput()
        return fullVessel.GetOutput()
