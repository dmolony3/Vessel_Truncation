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

    #centerlines=EquispacedSpline(centerlines.Centerlines,0.05) # every 0.5mm
    centerlineResampling=vmtkscripts.vmtkCenterlineResampling()
    centerlineResampling.Centerlines=centerlines.Centerlines
    centerlineResampling.Length=0.05
    centerlineResampling.Execute()

    centerlineGeometry=vmtkscripts.vmtkCenterlineGeometry()
    centerlineGeometry.Centerlines=centerlineResampling.Centerlines
    centerlineGeometry.SmoothingFactor=0.4
    centerlineGeometry.FrenetTangentArrayName='FrenetTangent'
    centerlineGeometry.FrenetNormalArrayName='FrenetNormal'
    centerlineGeometry.FrenetBinormalArrayName='FrenetBinormal'
    centerlineGeometry.Execute()

    centerlineAttributes=vmtkscripts.vmtkCenterlineAttributes()
    centerlineAttributes.Centerlines=centerlineGeometry.Centerlines
    centerlineAttributes.Execute()

    branchExtractor=vmtkscripts.vmtkBranchExtractor()
    branchExtractor.Centerlines=centerlineAttributes.Centerlines
    branchExtractor.GroupIdsArrayName = 'GroupIds'
    branchExtractor.RadiusArrayName='MaximumInscribedSphereRadius'
    branchExtractor.CenterlineIdsArrayName = 'CenterlineIds'
    branchExtractor.BlankingArrayName='Blanking'
    branchExtractor.Execute()

    return branchExtractor
