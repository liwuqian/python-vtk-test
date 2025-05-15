import vtkmodules.all as vtk

# Create points along a line
points = vtk.vtkPoints()
num_dots = 20
spacing = 0.05

for i in range(num_dots):
    points.InsertNextPoint(i * spacing, 0, 0)

# Create a polydata to store the points
polydata = vtk.vtkPolyData()
polydata.SetPoints(points)

# Create a small sphere to represent each dot
sphere = vtk.vtkSphereSource()
sphere.SetRadius(0.01)
sphere.SetThetaResolution(8)
sphere.SetPhiResolution(8)

# Use vtkGlyph3DMapper to copy the sphere to each point
glyph_mapper = vtk.vtkGlyph3DMapper()
glyph_mapper.SetInputData(polydata)
glyph_mapper.SetSourceConnection(sphere.GetOutputPort())

# Create an actor for the glyphs
actor = vtk.vtkActor()
actor.SetMapper(glyph_mapper)

# Set up renderer and window
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.3)

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

render_window.Render()
interactor.Start()
