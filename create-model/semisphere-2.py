import vtk

# Create a sphere source
sphereSource = vtk.vtkSphereSource()
sphereSource.SetRadius(1.0)
sphereSource.SetThetaResolution(100)
sphereSource.SetPhiResolution(100)
sphereSource.SetCenter(0, 0, 0)
sphereSource.Update()

# transform sphere source using transform filter
transform = vtk.vtkTransform()
# transform.Scale(1, 2, 3)
transform.Translate(0, 0, 0)
transformFilter = vtk.vtkTransformPolyDataFilter()
transformFilter.SetInputConnection(sphereSource.GetOutputPort())
transformFilter.SetTransform(transform)
transformFilter.Update()

# Create a clip filter to cut the sphere in half
clipFilter = vtk.vtkClipPolyData()
clipFilter.SetInputConnection(transformFilter.GetOutputPort())
clipFilter.SetClipFunction(vtk.vtkPlane())
clipFilter.GetClipFunction().SetNormal(-1, 0, 0)
clipFilter.GetClipFunction().SetOrigin(0, 0, 0)
clipFilter.Update()

# Create a mapper and actor for the clipped sphere
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(clipFilter.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# create pipeline for second sphere
sphereSource2 = vtk.vtkSphereSource()
sphereSource2.SetRadius(1.0)
sphereSource2.SetThetaResolution(100)
sphereSource2.SetPhiResolution(100)
sphereSource2.SetCenter(0, 0, 0)
sphereSource2.Update()

# transform sphere source using transform filter
transform2 = vtk.vtkTransform()
transform2.Translate(0, 0, 0)
transformFilter2 = vtk.vtkTransformPolyDataFilter()
transformFilter2.SetInputConnection(sphereSource2.GetOutputPort())
transformFilter2.SetTransform(transform2)
transformFilter2.Update()

# Create a clip filter to cut the sphere in half
clipFilter2 = vtk.vtkClipPolyData()
clipFilter2.SetInputConnection(transformFilter2.GetOutputPort())
clipFilter2.SetClipFunction(vtk.vtkPlane())
clipFilter2.GetClipFunction().SetNormal(1, 0, 0)
clipFilter2.GetClipFunction().SetOrigin(0, 0, 0)
clipFilter2.Update()

# Create a mapper and actor for the clipped sphere
mapper2 = vtk.vtkPolyDataMapper()
mapper2.SetInputConnection(clipFilter2.GetOutputPort())

actor2 = vtk.vtkActor()
actor2.SetMapper(mapper2)



# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# Add axes actor to scene
axes = vtk.vtkAxesActor()
renderer.AddActor(axes)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# Add the actor to the renderer and set the background color
renderer.AddActor(actor)
renderer.AddActor(actor2)
renderer.SetBackground(0.2, 0.3, 0.4)
renderer.ResetCamera()

# Set camera position and focal point
camera = renderer.GetActiveCamera()


# Start the interactor
interactor.Initialize()
renderWindow.Render()
interactor.Start()