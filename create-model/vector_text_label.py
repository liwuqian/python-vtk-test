import vtkmodules.all as vtk

# Create the renderer
renderer = vtk.vtkRenderer()

# Create the render window
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# Create the render window interactor
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Create the text source
textSource = vtk.vtkVectorText()
textSource.SetText("World Label")

# Create a mapper for the text
textMapper = vtk.vtkPolyDataMapper()
textMapper.SetInputConnection(textSource.GetOutputPort())

# Create a follower to keep the text facing the camera
textActor = vtk.vtkFollower()
textActor.SetMapper(textMapper)
textActor.SetScale(0.1, 0.1, 0.1)  # Adjust the scale to fit the scene
textActor.SetPosition(1.0, 1.0, 0.0)  # Position in world coordinates

# Add the text actor to the renderer
renderer.AddActor(textActor)

axes = vtk.vtkAxesActor()
renderer.AddActor(axes)

# Set the camera to follow the text actor
textActor.SetCamera(renderer.GetActiveCamera())

renderer.ResetCamera()

# Initialize and start the render window interactor
renderWindow.Render()
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()
