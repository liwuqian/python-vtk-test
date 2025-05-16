import vtkmodules.all as vtk

radius = 1
cylinder_height = 8
cone_height = 3
# Create a cylinder (pencil body)
cylinder = vtk.vtkCylinderSource()
cylinder.SetRadius(radius)  # Thinner like a pencil
cylinder.SetHeight(cylinder_height)  # Length of the pencil body
cylinder.SetResolution(50)
cylinder.SetCenter(0, -cylinder_height*0.5, 0)  # Center the cylinder at the origin
cylinder.Update()

# Create a mapper for the cylinder
cylinderMapper = vtk.vtkPolyDataMapper()
cylinderMapper.SetInputConnection(cylinder.GetOutputPort())
cylinderActor = vtk.vtkActor()
cylinderActor.SetMapper(cylinderMapper)

# Create a cone (pencil tip)
cone = vtk.vtkConeSource()
cone.SetRadius(radius)  # Same radius as the cylinder
cone.SetHeight(cone_height)  # Sharpened tip should be smaller
cone.SetResolution(50)
cone.SetDirection(0, -1, 0)
cone.SetCenter(0, -cylinder_height - cone_height*0.5, 0)  # Center the cone at the origin
cone.Update()

# Create a mapper for the cone
coneMapper = vtk.vtkPolyDataMapper()
coneMapper.SetInputConnection(cone.GetOutputPort())
coneActor = vtk.vtkActor()
coneActor.SetMapper(coneMapper)


# Append both cylinder and cone
appendFilter = vtk.vtkAppendPolyData()
appendFilter.AddInputData(cylinder.GetOutput())  # Add cylinder
appendFilter.AddInputData(cone.GetOutput())  # Add transformed cone
appendFilter.Update()

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(appendFilter.GetOutput())

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 600)  # Set the window size
renderWindow.SetPosition(200, 200)  # Set the window position
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# Add the actor to the renderer
# renderer.AddActor(cylinderActor)
# renderer.AddActor(coneActor)
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.1, 0.1)  # Dark background

# Add axes to the renderer
axes = vtk.vtkAxesActor()
axes.SetTotalLength(10, 10, 10)
renderer.AddActor(axes)

# Render and start interaction
renderWindow.Render()
interactor.Start()
