import vtkmodules.all as vtk

# Load your mesh
# read .vtk file
reader = vtk.vtkGenericDataObjectReader()
reader.SetFileName("data/noflyzone.vtk")
reader.Update()

# Simplify the mesh
decimate = vtk.vtkDecimatePro()
decimate.SetInputConnection(reader.GetOutputPort())
decimate.SetTargetReduction(0.7)  # Adjust the target reduction as needed
decimate.Update()

# Save the simplified mesh
writer = vtk.vtkSTLWriter()
writer.SetFileName("out/simplified_mesh.stl")
writer.SetInputData(decimate.GetOutput())
writer.Write()

# writer.SetFileName("data/original_mesh.stl")
# writer.SetInputData(reader.GetOutput())
# writer.Write()