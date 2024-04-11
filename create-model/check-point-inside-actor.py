import vtkmodules.all as vtk

# not working
def is_point_inside_actor_1(actor, point):
    # Get the polydata from the actor
    polydata = actor.GetMapper().GetInput()

    # Create a point locator for fast search
    point_locator = vtk.vtkPointLocator()
    point_locator.SetDataSet(polydata)
    point_locator.BuildLocator()

    # Check if the point is inside any of the cells (polygons)
    cell_id = vtk.mutable(0)
    sub_id = vtk.mutable(0)
    dist2 = vtk.mutable(0.0)
    inside = point_locator.FindClosestPoint(point, dist2, cell_id, sub_id)

    return inside != -1

# working, using vtkSelectEnclosedPoints, but (0 0.1 0) is not correct
def is_point_inside_actor_2(actor, point):
    # Create a vtkPoints object and add the point to it
    points = vtk.vtkPoints()
    points.InsertNextPoint(point)

    # Create a vtkPolyData to represent the point
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    # Use vtkSelectEnclosedPoints to check if the point is inside the actor
    select_enclosed = vtk.vtkSelectEnclosedPoints()
    select_enclosed.SetInputData(polydata)
    select_enclosed.SetSurfaceData(actor.GetMapper().GetInput())
    select_enclosed.Update()

    # Retrieve the status of the point (1 if inside, 0 if outside)
    return select_enclosed.IsInside(0)



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

check_point = [7.17, -7.07, 0]
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
is_inside = is_point_inside_actor_2(sphereActor1, check_point)
print("--- %s seconds ---" % (time.time() - start_time))
print('Is point inside sphereActor1:', is_inside)
is_inside = is_point_inside_actor_2(sphereActor2, check_point)
print('Is point inside sphereActor2:', is_inside)

# create append polydata filter to append actor1 and actor2
appendFilter = vtk.vtkAppendPolyData()
appendFilter.AddInputData(sphereActor1.GetMapper().GetInput())
appendFilter.AddInputData(sphereActor2.GetMapper().GetInput())
appendFilter.Update()

# Create vtkSelectEnclosedPoints filter
selector = vtk.vtkSelectEnclosedPoints()
selector.SetSurfaceData(appendFilter.GetOutput())

# Create a point set with the point to check
point_set = vtk.vtkPoints()
point_set.InsertNextPoint(check_point)
# Create a vtkPolyData to represent the point
polydata = vtk.vtkPolyData()
polydata.SetPoints(point_set)
selector.SetInputData(polydata)

# Update the filter
selector.Update()
is_inside = selector.IsInside(0)
print("points is in the side: ", is_inside)
# Check the output
output_points = selector.GetOutput()
num_points = output_points.GetNumberOfPoints()

if num_points > 0:
  print("Point is likely inside or on the surface of the actor, num_points:", num_points)
else:
  print("Point is likely outside the surface of the actor")

check_point_2 = [9.9, 0, 0]
start_time_2 = time.time()
point_set.Reset()
point_set.InsertNextPoint(check_point_2)
# polydata.SetPoints(point_set)
selector.Update()
is_inside = selector.IsInside(0)
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