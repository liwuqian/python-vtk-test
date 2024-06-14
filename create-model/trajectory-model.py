import vtkmodules.all as vtk

# Create a cylinder source
cylinder = vtk.vtkCylinderSource()
height = 10
cylinder.SetRadius(0.5)
cylinder.SetHeight(height)
cylinder.SetCenter(0, -height/2, 0)
cylinder.SetResolution(100)

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cylinder.GetOutputPort())

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.2, 0.3, 0.4)

# Add a axes actor
axes = vtk.vtkAxesActor()
renderer.AddActor(axes)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Start the interactor
interactor.Initialize()
interactor.Start()