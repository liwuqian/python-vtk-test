import vtkmodules.all as vtk

# Create a set of short line segments to simulate a dotted line
points = vtk.vtkPoints()
lines = vtk.vtkCellArray()

num_dots = 20
segment_length = 0.01
spacing = 0.05

for i in range(num_dots):
    p1 = [i * spacing, 0, 0]
    p2 = [i * spacing + segment_length, 0, 0]

    id1 = points.InsertNextPoint(p1)
    id2 = points.InsertNextPoint(p2)

    line = vtk.vtkLine()
    line.GetPointIds().SetId(0, id1)
    line.GetPointIds().SetId(1, id2)
    lines.InsertNextCell(line)

# Create polydata for the line segments
polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.SetLines(lines)

# Create a mapper and actor
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(polydata)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1, 1, 0)  # Yellow
actor.GetProperty().SetLineWidth(2.0)

# Set up rendering
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.1, 0.1)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

render_window.Render()
interactor.Start()
