import vtkmodules.all as vtk

# ! the vtkPointLocator only check the surface, if the point inside of actor, the result will be incorrect
# not working
def is_point_inside_actor_1(actor, point):
    # Get the polydata from the actor
    polydata = actor.GetMapper().GetInput()

    # Create a point locator for fast search
    point_locator = vtk.vtkPointLocator()
    point_locator.SetDataSet(polydata)
    point_locator.BuildLocator()

    # inside = point_locator.FindClosestPoint(point)
    dist2 = 0.0
    ref = vtk.reference(dist2)
    inside = point_locator.FindClosestPointWithinRadius(0.1, point, ref)
    print(f"closest point {inside}: , distance: {dist2}")

    return inside != -1

# working, using vtkSelectEnclosedPoints, but (0 0.1 0) is not correct
def is_point_inside_actor_2(polydata, point):
    # Create a point locator for fast search
    point_locator = vtk.vtkPointLocator()
    point_locator.SetDataSet(polydata)
    point_locator.BuildLocator()

    # inside = point_locator.FindClosestPoint(point)
    dist2 = 0.0
    ref = vtk.reference(dist2)
    inside = point_locator.FindClosestPointWithinRadius(0.1, point, ref)
    print(f"closest point {inside}: , distance: {dist2}")

    return inside != -1



radius = 10
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

resolution = 1000
opacity = 1
# Create two semi-spheres
sphereSource1 = vtk.vtkSphereSource()
sphereSource1.SetRadius(radius)
sphereSource1.SetPhiResolution(resolution)
sphereSource1.SetThetaResolution(resolution)
sphereSource1.SetStartTheta(0)
sphereSource1.SetEndTheta(180)
sphereSource1.Update()

sphereMapper1 = vtk.vtkPolyDataMapper()
sphereMapper1.SetInputConnection(sphereSource1.GetOutputPort())

sphereActor1 = vtk.vtkActor()
# sphereActor1.SetPosition(0, length/2, 0)
sphereActor1.SetMapper(sphereMapper1)
sphereActor1.GetProperty().SetColor(0, 0.3, 0.3)
sphereActor1.GetProperty().SetOpacity(opacity)

sphereSource2 = vtk.vtkSphereSource()
sphereSource2.SetRadius(radius)
sphereSource2.SetPhiResolution(resolution)
sphereSource2.SetThetaResolution(resolution)
sphereSource2.SetStartTheta(180)
sphereSource2.SetEndTheta(360)
sphereSource2.Update()

sphereMapper2 = vtk.vtkPolyDataMapper()
sphereMapper2.SetInputConnection(sphereSource2.GetOutputPort())

sphereActor2 = vtk.vtkActor()
sphereActor2.SetMapper(sphereMapper2)
# sphereActor2.SetPosition(0, -length/2, 0)
sphereActor2.GetProperty().SetColor(0.3, 0.3, 0)
sphereActor2.GetProperty().SetOpacity(opacity)

# create a point and add to render
point = vtk.vtkSphereSource()   
point.SetRadius(0.1)
point.SetPhiResolution(100)
point.SetThetaResolution(100)
point.Update()

pointMapper = vtk.vtkPolyDataMapper()
pointMapper.SetInputConnection(point.GetOutputPort())

pointActor = vtk.vtkActor()
pointActor.SetMapper(pointMapper)
pointActor.GetProperty().SetColor(0, 1, 0)
pointActor.GetProperty().SetOpacity(1)

check_point = [7.17, 7.107, 0]
# check_point = [0, 0.1, 0]
pointActor.SetPosition(check_point)

renderer = vtk.vtkRenderer()
# renderer.AddActor(tubeActor)
renderer.AddActor(sphereActor1)
renderer.AddActor(sphereActor2)
renderer.AddActor(pointActor)

# Add axes actor to scene
axes = vtk.vtkAxesActor()
# set axes axies length
axes.AxisLabelsOff()
axes.SetTotalLength(15, 15, 15)
renderer.AddActor(axes)


# Check if the point is inside the tube
# calculate the function run time
import time
start_time = time.time()
# is_inside = is_point_inside_actor_1(sphereActor1, check_point)
# print("--- %s seconds ---" % (time.time() - start_time))
# print('Is point inside sphereActor1:', is_inside)
# is_inside = is_point_inside_actor_1(sphereActor2, check_point)
# print('Is point inside sphereActor2:', is_inside)

# create append polydata filter to append actor1 and actor2
appendFilter = vtk.vtkAppendPolyData()
appendFilter.AddInputData(sphereActor1.GetMapper().GetInput())
appendFilter.AddInputData(sphereActor2.GetMapper().GetInput())
appendFilter.Update()

start_time = time.time()
is_inside = is_point_inside_actor_2(appendFilter.GetOutput(), check_point)
print("append filter --- %s seconds ---" % (time.time() - start_time))
print('Is point inside append polydata:', is_inside)

check_point_2 = [0, 7.107, 0]
start_time_2 = time.time()
is_inside = is_point_inside_actor_2(appendFilter.GetOutput(), check_point_2)
print("second --- %s seconds ---" % (time.time() - start_time_2))
print("points 2 is in the side: ", is_inside)


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