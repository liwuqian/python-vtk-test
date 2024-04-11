import vtk

# Create a sphere
sphereSource = vtk.vtkSphereSource()
sphereSource.SetCenter(0, 0, 0)  # Set the center of the sphere
sphereSource.SetRadius(0.5)       # Set the radius of the sphere

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(sphereSource.GetOutputPort())

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.SetPosition(1, 0, 0)  # Set the position of the actor
# actor.SetOrigin(1, 0, 0)     # Set the origin of the actor

# create a cylinder
cylinder = vtk.vtkCylinderSource()
cylinder.SetCenter(0, 0, 0)
cylinder.SetRadius(0.5)
cylinder.SetHeight(1)
cylinder.SetResolution(100)

# Create a mapper
cylinderMapper = vtk.vtkPolyDataMapper()
cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

# Create an actor
cylinderActor = vtk.vtkActor()
cylinderActor.SetMapper(cylinderMapper)
cylinderActor.SetPosition(1, 1, 0)
# cylinderActor.SetOrigin(0, 1, 0)

# Rotate the actor by using user matrix
transform = vtk.vtkTransform()
transform.RotateZ(90)
transform.Translate(1, 0, 0)
print(transform.GetMatrix())
actor.SetUserTransform(transform)
cylinderActor.SetUserTransform(transform)

# create a tube
tube = vtk.vtkTubeFilter()
# source using two points
source = vtk.vtkLineSource()
source.SetPoint1(1, 1, 0)
source.SetPoint2(1, 2, 0)
tube.SetInputConnection(source.GetOutputPort())
tube.SetRadius(0.1)
tube.SetNumberOfSides(50)

# Create a mapper
tubeMapper = vtk.vtkPolyDataMapper()
tubeMapper.SetInputConnection(tube.GetOutputPort())

# Create an actor
tubeActor = vtk.vtkActor()
tubeActor.SetMapper(tubeMapper)
print('tubeActor.GetPosition():', tubeActor.GetPosition())


# Create a renderer
renderer = vtk.vtkRenderer()

# Add the actor to the scene
renderer.AddActor(actor)
renderer.AddActor(cylinderActor)
renderer.AddActor(tubeActor)

# Add axes actor to scene
axes = vtk.vtkAxesActor()
renderer.AddActor(axes)

# Create a render window
renderWindow = vtk.vtkRenderWindow()

# Add the renderer to the render window
renderWindow.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# Start the rendering process
renderWindow.Render()
interactor.Start()
