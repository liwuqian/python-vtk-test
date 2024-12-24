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

def set_volume_properties_default(volumeProperty):
    # Create color transfer function
    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.AddRGBPoint(-3024, 0, 0, 0)
    colorTransferFunction.AddRGBPoint(-16, 0.73, 0.25, 0.30)
    colorTransferFunction.AddRGBPoint(641, 0.90, 0.82, 0.56)
    colorTransferFunction.AddRGBPoint(3071, 1, 1, 1)

    # Create opacity transfer function
    opacityTransferFunction = vtk.vtkPiecewiseFunction()
    opacityTransferFunction.AddPoint(-3024, 0.0)
    opacityTransferFunction.AddPoint(-16, 0.0)
    opacityTransferFunction.AddPoint(641, 0.5)
    opacityTransferFunction.AddPoint(3071, 0.5)

    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)
    # volumeProperty.SetScalarOpacityUnitDistance(0, 4.5)  # Adjust as needed

def  readmhd(filename):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

def readmhdandvisualization(filename):
    # Create a reader for the MHD file
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(filename)
    reader.Update()
    # using set_volume_properties_default to viualize the image
    # image_data = reader.GetOutput()
    volumeProperty = vtk.vtkVolumeProperty()
    set_volume_properties_default(volumeProperty)
    # Create a mapper
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    # Create a volume
    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(volumeProperty)
    return volume

def readstl(filename):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

def set_depth_peeling(renderWindow, renderer):
    # Enable depth peeling
    # 1. Use a render window with alpha bits (as initial value is 0 (false)):
    renderWindow.SetAlphaBitPlanes(1)

    # 2. Force to not pick a framebuffer with a multisample buffer
    # (as initial value is 8):
    renderWindow.SetMultiSamples(0)

    # 3. Choose to use depth peeling (if supported) (initial value is 0 (false)):
    # If 
    renderer.SetUseDepthPeeling(1)
    renderer.SetUseDepthPeelingForVolumes(1)

    # 4. Set depth peeling parameters
    maxNoOfPeels = 100
    occlusionRatio = 0.1
    # - Set the maximum number of rendering passes (initial value is 4):
    renderer.SetMaximumNumberOfPeels(maxNoOfPeels)
    # - Set the occlusion ratio (initial value is 0.0, exact image):
    renderer.SetOcclusionRatio(occlusionRatio)

# custom style to implement the pan functionality using mouse move event
class myStyleTrackballActor(vtkInteractorStyleTrackballActor):
    def __init__(self):
        self.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)
        self.AddObserver("MouseMoveEvent", self.MouseMoveEvent)
        self.AddObserver("LeftButtonReleaseEvent", self.OnLeftButtonUp)
        # selected actor
        self.selectedActor = None
        self.trackballcam = False
    
    def OnLeftButtonDown(self, obj, event):
        # pick prop, volume actor can not be picked
        picker = vtk.vtkPropPicker()
        picker.Pick(self.GetInteractor().GetEventPosition()[0],
                    self.GetInteractor().GetEventPosition()[1],
                    0, self.GetDefaultRenderer())
        # check if pick actor
        if picker.GetActor() == None:
            self.selectedActor = None
            self.trackballcam = True
            return
        self.selectedActor = picker.GetActor()
        # print("Selected actor:", self.selectedActor)
        self.trackballcam = False
        # print("Left button down")
        return

    def MouseMoveEvent(self, obj, event):
        # check InteractionProp is not None
        if self.trackballcam :
            # trackball camera
            x, y = self.GetInteractor().GetEventPosition()
            x0, y0 = self.GetInteractor().GetLastEventPosition()
            win_size = self.GetDefaultRenderer().GetRenderWindow().GetSize()
            delta_elevation = -20.0 / win_size[1]
            delta_azimuth = -20.0 / win_size[0]
            motion_factor = 10.0
            rxf = (x - x0) * delta_azimuth * motion_factor
            ryf = (y - y0) * delta_elevation * motion_factor
            camera = self.GetDefaultRenderer().GetActiveCamera()
            camera.Azimuth(rxf)
            camera.Elevation(ryf)
            camera.OrthogonalizeViewUp()
            self.GetInteractor().GetRenderWindow().Render()
        if self.selectedActor != None:
            center = self.selectedActor.GetCenter()
            # compute center in display coordinates
            center_display = [0, 0, 0]
            self.ComputeWorldToDisplay(self.GetDefaultRenderer(), center[0], center[1], center[2], center_display)
            # print("Mouse move event")
            x, y = self.GetInteractor().GetEventPosition()
            x0, y0 = self.GetInteractor().GetLastEventPosition()
            old_pick_point_wrd = [0, 0, 0, 1]
            new_pick_point_wrd = [0, 0, 0, 1]
            self.ComputeDisplayToWorld(self.GetDefaultRenderer(), x0, y0, center_display[2], old_pick_point_wrd)
            self.ComputeDisplayToWorld(self.GetDefaultRenderer(), x, y, center_display[2], new_pick_point_wrd)
            motion_vector = [0, 0, 0]
            for i in range(3):
                motion_vector[i] = new_pick_point_wrd[i] - old_pick_point_wrd[i]
            motion_mouse = [x - x0, y - y0, 0]
            # print("motion vector:", motion_vector)
            # print("motion  mouse:", motion_mouse)
            # translate actor by the difference in mouse positions from the actor center
            # using user matrix
            transform = vtk.vtkTransform()
            transform.PostMultiply()
            # check if the actor has a user matrix
            if self.selectedActor.GetUserMatrix() != None:
                transform.SetMatrix(self.selectedActor.GetUserMatrix())
            # transform.Translate(x - x0, y - y0, 0)
            transform.Translate(motion_vector[0], motion_vector[1], motion_vector[2])
            self.selectedActor.SetUserTransform(transform)
            # render
            self.GetInteractor().GetRenderWindow().Render()
    
    def OnLeftButtonUp(self, obj, event):
        # set selected actor to None
        self.selectedActor = None
        self.trackballcam = False
        print("Left button up")


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

    style = myStyleTrackballActor()
    style.SetDefaultRenderer(ren)
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

    # add mhd volume
    filename = "data/origin.mhd"
    volume = readmhdandvisualization(filename)
    volume.PickableOff()
    ren.AddVolume(volume)

    # add axes to the renderer
    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(20, 20, 20)
    ren.AddActor(axes)

    set_depth_peeling(renWin, ren)

    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()


if __name__ == '__main__':
    main()