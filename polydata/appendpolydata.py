import vtk

# Create a cylinder (pencil body)
cylinder = vtk.vtkCylinderSource()
cylinder.SetRadius(0.5)  # Thinner like a pencil
cylinder.SetHeight(5.0)  # Length of the pencil body
cylinder.SetResolution(50)
cylinder.Update()

# Create a cone (pencil tip)
cone = vtk.vtkConeSource()
cone.SetRadius(0.5)  # Same radius as the cylinder
cone.SetHeight(1.5)  # Sharpened tip should be smaller
cone.SetResolution(50)
cone.Update()

# Transform the cone to place its base on top of the cylinder
transform = vtk.vtkTransform()
# transform.RotateZ(90)
transform.Translate(0, cylinder.GetHeight() / 2 + cone.GetHeight() / 2, 0)  # Move it up
transform.RotateZ(90)  # Rotate it to place the base on top

transformFilter = vtk.vtkTransformPolyDataFilter()
transformFilter.SetTransform(transform)
transformFilter.SetInputConnection(cone.GetOutputPort())
transformFilter.Update()

# Append both cylinder and cone
appendFilter = vtk.vtkAppendPolyData()
appendFilter.AddInputData(cylinder.GetOutput())  # Add cylinder
appendFilter.AddInputData(transformFilter.GetOutput())  # Add transformed cone
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
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# Add the actor to the renderer
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.1, 0.1)  # Dark background

# Add axes to the renderer
axes = vtk.vtkAxesActor()
axes.SetTotalLength(10, 10, 10)
renderer.AddActor(axes)

# Render and start interaction
renderWindow.Render()
interactor.Start()
