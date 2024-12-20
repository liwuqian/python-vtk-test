import vtk

def set_volume_properties_default(volumeProperty):
    # Create color transfer function
    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.AddRGBPoint(-3024, 0, 0, 0)
    colorTransferFunction.AddRGBPoint(-16, 0.73, 0.25, 0.30)
    colorTransferFunction.AddRGBPoint(641, 0.90, 0.82, 0.56)
    colorTransferFunction.AddRGBPoint(3071, 1, 1, 1)

    # Create opacity transfer function
    opacityTransferFunction = vtk.vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(-3024, 0.0)
    opacityTransferFunction.AddPoint(-16, 0.0)
    opacityTransferFunction.AddPoint(641, 0.5)
    opacityTransferFunction.AddPoint(3071, 0.5)

    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)
    # volumeProperty.SetScalarOpacityUnitDistance(0, 4.5)  # Adjust as needed

# Create a reader for the MHD file
# filename = "/opt/mnav/data/PHI/patientdata/jiagu2^^/CT-1/registerplandata/Whole.mhd"
filename = "data/origin.mhd"
reader = vtk.vtkMetaImageReader()
reader.SetFileName(filename)
reader.Update()

# using set_volume_properties_default to viualize the image
image_data = reader.GetOutput()
volumeProperty = vtk.vtkVolumeProperty()
set_volume_properties_default(volumeProperty)

# Create a mapper
mapper = vtk.vtkSmartVolumeMapper()
mapper.SetInputConnection(reader.GetOutputPort())

# Create a volume
volume = vtk.vtkVolume()
volume.SetMapper(mapper)
volume.SetProperty(volumeProperty)

# Create a renderer
renderer = vtk.vtkRenderer()
renderer.AddVolume(volume)

# add axes to the renderer
axes = vtk.vtkAxesActor()
axes.SetTotalLength(10, 10, 10)
renderer.AddActor(axes)

# Create a render window
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# Set window size and to center of the screen
renderWindow.SetSize(600, 600)
renderWindow.SetPosition(500, 500)

# Set camera to look the volume from oblique angle
renderer.ResetCamera()
camera = renderer.GetActiveCamera()
# camera.SetPosition(-500, 500, 500)
# camera.SetFocalPoint(0, 0, 0)
# camera.SetViewUp(0, 0, 1)
camera.Azimuth(95)
camera.Elevation(-25)


# Create a render window interactor
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Start the rendering loop
renderWindow.Render()
renderWindowInteractor.Start()
