import vtkmodules.all as vtk

'''
This script demonstrates how to adjust the window width and level of a volume rendering.
The user can adjust the window width and level using the 'w', 's', 'a', and 'd' keys.
The user can adjust the volume opacity using the 'o' and 'p' keys.
'''

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
    actor.GetProperty().SetOpacity(0.6)
    return actor


# add function to adjust volume window width and level
def adjust_window_level(volume_property, window, level):
    color_func = volume_property.GetRGBTransferFunction(0)
    scalar_range = [0, 0]
    color_func.GetRange(scalar_range)
    print("Scalar range in adjust:", scalar_range)
    # scalar_range = volume_property.GetScalarOpacity(0).GetRange()
    color_func.RemoveAllPoints()
    # color_func.AddRGBPoint(scalar_range[0], 0, 0, 0)
    color_func.AddRGBPoint(level - window / 2, 0, 0, 0)
    color_func.AddRGBPoint(level + window / 2, 1, 1, 1)
    # color_func.AddRGBPoint(scalar_range[1], 1, 1, 1)
    volume_property.SetColor(color_func)

    opacity_func = volume_property.GetScalarOpacity(0)
    opacity_func.RemoveAllPoints()
    # opacity_func.AddPoint(scalar_range[0], 0)
    opacity_func.AddPoint(level - window / 2, 0.0)
    opacity_func.AddPoint(level + window / 2, 1)
    # opacity_func.AddPoint(scalar_range[1], 1)
    volume_property.SetScalarOpacity(opacity_func)

    return volume_property

# add function to adjust volume opacity
def adjust_volume_opacity(volume_property, opacity):
    scalar_range = volume_property.GetScalarOpacity(0).GetRange()
    print("Scalar range:", scalar_range)
    # Create a vtkPiecewiseFunction instance for the scalar opacity
    opacity_func = volume_property.GetScalarOpacity(0)
    opacity_func.RemoveAllPoints()
    opacity_func.AddPoint(scalar_range[0], 0)
    opacity_func.AddPoint(scalar_range[1], opacity)
    
    # Set the scalar opacity function
    volume_property.SetScalarOpacity(opacity_func)
    
    return volume_property

def read_mhd(directory):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(directory)
    reader.Update()
    return reader

def read_nii(directory):
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(directory)
    reader.Update()
    return reader


# Read the data
filename = "data/origin.mhd"
filename = "output/liver_57_label_19.mhd"
filename = "output/label_19.mhd"
# filename = "label_19_cropped.mhd"
reader = read_mhd(filename)
# filename = "data/liver_57.nii.gz"
# reader = read_nii(filename)

scalar_range = reader.GetOutput().GetScalarRange()
print("filename:", filename)
print("Scalar range:", scalar_range)
# print origin, extent, dimensions, bounds
origin = reader.GetOutput().GetOrigin()
extent = reader.GetOutput().GetExtent()
dimensions = reader.GetOutput().GetDimensions()
bounds = reader.GetOutput().GetBounds()
print("Origin:", origin)
print("Extent:", extent)
print("Dimensions:", dimensions)
print("Bounds:", bounds)

# Create transfer functions
color_func = vtk.vtkColorTransferFunction()
color_func.AddRGBPoint(scalar_range[0], 0, 0, 0)
# color_func.AddRGBPoint(641, 1, 1, 1)
color_func.AddRGBPoint(scalar_range[1], 1, 1, 1)

opacity_func = vtk.vtkPiecewiseFunction()
opacity_func.AddPoint(scalar_range[0], 0)
# opacity_func.AddPoint(641, 0.0)
opacity_func.AddPoint(scalar_range[1], 0.9)

# Create volume property
volume_property = vtk.vtkVolumeProperty()
volume_property.SetColor(color_func)
volume_property.SetScalarOpacity(opacity_func)
volume_property.ShadeOff()
volume_property.SetInterpolationTypeToLinear()

g_window = 1000
g_level = 500
g_opacity = 1
adjust_window_level(volume_property, g_window, g_level)

# Create volume mapper
volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
volume_mapper.SetBlendModeToComposite()
volume_mapper.SetInputConnection(reader.GetOutputPort())

# Create volume
volume = vtk.vtkVolume()
volume.SetMapper(volume_mapper)
volume.SetProperty(volume_property)

# Create renderer
renderer = vtk.vtkRenderer()
renderer.AddVolume(volume)
renderer.SetBackground(0, 0, 0)

cylinder_actor = create_cylinder_actor()
cylinder_actor.SetPosition(50, 50, -50)
renderer.AddActor(cylinder_actor)

# add axes to the renderer
axes = vtk.vtkAxesActor()
axes.SetTotalLength(10, 10, 10)
# set the text scale mode to none
axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
axes.GetXAxisCaptionActor2D().GetTextActor().SetHeight(0.02)
axes.GetYAxisCaptionActor2D().GetTextActor().SetHeight(0.02)
axes.GetZAxisCaptionActor2D().GetTextActor().SetHeight(0.02)
renderer.AddActor(axes)

renderer.SetUseDepthPeeling(1)
renderer.SetUseDepthPeelingForVolumes(1)

# Create render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(800, 800)

# Create render window interactor
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)


# Add keypress event
def keypress(obj, event):
    global g_window, g_level, g_opacity  # Declare g_window and g_level as global
    key = obj.GetKeySym()
    if key == "w":
        g_window = g_window + 20
        print("Window width increased, Width: ", g_window, " Level: ", g_level)
        volume_property = volume.GetProperty()
        scalar_range = volume_property.GetScalarOpacity(0).GetRange()
        print("Scalar range:", scalar_range)
        volume_property = adjust_window_level(volume_property, g_window, g_level)
        render_window.Render()
    elif key == "s":
        g_window = g_window - 20 if g_window > 20 else 20
        print("Window width decreased, Width: ", g_window, " Level: ", g_level)
        volume_property = volume.GetProperty()
        volume_property = adjust_window_level(volume_property, g_window, g_level)
        render_window.Render()
    elif key == "d":
        g_level = g_level - 20
        print("Window level decreased, Width: ", g_window, " Level: ", g_level)
        volume_property = volume.GetProperty()
        volume_property = adjust_window_level(volume_property, g_window, g_level)
        render_window.Render()
    elif key == "a":
        g_level = g_level + 20
        print("Window level increased, Width: ", g_window, " Level: ", g_level)
        volume_property = volume.GetProperty()
        volume_property = adjust_window_level(volume_property, g_window, g_level)
        render_window.Render()
    # Adjust volume opacity
    elif key == "o":
        g_opacity = g_opacity + 0.05 if g_opacity <= 0.95 else 1
        print("opacity: ", g_opacity)
        volume_property = volume.GetProperty()
        adjust_volume_opacity(volume_property, g_opacity)
        render_window.Render()
    elif key == "p":
        g_opacity = g_opacity - 0.05 if g_opacity > 0.05 else 0
        print("opacity: ", g_opacity)
        volume_property = volume.GetProperty()
        adjust_volume_opacity(volume_property, g_opacity)
        render_window.Render()


render_window_interactor.AddObserver("KeyPressEvent", keypress)

# Start the interaction
render_window.Render()
render_window_interactor.Start()
