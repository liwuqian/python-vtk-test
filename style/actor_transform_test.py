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
    ren.SetBackground(colors.GetColor3d('PaleGoldenrod'))

    # add screw stl
    stl = readstl("data/36924050.stl")
    screwMapper = vtkPolyDataMapper()
    screwMapper.SetInputData(stl)
    screwActor = vtkActor()
    screwActor.SetMapper(screwMapper)
    screwActor.GetProperty().SetColor(colors.GetColor3d('Tomato'))
    screwActor.GetProperty().SetOpacity(0.8)
    # screwActor.SetPosition(0, -20, 0)
    screwActor.SetOrigin(0, 0, 0)
    # print origin
    print("screw actor origin:", screwActor.GetOrigin())
    print("screw actor position:", screwActor.GetPosition())
    print("screw actor center:", screwActor.GetCenter())
    ren.AddActor(screwActor)
    
    # roate the screw actor along the z-axis by 45 degrees using actor center as the pivot using vtkTransform
    origin = screwActor.GetOrigin()
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    center = screwActor.GetCenter()
    
    transform.Translate(-center[0], -center[1], -center[2])
    # transform.RotateWXYZ(45, 0, 0, 1)
    transform.RotateZ(45)
    transform.Translate(center[0], center[1], center[2])
    # transform.Translate(-origin[0], -origin[1], -origin[2])
    # transform.PreMultiply()
    # transform.Translate(origin[0], origin[1], origin[2])
    screwActor.SetUserMatrix(transform.GetMatrix())
    # screwActor.SetUserTransform(transform)
    center = screwActor.GetCenter()
    usermatrix = screwActor.GetUserMatrix()
    transform2 = vtk.vtkTransform()
    transform2.SetMatrix(usermatrix)
    transform2.PostMultiply()
    transform2.Translate(-center[0], -center[1], -center[2])
    transform2.RotateZ(45)
    transform2.Translate(center[0], center[1], center[2])
    screwActor.SetUserMatrix(transform2.GetMatrix())

    # add axes to the renderer
    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(20, 20, 20)
    ren.AddActor(axes)

    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()


if __name__ == '__main__':
    main()