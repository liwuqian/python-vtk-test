# input many points and draw connected segment lines
import vtkmodules.all as vtk

def create_line(points):
    # Create a vtkPoints object and store the points in it
    points_vtk = vtk.vtkPoints()
    for p in points:
        points_vtk.InsertNextPoint(p)
    # Create a cell array to store the lines in and add the lines to it
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(len(points))
    for i in range(len(points)):
        lines.InsertCellPoint(i)
    # Create a polydata to store everything in
    polydata = vtk.vtkPolyData()
    # Add the points to the dataset
    polydata.SetPoints(points_vtk)
    # Add the lines to the dataset
    polydata.SetLines(lines)
    return polydata

def main():
    colors = vtk.vtkNamedColors()

    # Create a set of points
    points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]
    polydata = create_line(points)

    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetLineWidth(4)
    actor.GetProperty().SetColor(colors.GetColor3d('Tomato'))

    # Create a renderer
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('PaleGoldenrod'))

    # Create a render window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetWindowName('MultiPointLine')
    renderWindow.AddRenderer(renderer)

    # Create a render window interactor
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # Add the actor to the scene
    renderer.AddActor(actor)

    # Render and interact
    renderWindow.Render()
    renderWindow.SetWindowName('MultiPointLine')
    renderWindow.Render()
    renderWindowInteractor.Start()

if __name__ == '__main__':
    main()