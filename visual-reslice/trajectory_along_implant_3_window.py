import vtkmodules.all as vtk
import numpy as np
import threading


def load_mhd_file(file_path):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(file_path)
    reader.Update()
    return reader.GetOutput()


def create_reslice_matrix_from_transform(transform, axis):
    # Create a reslice axes matrix aligned to the implant's local axes
    m = transform.GetMatrix()
    axes = vtk.vtkMatrix4x4()
    for i in range(3):
        for j in range(3):
            axes.SetElement(i, j, m.GetElement(i, j))
        axes.SetElement(i, 3, m.GetElement(i, 3))

    # Select which axis to align as view direction (X=0, Y=1, Z=2)
    permute = [0, 1, 2]
    if axis == 0:  # X view
        permute = [1, 2, 0]
    elif axis == 1:  # Y view
        permute = [2, 0, 1]
    elif axis == 2:  # Z view
        permute = [0, 1, 2]

    # Create new axes with permuted directions
    new_axes = vtk.vtkMatrix4x4()
    for i in range(3):
        for j in range(3):
            new_axes.SetElement(i, j, axes.GetElement(i, permute[j]))
        new_axes.SetElement(i, 3, axes.GetElement(i, 3))
    return new_axes


def apply_window_level(reslice_output, window, level):
    color_map = vtk.vtkImageMapToWindowLevelColors()
    color_map.SetInputConnection(reslice_output.GetOutputPort())
    color_map.SetWindow(window)
    color_map.SetLevel(level)
    color_map.Update()
    return color_map


def create_cylinder_actor():
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetRadius(5)
    cylinder.SetHeight(100)
    cylinder.SetResolution(50)
    cylinder.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cylinder.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.9, 0.7, 0.3)
    return actor


def apply_reslice_transform_to_actor(actor, reslice_matrix, implant_matrix):
    inverse_reslice = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Invert(reslice_matrix, inverse_reslice)

    final_matrix = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(inverse_reslice, implant_matrix, final_matrix)

    actor.SetUserMatrix(final_matrix)


class View:
    def __init__(self, image_data, implant_transform, axis, title):
        self.image_data = image_data
        self.implant_transform = implant_transform
        self.axis = axis
        self.title = title

        self.reslice = vtk.vtkImageReslice()
        self.reslice.SetInputData(image_data)
        self.reslice.SetOutputDimensionality(2)
        self.reslice.SetInterpolationModeToLinear()
        self.reslice.SetOutputSpacing(1.0, 1.0, 1.0)

        self.implant_actor = create_cylinder_actor()
        self.color_map = apply_window_level(self.reslice, window=400, level=40)

        self.image_actor = vtk.vtkImageActor()
        self.image_actor.GetMapper().SetInputConnection(self.color_map.GetOutputPort())

        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(self.image_actor)
        self.renderer.AddActor(self.implant_actor)
        self.renderer.SetBackground(0.1, 0.1, 0.1)

        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(600, 600)
        self.render_window.SetWindowName(title)

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        self.interactor.AddObserver("KeyPressEvent", self.keypress_callback)

        self.renderer.GetActiveCamera().SetParallelProjection(True)

        self.update_reslice()
        self.renderer.ResetCamera()

    def update_reslice(self):
        new_reslice_matrix = create_reslice_matrix_from_transform(self.implant_transform, self.axis)
        self.reslice.SetResliceAxes(new_reslice_matrix)
        self.reslice.Update()
        self.color_map.Update()
        apply_reslice_transform_to_actor(
            self.implant_actor,
            new_reslice_matrix,
            self.implant_transform.GetMatrix()
        )

    def keypress_callback(self, obj, event):
        key = obj.GetKeySym()
        ctrl = obj.GetControlKey()
        # print(f"Key pressed: {key}, Ctrl: {ctrl}")

        if key == 'w':
            self.implant_transform.Translate(0, 1, 0)
        elif key == 's':
            self.implant_transform.Translate(0, -1, 0)
        elif key == 'a':
            self.implant_transform.Translate(-1, 0, 0)
        elif key == 'd':
            self.implant_transform.Translate(1, 0, 0)
        elif key == 'Up':
            self.implant_transform.Translate(0, 0, -1)
        elif key == 'Down':
            self.implant_transform.Translate(0, 0, 1)

        # Rotation with ctrl for inverse
        elif key in ('x', 'y', 'z'):
            center = self.implant_transform.GetPosition()
            axis = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]}[key]
            angle = -5 if ctrl else 5
            self.implant_transform.Translate(-center[0], -center[1], -center[2])
            self.implant_transform.RotateWXYZ(angle, *axis)
            self.implant_transform.Translate(center[0], center[1], center[2])

        self.update_reslice()
        self.render_window.Render()

    def start(self):
        self.render_window.Render()
        self.interactor.Start()


class ViewManager:
    def __init__(self, image_data):
        self.implant_transform = vtk.vtkTransform()
        self.implant_transform.PostMultiply()
        self.implant_transform.Translate(image_data.GetCenter())

        self.views = [
            View(image_data, self.implant_transform, 0, "Trajectory 1 - X"),
            View(image_data, self.implant_transform, 1, "Trajectory 2 - Y"),
            View(image_data, self.implant_transform, 2, "Trajectory 3 - Z"),
        ]

    def start_all(self):
        # threads = []
        for view in self.views:
            view.start()
        #     thread = threading.Thread(target=view.start)
        #     thread.start()
        #     threads.append(thread)
        # for thread in threads:
        #     thread.join()


if __name__ == "__main__":
    image = load_mhd_file("data/L1.mhd")  # Update this path to your MHD file
    manager = ViewManager(image)
    manager.start_all()
