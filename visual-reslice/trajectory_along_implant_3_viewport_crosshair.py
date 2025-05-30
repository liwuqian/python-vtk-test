import vtkmodules.all as vtk


def load_mhd_file(file_path):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(file_path)
    reader.Update()
    return reader.GetOutput()


def create_reslice_matrix_from_transform(transform, axis):
    m = transform.GetMatrix()
    axes = vtk.vtkMatrix4x4()
    for i in range(3):
        for j in range(3):
            axes.SetElement(i, j, m.GetElement(i, j))
        axes.SetElement(i, 3, m.GetElement(i, 3))

    permute = [0, 1, 2]
    if axis == 0:
        permute = [1, 2, 0]
    elif axis == 1:
        permute = [2, 0, 1]
    elif axis == 2:
        permute = [0, 1, 2]

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
    def __init__(self, image_data, implant_transform, axis, viewport, render_window):
        self.image_data = image_data
        self.implant_transform = implant_transform
        self.axis = axis
        self.viewport = viewport
        self.render_window = render_window

        self.reslice = vtk.vtkImageReslice()
        self.reslice.SetInputData(image_data)
        self.reslice.SetOutputDimensionality(2)
        self.reslice.SetInterpolationModeToLinear()

        self.color_map = apply_window_level(self.reslice, window=400, level=40)

        self.image_actor = vtk.vtkImageActor()
        self.image_actor.GetMapper().SetInputConnection(self.color_map.GetOutputPort())

        self.implant_actor = create_cylinder_actor()

        self.renderer = vtk.vtkRenderer()
        self.renderer.SetViewport(*viewport)
        self.renderer.SetBackground(0.1, 0.1, 0.1)
        self.renderer.AddActor(self.image_actor)
        self.renderer.AddActor(self.implant_actor)
        self.renderer.GetActiveCamera().SetParallelProjection(True)

        self.render_window.AddRenderer(self.renderer)

        self.crosshair_lines = [vtk.vtkActor(), vtk.vtkActor()]
        for actor in self.crosshair_lines:
            actor.GetProperty().SetLineWidth(2)
            self.renderer.AddActor(actor)

        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        self.crosshair_lines[0].GetProperty().SetColor(colors[(self.axis + 1) % 3])
        self.crosshair_lines[1].GetProperty().SetColor(colors[(self.axis + 2) % 3])

        self.update_reslice()
        self.renderer.ResetCamera()

    def update_reslice(self):
        def get_in_plane_vectors(implant_matrix, new_reslice_matrix, axis):
            inverse = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Invert(new_reslice_matrix, inverse)
            dicom_v1 = [implant_matrix.GetElement(0, (axis + 1) % 3),
                        implant_matrix.GetElement(1, (axis + 1) % 3),
                        implant_matrix.GetElement(2, (axis + 1) % 3)]
            dicom_v2 = [implant_matrix.GetElement(0, (axis + 2) % 3),
                        implant_matrix.GetElement(1, (axis + 2) % 3),
                        implant_matrix.GetElement(2, (axis + 2) % 3)]
            # print("dicom_v1:", dicom_v1, "dicom_v2:", dicom_v2)
            # convert direction vectors to reslice space, [0.0] is to avoid origin translation
            v1 = list(inverse.MultiplyDoublePoint(dicom_v1 + [0.0]))[:3]
            v2 = list(inverse.MultiplyDoublePoint(dicom_v2 + [0.0]))[:3]
            # print("axis:", axis, "v1:", v1, "v2:", v2)
            # normalize vectors
            v1_length = vtk.vtkMath.Norm(v1)
            v2_length = vtk.vtkMath.Norm(v2)
            if v1_length > 0:
                v1 = [x / v1_length for x in v1]
            if v2_length > 0:
                v2 = [x / v2_length for x in v2]
            # print("normalized v1:", v1, "v2:", v2)
            return v1, v2

        def transform_point_to_reslice_space(point, reslice_matrix):
            inverse = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Invert(reslice_matrix, inverse)
            p = list(inverse.MultiplyDoublePoint(list(point) + [1.0]))[:3]
            return p

        def build_line_actor(p, direction, length=100):
            line = vtk.vtkLineSource()
            d = [length * x for x in direction]
            line.SetPoint1(p[0] - d[0], p[1] - d[1], p[2] - d[2])
            line.SetPoint2(p[0] + d[0], p[1] + d[1], p[2] + d[2])
            line.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(line.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            return actor

        new_reslice_matrix = create_reslice_matrix_from_transform(self.implant_transform, self.axis)
        self.reslice.SetResliceAxes(new_reslice_matrix)
        self.reslice.Update()
        self.color_map.Update()
        apply_reslice_transform_to_actor(
            self.implant_actor,
            new_reslice_matrix,
            self.implant_transform.GetMatrix()
        )

        center_world = self.implant_transform.GetPosition()
        center_reslice = transform_point_to_reslice_space(center_world, new_reslice_matrix)
        v1, v2 = get_in_plane_vectors(self.implant_transform.GetMatrix(), new_reslice_matrix, self.axis)
        # print("axis:", self.axis, "center:", center_reslice, "v1:", v1, "v2:", v2)

        self.crosshair_lines[0].SetMapper(build_line_actor(center_reslice, v1).GetMapper())
        self.crosshair_lines[1].SetMapper(build_line_actor(center_reslice, v2).GetMapper())


class ViewManager:
    def __init__(self, image_data):
        self.implant_transform = vtk.vtkTransform()
        self.implant_transform.PostMultiply()
        self.implant_transform.Translate(image_data.GetCenter())

        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetSize(1800, 600)
        self.render_window.SetWindowName("Multi-View Reslice Viewer")

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)

        self.views = [
            View(image_data, self.implant_transform, 0, (0.0, 0.0, 0.33, 1.0), self.render_window),
            View(image_data, self.implant_transform, 1, (0.33, 0.0, 0.66, 1.0), self.render_window),
            View(image_data, self.implant_transform, 2, (0.66, 0.0, 1.0, 1.0), self.render_window),
        ]

        self.interactor.AddObserver("KeyPressEvent", self.keypress_callback)

    def keypress_callback(self, obj, event):
        key = obj.GetKeySym()
        ctrl = obj.GetControlKey()

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

        elif key in ('x', 'y', 'z'):
            center = self.implant_transform.GetPosition()
            axis = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]}[key]
            angle = -5 if ctrl else 5
            self.implant_transform.Translate(-center[0], -center[1], -center[2])
            self.implant_transform.RotateWXYZ(angle, *axis)
            self.implant_transform.Translate(center[0], center[1], center[2])

        for view in self.views:
            view.update_reslice()
        self.render_window.Render()

    def start(self):
        self.render_window.Render()
        self.interactor.Start()


if __name__ == "__main__":
    image = load_mhd_file("data/L1.mhd")  # Update with correct path
    manager = ViewManager(image)
    manager.start()
