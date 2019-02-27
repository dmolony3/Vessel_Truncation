import vtk
from vmtk import vmtkscripts


class ClipModel():
    def __init__(self):
        self.write = True
        self.fname = ''
        self.rootId=0
        self.normal=1 # flag determining whether the clipping returns a flat surface

    def Clip(self, surface, centerlines, clip_index):
        point = centerlines.GetPoint(clip_index)
        normal = centerlines.GetPointData().GetArray('FrenetTangent').GetTuple3(clip_index)
        plane = self._GeneratePlane(point, normal)
        if self.normal == 1:
            self.clipped = self._ClipModelNormal(plane, surface)
        elif self.normal == 0:
            self.clipped = self._ClipModel(plane, surface)

        if self.write:
            self.WriteModel()
              
    def SetNormal(self, normal):
        """Set flag determining whether the clipping plane should return a flat surface"""
        self.normal=normal
        
    def GetOutput(self):
        return self.clipped.GetOutput()

    def GetClippedOutput(self):
        "Returns the clipped output"""
        return self.clipped.GetClippedOutput()

    def WriteModel(self):
        """Writes model to file as stl file"""
        if self.fname == '':
            self.fname = 'Model1'
        stlWriter=vtk.vtkSTLWriter()
        stlWriter.SetFileName(self.fname+'.stl')
        stlWriter.SetInputData(self.clipped.GetOutput())
        stlWriter.Write()

    def _GeneratePlane(self, point, normal):
        plane=vtk.vtkPlane()
        plane.SetOrigin(point)
        plane.SetNormal(normal)
        return plane
    
    def _ClipModelNormal(self, plane, surface):
        """Clips surface"""
        clipper=vtk.vtkClipPolyData()
        clipper.SetInputData(surface)
        clipper.GenerateClipScalarsOn()
        clipper.GenerateClippedOutputOn()
        clipper.SetClipFunction(plane)
        clipper.Update()
        return clipper
    
    def _ClipModel(self, plane, surface):
        """Clips surface and returns full cells on the plane i.e. does not produce flat output"""
        clipper=vtk.vtkExtractPolyDataGeometry()
        clipper.SetInputData(surface)
        clipper.SetImplicitFunction(plane)
        clipper.Update()
        return clipper
