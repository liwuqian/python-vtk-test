import vtkmodules.all as vtk
import os

# Function to read DICOM files from a directory
def read_mhd(directory):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(directory)
    reader.Update()
    return reader.GetOutput()

def set_volume_properties_default(volume_property):
    # Create transfer functions
    opacity_transfer_function = vtk.vtkPiecewiseFunction()
    color_transfer_function = vtk.vtkColorTransferFunction()
    gradient_opacity_transfer_function = vtk.vtkPiecewiseFunction()

    # Set up opacity transfer function
    opacity_transfer_function.AddPoint(-1000, 0.0)
    opacity_transfer_function.AddPoint(0, 0.0)
    opacity_transfer_function.AddPoint(1000, 1.0)

    # Set up color transfer function
    color_transfer_function.AddRGBPoint(-1000, 0.0, 0.0, 0.0)
    color_transfer_function.AddRGBPoint(0, 1.0, 1.0, 1.0)
    color_transfer_function.AddRGBPoint(1000, 1.0, 1.0, 1.0)

    # Set up gradient opacity transfer function
    gradient_opacity_transfer_function.AddPoint(-1000, 0.0)
    gradient_opacity_transfer_function.AddPoint(0, 0.0)
    gradient_opacity_transfer_function.AddPoint(1000, 1.0)

    # Apply transfer functions to volume property
    volume_property.SetScalarOpacity(opacity_transfer_function)
    # volume_property.SetGradientOpacity(gradient_opacity_transfer_function)
    volume_property.SetColor(color_transfer_function)
    

def set_volume_properties_for_bone(volume_property):
    # Create transfer functions
    opacity_transfer_function = vtk.vtkPiecewiseFunction()
    color_transfer_function = vtk.vtkColorTransferFunction()

    # Set up opacity transfer function
    opacity_transfer_function.AddPoint(0, 0.0)
    opacity_transfer_function.AddPoint(200, 0.0)
    opacity_transfer_function.AddPoint(1000, 0.2)
    opacity_transfer_function.AddPoint(2000, 0.8)

    # Set up color transfer function
    color_transfer_function.AddRGBPoint(0, 0.0, 0.0, 0.0)
    color_transfer_function.AddRGBPoint(200, 0.2, 0.1, 0.0)
    color_transfer_function.AddRGBPoint(1000, 1.0, 1.0, 0.8)
    color_transfer_function.AddRGBPoint(2000, 1.0, 1.0, 1.0)

    # Apply transfer functions to volume property
    volume_property.SetScalarOpacity(opacity_transfer_function)
    volume_property.SetColor(color_transfer_function)

# Function to create a VTK actor for a polygon
def create_polygon_actor():
    polygon = vtk.vtkRegularPolygonSource()
    polygon.SetNumberOfSides(600)
    polygon_mapper = vtk.vtkPolyDataMapper()
    polygon_mapper.SetInputConnection(polygon.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(polygon_mapper)
    actor.GetProperty().SetColor(1, 0, 0)  # Red color
    return actor

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

# Callback function for keyboard events
def keyboard_callback(obj, event):
    key = obj.GetKeySym()
    if key == "Up":
        transform.Translate(0, 1, 0)
    elif key == "Down":
        transform.Translate(0, -1, 0)
    elif key == "Left":
        transform.Translate(-1, 0, 0)
    elif key == "Right":
        transform.Translate(1, 0, 0)
    render_window.Render()

# Callback function for mouse events
def mouse_callback(obj, event):
    global last_x, last_y
    x, y = obj.GetEventPosition()
    if event == "LeftButtonPressEvent":
        last_x, last_y = x, y
    elif event == "LeftButtonReleaseEvent":
        pass
    elif event == "MouseMoveEvent":
        dx, dy = x - last_x, y - last_y
        transform.Translate(dx, dy, 0)
        last_x, last_y = x, y
        render_window.Render()

# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderer.SetUseDepthPeeling(1)
# must set 
renderer.SetUseDepthPeelingForVolumes(1)
renderer.SetMaximumNumberOfPeels(100)
renderer.SetOcclusionRatio(0.1)
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Read DICOM files
dicom_directory = "data/origin.mhd"
image_data = read_mhd(dicom_directory)

# Create a smart volume mapper
volume_mapper = vtk.vtkSmartVolumeMapper()
volume_mapper.SetInputData(image_data)

# Create a volume property
volume_property = vtk.vtkVolumeProperty()

set_volume_properties_default(volume_property)

# Create a volume
volume = vtk.vtkVolume()
volume.SetMapper(volume_mapper)
volume.SetProperty(volume_property)

# Create a polygon actor
polygon_actor = create_cylinder_actor()
polygon_actor.SetPosition(50, 50, -50)

# Create a transform to move the polygon actor
transform = vtk.vtkTransform()
polygon_actor.SetUserTransform(transform)

# Add actors to the renderer
renderer.AddActor(volume)
renderer.AddActor(polygon_actor)

# Setup keyboard and mouse events
# render_window_interactor.AddObserver("KeyPressEvent", keyboard_callback)
# render_window_interactor.AddObserver("LeftButtonPressEvent", mouse_callback)
# render_window_interactor.AddObserver("LeftButtonReleaseEvent", mouse_callback)
# render_window_interactor.AddObserver("MouseMoveEvent", mouse_callback)

# Initialize and start the interactor
render_window.Render()
render_window_interactor.Start()
