import vtkmodules.all as vtk

# Create a circle
circleSource = vtk.vtkRegularPolygonSource()
circleSource.SetNumberOfSides(50)  # Set the number of sides of the polygon (more sides means smoother circle)
circleSource.SetRadius(5.0)  # Set the radius of the circle
circleSource.SetCenter(0.0, 0.0, 0.0)  # Set the center of the circle
circleSource.GeneratePolygonOff() # Disable polygon surface

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(circleSource.GetOutputPort())

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
# renderer.SetBackground(1, 1, 1)  # Set the background color to white

# Create a render window
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 800)

# Create an interactor
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Start the interaction
renderWindow.Render()
renderWindowInteractor.Start()
