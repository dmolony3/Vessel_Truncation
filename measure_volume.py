import vtk
from vmtk import vmtkscripts
from VesselTruncation import *
import GenerateCenterline

diameter=0.15
"""fname1='/media/microway/1TB/PhaseB/Monash5/Surface/PhaseA_Monash5_RCA_clipped_sp.vtp'
#dataReader=vtk.vtkDataReader()
readSurface = vtk.vtkXMLPolyDataReader()
readSurface.SetFileName(fname1)
readSurface.Update()
fname2='/media/microway/1TB/PhaseB/Monash5/Surface/PhaseA_Monash5_RCA_clipped_clsp.vtp'

vessel=VesselTruncation()
vessel.SetInputSurface(fname1)
vessel.SetInputCenterlines(fname2)
vessel.SetDiameter(diameter)
vessel.Update()
"""

filename='/media/microway/1TB/PhaseB/Monash5/Surface/PhaseA_Monash5_RCA.stl'
fname1='/media/microway/1TB/PhaseB/Monash5/Surface/PhaseA_Monash5_RCA_sp.vtp'
fname2='/media/microway/1TB/PhaseB/Monash5/Surface/PhaseA_Monash5_RCA_clsp.vtp'
readSurface=vtk.vtkSTLReader()
readSurface.SetFileName(filename)
readSurface.Update()

# generate centerline from unclipped centerlines file
centerlines=vmtkscripts.vmtkCenterlines()
centerlines.Surface=readSurface.GetOutput()
centerlines.RadiusArrayName='MaximumInscribedSphereRadius'
centerlines.Execute()

centerlines=GenerateCenterline.ExtractGeometry(centerlines)
centerlineviewer=vmtkscripts.vmtkCenterlineViewer()
centerlineviewer.Centerlines=centerlines.Centerlines
centerlineviewer.CellDataArrayName='GroupIds'
centerlineviewer.Legend=1
centerlineviewer.Execute()

branchClipper=vmtkscripts.vmtkBranchClipper()
branchClipper.Centerlines=centerlines.Centerlines
branchClipper.Surface=readSurface.GetOutput()
branchClipper.Execute()

surfaceWriter=vmtkscripts.vmtkSurfaceWriter()
surfaceWriter.Surface=branchClipper.Surface
surfaceWriter.Mode='ascii'
surfaceWriter.OutputFileName='/media/microway/1TB/PhaseB/Monash5/Surface/PhaseA_Monash5_RCA_sp.vtp'
surfaceWriter.Execute()
surfaceWriter=vmtkscripts.vmtkSurfaceWriter()
surfaceWriter.Surface=branchClipper.Centerlines
surfaceWriter.Mode='ascii'
surfaceWriter.OutputFileName='/media/microway/1TB/PhaseB/Monash5/Surface/PhaseA_Monash5_RCA_clsp.vtp'
surfaceWriter.Execute()


vessel=VesselTruncation()
vessel.SetInputSurface(fname1)
vessel.SetInputCenterlines(fname2)
vessel.SetDiameter(diameter)
vessel.Update()

vmtksurfaceviewer=vmtkscripts.vmtkSurfaceViewer()
vmtksurfaceviewer.Surface=readSurface.GetOutput()
vmtksurfaceviewer.Execute()
vmtksurfaceviewer=vmtkscripts.vmtkSurfaceViewer()
vmtksurfaceviewer.Surface=vessel.GetOutput()
vmtksurfaceviewer.Execute()

centerlinesTruncated=vmtkscripts.vmtkCenterlines()
centerlinesTruncated.Surface=vessel.GetOutput()
centerlinesTruncated.RadiusArrayName='MaximumInscribedSphereRadius'
centerlinesTruncated.SeedSelectorName='openprofiles'
centerlinesTruncated.Execute()

centerlineviewer=vmtkscripts.vmtkCenterlineViewer()
centerlineviewer.Centerlines=centerlinesTruncated.Centerlines
centerlineviewer.PointDataArrayName='MaximumInscribedSphereRadius'
centerlineviewer.Legend=1
centerlineviewer.NumberOfColors=10
centerlineviewer.Colormap='rainbow'
centerlineviewer.Execute()

# write surface to stl
stlWriter=vtk.vtkSTLWriter()
stlWriter.SetFileName('Model_clipped_volume.stl')
stlWriter.SetInputData(vessel.GetOutput())
stlWriter.Write()
