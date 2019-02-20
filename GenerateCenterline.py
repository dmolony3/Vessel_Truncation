import vtk
from vmtk import vmtkscripts

def EquispacedSpline(line,l):  
   splineFilter = vtk.vtkSplineFilter()
   splineFilter.SetInputData(line)
   splineFilter.SetSubdivideToLength()
   splineFilter.SetLength(l)
   splineFilter.Update()

   return splineFilter.GetOutput()  


def ExtractGeometry(centerlines):

    centerlines.Centerlines=EquispacedSpline(centerlines.Centerlines,0.05) 
    centerlineGeometry=vmtkscripts.vmtkCenterlineGeometry()
    centerlineGeometry.Centerlines=centerlines.Centerlines
    centerlineGeometry.SmoothingFactor=0.4
    centerlineGeometry.FrenetTangentArrayName='FrenetTangent'
    centerlineGeometry.FrenetNormalArrayName='FrenetNormal'
    centerlineGeometry.FrenetBinormalArrayName='FrenetBinormal'
    centerlineGeometry.Execute()

    centerlineAttributes=vmtkscripts.vmtkCenterlineAttributes()
    centerlineAttributes.Centerlines=centerlineGeometry.Centerlines
    centerlineAttributes.Execute()


    branchExtractor=vmtkscripts.vmtkBranchExtractor()
    branchExtractor.Centerlines=centerlineGeometry.Centerlines
    branchExtractor.GroupIdsArrayName = 'GroupIds'
    branchExtractor.RadiusArrayName='MaximumInscribedSphereRadius'
    branchExtractor.CenterlineIdsArrayName = 'CenterlineIds'
    branchExtractor.BlankingArrayName='Blanking'
    branchExtractor.Execute()

    return branchExtractor
