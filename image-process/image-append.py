import vtkmodules.all as vtk
# If the two image have intersection, do not use the class
# Append image along z-axis

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

def create_cylinder_actor():
    source = vtk.vtkCylinderSource()
    source.SetHeight(60)
    source.SetRadius(3)
    source.SetResolution(200)
    source.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0, 0.8, 0.5)
    actor.GetProperty().SetOpacity(0.8)
    return actor


def read_mhd(directory):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(directory)
    reader.Update()
    return reader

path_1 = "data/L1.mhd"
path_2 = "data/L2.mhd"
reader_1 = read_mhd(path_1)
reader_2 = read_mhd(path_2)
image_1 = vtk.vtkImageData()
image_1 = reader_1.GetOutput()
# image_1.SetExtent(0, 252, 0, 260, 0, 210)
image_2 = reader_2.GetOutput()
print("image 1 ------------------------")
print(image_1)
print("image 2 ------------------------")
print(image_2)

imageappend = vtk.vtkImageAppend()
# the default is 0
# imageappend.SetAppendAxis(2)
imageappend.PreserveExtentsOn()
imageappend.AddInputData(image_2)
imageappend.AddInputData(image_1)

imageappend.Update()
image_all = imageappend.GetOutput()
print("image all ------------------------")
print(image_all)

# Create renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Enable depth peeling
# 1. Use a render window with alpha bits (as initial value is 0 (false)):
renderWindow.SetAlphaBitPlanes(1)

# 2. Force to not pick a framebuffer with a multisample buffer
# (as initial value is 8):
renderWindow.SetMultiSamples(0)

# 3. Choose to use depth peeling (if supported) (initial value is 0 (false)):
# If 
renderer.SetUseDepthPeeling(1)
renderer.SetUseDepthPeelingForVolumes(1)

# 4. Set depth peeling parameters
maxNoOfPeels = 100
occlusionRatio = 0.1
# - Set the maximum number of rendering passes (initial value is 4):
renderer.SetMaximumNumberOfPeels(maxNoOfPeels)
# - Set the occlusion ratio (initial value is 0.0, exact image):
renderer.SetOcclusionRatio(occlusionRatio)

# Create volume mapper and volume
volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
# volumeMapper.SetInputConnection(imageappend.GetOutputPort())
volumeMapper.SetInputData(imageappend.GetOutput())
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)

# Create a volume property
volume_property = vtk.vtkVolumeProperty()
set_volume_properties_default(volume_property)
volume.SetProperty(volume_property)

# Add volume to the renderer
renderer.AddVolume(volume)

# Create a polygon actor
polygon_actor = create_cylinder_actor()
polygon_actor.SetPosition(50, 50, -50)
renderer.AddActor(polygon_actor)

# Add axis
axis = vtk.vtkAxesActor()
axis.SetTotalLength(30, 30, 30)
renderer.AddActor(axis)

# Set background color
renderer.SetBackground(1, 1, 1)

renderWindow.SetPosition(500, 300)
renderWindow.SetSize(600, 600)

# Start interaction
renderWindow.Render()
renderWindowInteractor.Start()
