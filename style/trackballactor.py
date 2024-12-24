#!/usr/bin/env python
import vtkmodules.all as vtk

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

def readstl(filename):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

def main():
    colors = vtkNamedColors()

    # create a rendering window and renderer
    ren = vtkRenderer()
    renWin = vtkRenderWindow()
    renWin.SetPosition(300, 300)
    renWin.SetSize(800, 600)
    renWin.AddRenderer(ren)
    renWin.SetWindowName('InteractorStyleTrackballActor')

    # create a renderwindowinteractor
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    style = vtkInteractorStyleTrackballActor()
    iren.SetInteractorStyle(style)

    # create source
    sphereSource = vtkSphereSource()
    sphereSource.SetCenter(30.0, 0.0, 0.0)
    sphereSource.SetRadius(10.0)

    # mapper
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())

    # actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Chartreuse'))
    print('sphere actor origin:', actor.GetOrigin())
    print('sphere actor position:', actor.GetPosition())
    print('sphere actor center:', actor.GetCenter())

    # assign actor to the renderer
    ren.AddActor(actor)
    ren.SetBackground(colors.GetColor3d('PaleGoldenrod'))

    # add cone actor
    cone = vtk.vtkConeSource()
    cone.SetResolution(50)
    cone.SetHeight(30)
    cone.SetRadius(10)
    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())
    coneActor = vtk.vtkActor()
    coneActor.SetMapper(coneMapper)
    coneActor.GetProperty().SetColor(colors.GetColor3d('Tomato'))
    coneActor.GetProperty().SetOpacity(0.9)
    coneActor.SetPosition(-30, 0, 0)
    ren.AddActor(coneActor)

    # add screw stl
    stl = readstl("data/36924050.stl")
    screwMapper = vtkPolyDataMapper()
    screwMapper.SetInputData(stl)
    screwActor = vtkActor()
    screwActor.SetMapper(screwMapper)
    screwActor.GetProperty().SetColor(colors.GetColor3d('Tomato'))
    screwActor.GetProperty().SetOpacity(0.9)
    # screwActor.SetPosition(0, -20, 0)
    # screwActor.SetOrigin(0, -20, 0)
    # print origin
    print("screw actor origin:", screwActor.GetOrigin())
    print("screw actor position:", screwActor.GetPosition())
    print("screw actor center:", screwActor.GetCenter())
    ren.AddActor(screwActor)

    # add axes to the renderer
    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(10, 10, 10)
    ren.AddActor(axes)

    ren.GetActiveCamera().SetParallelProjection(True)
    # set camera look from y-axis
    # ren.GetActiveCamera().SetPosition(0, -100, 0)
    # ren.GetActiveCamera().SetFocalPoint(0, 0, 0)
    # ren.GetActiveCamera().SetViewUp(0, 0, 1)
    # ren.ResetCamera()

    # set camera tilt 45 degrees
    ren.GetActiveCamera().Azimuth(45)
    ren.GetActiveCamera().Elevation(45)
    ren.ResetCamera()

    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()


if __name__ == '__main__':
    main()