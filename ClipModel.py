import vtk
from vmtk import vmtkscripts

class ClipModel():
    def __init__(self):
        self.write = True
        self.fname = ''

    def SetDiameter(self, diameter):
        """Sets the diameter to perform the clippin at"""
        self.diameter=diameter

    def Clip(self, surface, centerlines, centerline_idx):
        """Clips the input surface at the desired diameter for the specified centerline"""
        centerlines = self.GenerateFrenet(centerlines)
        clip_candidate_idx=[]
        for i in range(int(centerlines.GetNumberOfPoints())):
            if int(centerlines.GetPointData().GetArray('CenterlineIds').GetTuple(i)[0]) == centerline_idx:
                point=centerlines.GetPoint(i)
                normal = centerlines.GetPointData().GetArray('FrenetTangent').GetTuple3(i)
                plane=self.GeneratePlane(point, normal)
                clipped_model, cutPoly = self.SliceModel(plane, surface)
                clip_candidate_idx = self.CompareDiameter(centerlines, clip_candidate_idx, i)
        if not clip_candidate_idx:
            print("Vessel diameter greater than {}, clipping distal portion {}".format(self.diameter, clip_candidate_idx))
            clip_candidate_idx.append(i)
        point = centerlines.GetPoint(clip_candidate_idx[-1])
        normal = centerlines.GetPointData().GetArray('FrenetTangent').GetTuple3(clip_candidate_idx[-1])
        self.plane = self.GeneratePlane(point, normal)
        self.clipped = self.ClipModel(self.plane, surface)
        if self.write:
           self.WriteModel() 
   
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

    def CompareDiameter(self, centerlines, clip_candidate_idx, idx):
        radius=centerlines.GetPointData().GetArray('MaximumInscribedSphereRadius').GetValue(idx)
        diameter=radius*2
        if diameter <= self.diameter:
            if not clip_candidate_idx:
                clip_candidate_idx.append(idx)
            elif diameter > self.diameter:
                if clip_candidate_idx: # if diameter increases again record this as the new cutoff
                    clip_candidate_idx.append(idx)
        return clip_candidate_idx

    def GenerateFrenet(self, centerlines):
        """Generates the frenet frame for an input centerline"""
        centerlineGeometry=vmtkscripts.vmtkCenterlineGeometry()
        centerlineGeometry.Centerlines=centerlines
        centerlineGeometry.SmoothingFactor=0.4
        centerlineGeometry.FrenetTangentArrayName='FrenetTangent'
        centerlineGeometry.FrenetNormalArrayName='FrenetNormal'
        centerlineGeometry.FrenetBinormalArrayName='FrenetBinormal'
        centerlineGeometry.Execute()
        return centerlineGeometry.Centerlines

    def GeneratePlane(self, point, normal):
        plane=vtk.vtkPlane()
        plane.SetOrigin(point)
        plane.SetNormal(normal)
        return plane

    def ClipModel(self, plane, surface):
        """Clips surface"""
        clipper=vtk.vtkClipPolyData()
        clipper.SetInputData(surface)
        clipper.GenerateClipScalarsOn()
        clipper.GenerateClippedOutputOn()
        clipper.SetClipFunction(plane)
        clipper.Update()
        return clipper

    def SliceModel(self, plane, surface):
        """cuts surface and returns polydata of the clipped surface and the clipped face"""
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(surface)
        cutter.Update()   
  
        FeatureEdges = vtk.vtkFeatureEdges()
        FeatureEdges.SetInputConnection(cutter.GetOutputPort())
        FeatureEdges.BoundaryEdgesOn()
        FeatureEdges.FeatureEdgesOff()
        FeatureEdges.NonManifoldEdgesOff()
        FeatureEdges.ManifoldEdgesOff()
        FeatureEdges.Update()
   
        cutStrips = vtk.vtkStripper()  # Forms loops (closed polylines) from cutter
        cutStrips.SetInputConnection(cutter.GetOutputPort())
        cutStrips.Update()
        cutPoly = vtk.vtkPolyData()  # This trick defines polygons as polyline loop
        cutPoly.SetPoints((cutStrips.GetOutput()).GetPoints())
        cutPoly.SetPolys((cutStrips.GetOutput()).GetLines())
 
        return cutter.GetOutput(), cutPoly

