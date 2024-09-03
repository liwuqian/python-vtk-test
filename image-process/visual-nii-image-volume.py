import vtkmodules.all as vtk

# Read the NIFTI file (.nii.gz)
reader = vtk.vtkNIFTIImageReader()
reader.SetFileName("data/liver_57.nii.gz")
reader.Update()

# Set up the volume mapper
volume_mapper = vtk.vtkSmartVolumeMapper()
volume_mapper.SetInputConnection(reader.GetOutputPort())

# Set up the volume property
volume_property = vtk.vtkVolumeProperty()
volume_property.ShadeOn()
volume_property.SetInterpolationTypeToLinear()

# Set up color and opacity transfer functions
color_func = vtk.vtkColorTransferFunction()
color_func.AddRGBPoint(0, 0.0, 0.0, 0.0)
color_func.AddRGBPoint(500, 1.0, 0.5, 0.3)
color_func.AddRGBPoint(1000, 1.0, 0.5, 0.3)
color_func.AddRGBPoint(1150, 1.0, 1.0, 0.9)

opacity_func = vtk.vtkPiecewiseFunction()
opacity_func.AddPoint(0, 0.00)
opacity_func.AddPoint(500, 0.15)
opacity_func.AddPoint(1000, 0.15)
opacity_func.AddPoint(1150, 0.85)

volume_property.SetColor(color_func)
volume_property.SetScalarOpacity(opacity_func)

# Set up the volume actor
volume = vtk.vtkVolume()
volume.SetMapper(volume_mapper)
volume.SetProperty(volume_property)

# Set up the renderer, render window, and interactor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Add the volume to the renderer
renderer.AddVolume(volume)
renderer.SetBackground(0, 0, 0)  # Set the background color to black

# Initialize and start the rendering loop
render_window.Render()
interactor.Start()
