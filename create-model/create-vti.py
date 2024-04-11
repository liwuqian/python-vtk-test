import vtkmodules.all as vtk

# Create a vtkImageData object
image_data = vtk.vtkImageData()
image_data.SetDimensions(10, 10, 10)  # Set dimensions (x, y, z)
image_data.SetOrigin(0.0, 0.0, 0.0)  # Set origin (optional)
image_data.SetSpacing(1.0, 1.0, 1.0)  # Set spacing (optional)
image_data.AllocateScalars(vtk.VTK_DOUBLE, 1)  # Allocate memory for scalar values

# Fill the image with some data (e.g., a simple gradient)
for z in range(10):
    for y in range(10):
        for x in range(10):
            value = x + y + z
            image_data.SetScalarComponentFromDouble(x, y, z, 0, value)

# Write the vtkImageData object to a VTI file
writer = vtk.vtkXMLImageDataWriter()
writer.SetFileName("data/output_custom.vti")
writer.SetInputData(image_data)
writer.Write()
