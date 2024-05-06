import vtkmodules.all as vtk

# Define the path to your MHD file
mhd_file_path = "data/decompressionvolume.mhd"

# Create a reader for the MHD file
reader = vtk.vtkMetaImageReader()
reader.SetFileName(mhd_file_path)
reader.Update()

# Get the output of the reader
image_data = vtk.vtkImageData
image_data = reader.GetOutput()

# Create a mapper
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(image_data)

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(1, 1, 1)  # Set background to white

axes = vtk.vtkAxesActor()
renderer.AddActor(axes)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create an interactor
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Start the rendering loop
render_window.Render()
render_window_interactor.Start()
