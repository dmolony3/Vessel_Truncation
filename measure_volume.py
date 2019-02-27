import vtk
from vmtk import vmtkscripts
from VesselTruncation import *
import GenerateCenterline

precomputed=0

diameters=[0.15, 0.1]
inputSurface='/media/microway/1TB/PhaseA/Case3/Surface2/PhaseA_LCA_3.stl'
fname1='/media/microway/1TB/PhaseA/Case3/Surface2/PhaseA_LCA_3_sp.vtp'
fname2='/media/microway/1TB/PhaseA/Case3/Surface2/PhaseA_LCA_3_clsp.vtp'

if precomputed == 1:
    readSurface = vtk.vtkXMLPolyDataReader()
    readSurface.SetinputSurface(fname1)
    readSurface.Update()

    readCenterlines = vtk.vtkXMLPolyDataReader()
    readCenterlines.SetinputSurface(fname2)
    readCenterlines.Update()

    for diameter in diameters:
        outputName=fname1.split('.') +str(diameter) + 'mm.vtp'
        vessel=VesselTruncation()
        vessel.SetInputSurface(readSurface.GetOutput())
        vessel.SetInputCenterlines(readCenterlines.GetOutput())
        vessel.SetDiameter(diameter)
        vessel.Update()
        vessel.SetOutputinputSurface(outputName)
        vessel.Write()
        vessel.GetVolume()
else:
    readSurface=vtk.vtkSTLReader()
    readSurface.SetinputSurface(inputSurface)
    readSurface.Update()

    # generate centerline
    centerlines=vmtkscripts.vmtkCenterlines()
    centerlines.Surface=readSurface.GetOutput()
    centerlines.RadiusArrayName='MaximumInscribedSphereRadius'
    centerlines.Execute()

    centerlines=GenerateCenterline.ExtractGeometry(centerlines)
    centerlineviewer=vmtkscripts.vmtkCenterlineViewer()
    centerlineviewer.Centerlines=centerlines.Centerlines
    #centerlineviewer.CellDataArrayName='GroupIds'
    centerlineviewer.PointDataArrayName='MaximumInscribedSphereRadius'
    centerlineviewer.Legend=1
    centerlineviewer.Execute()

    branchClipper=vmtkscripts.vmtkBranchClipper()
    branchClipper.Centerlines=centerlines.Centerlines
    branchClipper.Surface=readSurface.GetOutput()
    branchClipper.Execute()

    branchMetrics=vmtkscripts.vmtkBranchMetrics()
    branchMetrics.Centerlines=branchClipper.Centerlines
    branchMetrics.Surface=branchClipper.Surface
    branchMetrics.AbscissasArrayName='Abscissas'
    branchMetrics.ComputeAngularMetric=0
    branchMetrics.Execute()

    surfaceWriter=vmtkscripts.vmtkSurfaceWriter()
    surfaceWriter.Surface=branchMetrics.Surface
    surfaceWriter.Format='vtkxml'
    surfaceWriter.Mode='ascii'
    surfaceWriter.OutputinputSurface=fname1
    surfaceWriter.Execute()
    surfaceWriter=vmtkscripts.vmtkSurfaceWriter()
    surfaceWriter.Format='vtkxml'
    surfaceWriter.Surface=branchClipper.Centerlines
    surfaceWriter.Mode='ascii'
    surfaceWriter.OutputinputSurface=fname2
    surfaceWriter.Execute()

    for diameter in diameters:
        outputName=fname1.split('.')+str(diameter) + 'mm.vtp'
        vessel=VesselTruncation()
        vessel.SetInputSurface(branchMetrics.Surface)
        vessel.SetInputCenterlines(branchClipper.Centerlines)
        vessel.SetDiameter(diameter)
        vessel.SetOutputinputSurface(outputName)
        vessel.Update()
        vessel.Write()
        vessel.GetVolume()

vmtksurfaceviewer=vmtkscripts.vmtkSurfaceViewer()
vmtksurfaceviewer.Surface=vessel.GetOutput()
vmtksurfaceviewer.Execute()
