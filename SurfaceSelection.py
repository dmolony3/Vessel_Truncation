import vtk

class SurfaceSelection():
    def __init__(self):
        self.Write=0
        self.Reverse=1

    def SelectGroup(self, groupId):
        """Create a selection object of the desired group"""
        ids=self.ObtainIds(self.Surface, groupId)
        selectionNode=vtk.vtkSelectionNode()
        selectionNode.SetFieldType(1)
        selectionNode.SetContentType(4)
        selectionNode.SetSelectionList(ids)        
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.INVERSE(), self.Reverse)
        selectionNode.GetProperties().Set(vtk.vtkSelectionNode.CONTAINING_CELLS(), 1);
        self.selection=vtk.vtkSelection()
        self.selection.AddNode(selectionNode)

    def Update(self):
        """Runs the group selection"""
        extract=vtk.vtkExtractSelection()
        extract.SetInputData(1, self.selection)
        extract.SetInputData(0, self.Surface) # flag of 0 for surface and 1 for selection
        extract.Update()
        self.polySurface=self.ConvertToPolyData(extract)

    def GetOutput(self):
        """return the output surface as vtkpolydata"""
        return self.polySurface

    def SetInputData(self, surface):
        self.Surface=surface

    def ReverseSelection(self, reverse):
        """Set to 1 if the main vessel is desired"""
        self.Reverse=reverse

    def ObtainIds(self, surface, groupId):
        ids=vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        for j in range(surface.GetPoints().GetNumberOfPoints()):
            if surface.GetPointData().GetArray('GroupIds').GetTuple(j)[0] == groupId:
                ids.InsertNextValue(j)
        return ids
   
    def ConvertToPolyData(self, extract):
        # convert back to polydata
        polySurface=vtk.vtkDataSetSurfaceFilter()
        polySurface.SetInputConnection(extract.GetOutputPort())
        polySurface.Update()
        return polySurface.GetOutput()

