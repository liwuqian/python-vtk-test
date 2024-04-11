import vtk

radius = 5
length = 10
# Create a tube
tubeSource = vtk.vtkLineSource()
tubeSource.SetPoint1(0, -length/2, 0)
tubeSource.SetPoint2(0, length/2, 0)
tubeSource.SetResolution(100)
tubeSource.Update()

# Create a tube filter
tubeFilter = vtk.vtkTubeFilter()
tubeFilter.SetInputConnection(tubeSource.GetOutputPort())
tubeFilter.SetRadius(radius)
tubeFilter.SetNumberOfSides(50)
tubeFilter.Update()

tubeMapper = vtk.vtkPolyDataMapper()
tubeMapper.SetInputConnection(tubeFilter.GetOutputPort())

tubeActor = vtk.vtkActor()
tubeActor.SetMapper(tubeMapper)
tubeActor.GetProperty().SetColor(1, 1, 1)
tubeActor.GetProperty().SetOpacity(0.8)

# Create two semi-spheres
sphereSource1 = vtk.vtkSphereSource()
sphereSource1.SetRadius(radius)
sphereSource1.SetPhiResolution(100)
sphereSource1.SetThetaResolution(100)
sphereSource1.SetStartTheta(0)
sphereSource1.SetEndTheta(180)
sphereSource1.Update()

sphereMapper1 = vtk.vtkPolyDataMapper()
sphereMapper1.SetInputConnection(sphereSource1.GetOutputPort())

sphereActor1 = vtk.vtkActor()
sphereActor1.SetPosition(0, length/2, 0)
sphereActor1.SetMapper(sphereMapper1)
sphereActor1.GetProperty().SetColor(0, 0, 1)
sphereActor1.GetProperty().SetOpacity(0.8)

sphereSource2 = vtk.vtkSphereSource()
sphereSource2.SetRadius(radius)
sphereSource2.SetPhiResolution(100)
sphereSource2.SetThetaResolution(100)
sphereSource2.SetStartTheta(180)
sphereSource2.SetEndTheta(360)
sphereSource2.Update()

sphereMapper2 = vtk.vtkPolyDataMapper()
sphereMapper2.SetInputConnection(sphereSource2.GetOutputPort())

sphereActor2 = vtk.vtkActor()
sphereActor2.SetMapper(sphereMapper2)
sphereActor2.SetPosition(0, -length/2, 0)
sphereActor2.GetProperty().SetColor(1, 0, 0)
sphereActor2.GetProperty().SetOpacity(0.8)

# Create a renderer and add the actors
renderer = vtk.vtkRenderer()
renderer.AddActor(tubeActor)
renderer.AddActor(sphereActor1)
renderer.AddActor(sphereActor2)

# Add axes actor to scene
axes = vtk.vtkAxesActor()
# set axes axies length
axes.AxisLabelsOff()
axes.SetTotalLength(10, 10, 10)
renderer.AddActor(axes)

# Create a render window and set the renderer
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetPosition(800, 500)
renderWindow.SetSize(600, 600)

# Create an interactor and set the render window
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# Start the interactor
interactor.Initialize()
interactor.Start()