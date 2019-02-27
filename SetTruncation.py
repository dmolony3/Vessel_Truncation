import vtk

class SetTruncation():
    def __init__(self):
        self.rootId=0
        self.clip_idx=None
        self.abscissas=None
        self.groupId=None
        self.Surface=None
        self.Centerlines=None
        self.notTruncated=0

    def Traverse(self, centerline_idx):
        """Traverses the centerline until diameter is found"""
        clip_candidate_idx=[]  
        num_points=int(self.Centerlines.GetPointData().GetArray('CenterlineIds').GetNumberOfTuples())
        for i in range(num_points):
            if int(self.Centerlines.GetPointData().GetArray('CenterlineIds').GetTuple(i)[0]) == centerline_idx:        
            # do not clip root i.e. groupid 0
                if int(self.Centerlines.GetPointData().GetArray('GroupIds').GetTuple(i)[0]) != self.rootId:
                    point=self.Centerlines.GetPoint(i)
                    normal = self.Centerlines.GetPointData().GetArray('FrenetTangent').GetTuple3(i)
                    plane=self._GeneratePlane(point, normal)
                    #clipped_model, cutPoly = self._SliceModel(plane)
                    #area = self._ComputeArea(cutPoly)
                    clip_candidate_idx = self._CompareDiameter(clip_candidate_idx, i)
        if not clip_candidate_idx:
            groupId = self.Centerlines.GetPointData().GetArray('GroupIds').GetTuple(i)
            abscissas = self.Centerlines.GetPointData().GetArray('Abscissas').GetTuple(i)
            clip_candidate_idx.append((i, groupId, abscissas))
            print("Vessel diameter greater than {}, clipping terminal id {}".format(self.diameter, clip_candidate_idx[-1][1]))
            self.notTruncated = 1
        else:
            print("Vessel diameter less than {}, clipping id {}".format(self.diameter, clip_candidate_idx[-1][1]))
        self.groupId = clip_candidate_idx[-1][1]
        self.abscissas = clip_candidate_idx[-1][2]        
        self.clip_idx = clip_candidate_idx[-1][0] 
 
    def SetInputSurface(self, surface):
        self.Surface=surface

    def SetInputCenterlines(self, centerlines):
        self.Centerlines=centerlines
       
    def SetDiameter(self, diameter):
        """Sets the diameter to perform the clippin at"""
        self.diameter=diameter      
      
    def GetTruncatedStatus(self):
        return self.notTruncated

    def GetTruncatedGroup(self):
        return self.groupId
    
    def GetTruncatedLength(self):
        return self.abscissas
    
    def GetTruncatedIdx(self):
        return self.clip_idx
      
    def _ComputeArea(cutPoly):
        """Computes the area of sliced surface"""
        area = []
        for i in range(cutPoly.GetNumberOfCells()):
            tri=polydata.GetCell(i)
            points=tri.GetPoints()
            area.append(tri.ComputeArea())

        print('Area is {}'.format(sum(area)))
        print('Diameter is {}'.format(sqrt(4*sum(area)/pi**2)))
        
    def _CompareDiameter(self, clip_candidate_idx, idx):
        """Checks if the diameter is less than the minimum diameter and stores the radius
        the corresponding groupId and Abscissas value"""
        radius=self.Centerlines.GetPointData().GetArray('MaximumInscribedSphereRadius').GetValue(idx)
        groupId = self.Centerlines.GetPointData().GetArray('GroupIds').GetTuple(idx)
        abscissas = self.Centerlines.GetPointData().GetArray('Abscissas').GetTuple(idx)
        diameter=radius*2
        if diameter <= self.diameter:
            if not clip_candidate_idx:
                clip_candidate_idx.append((idx, groupId, abscissas))
        elif diameter > self.diameter:
            if clip_candidate_idx: # if diameter increases again record this as the new cutoff
                clip_candidate_idx.append((idx, groupId, abscissas))
        return clip_candidate_idx

    def _GenerateFrenet(self):
        """Generates the frenet frame for an input centerline"""
        centerlineGeometry=vmtkscripts.vmtkCenterlineGeometry()
        centerlineGeometry.Centerlines=self.Centerlines
        centerlineGeometry.SmoothingFactor=0.4
        centerlineGeometry.FrenetTangentArrayName='FrenetTangent'
        centerlineGeometry.FrenetNormalArrayName='FrenetNormal'
        centerlineGeometry.FrenetBinormalArrayName='FrenetBinormal'
        centerlineGeometry.Execute()
        self.Centerlines=centerlineGeometry.Centerlines

    def _GeneratePlane(self, point, normal):
        plane=vtk.vtkPlane()
        plane.SetOrigin(point)
        plane.SetNormal(normal)
        return plane
    
    def _SliceModel(self, plane):
        """cuts surface and returns polydata of the clipped surface and the clipped face"""
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(self.Surface)
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
