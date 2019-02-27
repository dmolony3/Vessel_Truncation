import vtk

class SurfaceSelection():
    def __init__(self):
        self.Write=0
        self.Reverse=1
        self.selection=None
        self.Surface=None

    def SelectGroup(self, truncatedIds, truncationLength):
        """Create a selection object of the desired groups
        truncatedId is a list of groups to include in the truncation
        """
        #print(truncatedIds)
        self.ids=self._ObtainIds(self.Surface, truncatedIds, truncationLength)

    def Update(self):
        """Runs the group selection"""
        selectionNode=vtk.vtkSelectionNode()
        selectionNode.SetFieldType(1)
        selectionNode.SetContentType(4)
        selectionNode.SetSelectionList(self.ids)        
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.INVERSE(), self.Reverse)
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(), 1);
        self.selection=vtk.vtkSelection()
        self.selection.AddNode(selectionNode)
        
        extract=vtk.vtkExtractSelection()
        extract.SetInputData(1, self.selection)
        extract.SetInputData(0, self.Surface) # flag of 0 for surface and 1 for selection
        extract.Update()
        self.polySurface=self._ConvertToPolyData(extract)

    def GetOutput(self):
        """return the output surface as vtkpolydata"""
        return self.polySurface

    def SetInputData(self, surface):
        self.Surface=surface

    def ReverseSelection(self, reverse):
        """Set to 1 if the main vessel is desired"""
        self.Reverse=reverse

    def _ObtainIds(self, surface, truncatedIds, truncationLength):
        ids=vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        truncation_tolerance=0.25 # cm
        for j in range(surface.GetPoints().GetNumberOfPoints()):
            if surface.GetPointData().GetArray('GroupIds').GetTuple(j)[0] in truncatedIds:
                if surface.GetPointData().GetArray('AbscissaMetric').GetTuple(j)[0] >= truncationLength[0]-truncation_tolerance:
                    ids.InsertNextValue(j)
        return ids
   
    def _ConvertToPolyData(self, extract):
        # convert back to polydata
        polySurface=vtk.vtkDataSetSurfaceFilter()
        polySurface.SetInputConnection(extract.GetOutputPort())
        polySurface.Update()
        return polySurface.GetOutput()
