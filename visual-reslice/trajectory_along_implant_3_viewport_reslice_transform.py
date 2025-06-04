import vtkmodules.all as vtk

'''
This script demonstrates a multi-view reslice viewer using VTK.
It allows for interactive manipulation of an implant trajectory and scrolling view
and visualizes the corresponding resliced images in three orthogonal views and crosshair lines.
'''
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
        self.slice_offset = 0.0  # slice offset along implant axis

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
        # crosshair lines, two per view representing the two implant axes perpendicular to this view axis
        self.crosshair_lines = [vtk.vtkActor(), vtk.vtkActor()]
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        for i, actor in enumerate(self.crosshair_lines):
            actor.GetProperty().SetLineWidth(2)
            actor.GetProperty().SetColor(colors[(self.axis + 1 + i) % 3])
            self.renderer.AddActor(actor)
        self.update_reslice()
        self.update_crosshair_lines([0.0, 0.0, 0.0])  # Initialize crosshair lines
        self.renderer.ResetCamera()

    def update_reslice(self):
        base_reslice_matrix = create_reslice_matrix_from_transform(self.implant_transform, self.axis)
        # Modify the origin along the slice axis to apply the slice offset:
        origin = [base_reslice_matrix.GetElement(i, 3) for i in range(3)]
        axis_vector = [base_reslice_matrix.GetElement(i, 2) for i in range(3)]
        offset = [self.slice_offset * v for v in axis_vector]
        new_origin = [origin[i] + offset[i] for i in range(3)]
        for i in range(3):
            base_reslice_matrix.SetElement(i, 3, new_origin[i])
        self.reslice.SetResliceAxes(base_reslice_matrix)
        self.reslice.Update()
        self.color_map.Update()
        apply_reslice_transform_to_actor(
            self.implant_actor,
            base_reslice_matrix,
            self.implant_transform.GetMatrix()
        )
        # set camera clipping range
        # distance = self.renderer.GetActiveCamera().GetDistance()
        # self.renderer.GetActiveCamera().SetClippingRange(distance - 0.5, distance + 0.5)

    def update_crosshair_one_line(self, idx, center, direction):
        length = 100
        p1 = [center[i] - length * direction[i] for i in range(3)]
        p2 = [center[i] + length * direction[i] for i in range(3)]
        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(p1)
        line_source.SetPoint2(p2)
        line_source.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(line_source.GetOutputPort())
        self.crosshair_lines[idx].SetMapper(mapper)

    def update_crosshair_line_for_axis(self, active_axis, active_offset):
        crosshair_axes = [(self.axis + 1) % 3, (self.axis + 2) % 3]
        if active_axis not in crosshair_axes:
            return
        idx = crosshair_axes.index(active_axis)
        idx = (idx + 1) % 2  # switch to the other line
        base_reslice_matrix = create_reslice_matrix_from_transform(self.implant_transform, self.axis)
        implant_pos = self.implant_transform.GetPosition()
        axis_vec = [self.implant_transform.GetMatrix().GetElement(i, active_axis) for i in range(3)]
        center_world = [implant_pos[i] + active_offset * axis_vec[i] for i in range(3)]
        inverse = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Invert(base_reslice_matrix, inverse)
        center_reslice = list(inverse.MultiplyDoublePoint(center_world + [1]))[:3]
        update_dir = [1.0, 0.0, 0.0]
        if idx == 1:
            update_dir = [0.0, 1.0, 0.0]
        self.update_crosshair_one_line(idx, center_reslice, update_dir)
        
    def update_crosshair_lines(self, slice_offsets):
        for axis in range(3):
            if axis == self.axis:
                continue
            self.update_crosshair_line_for_axis(axis, slice_offsets[axis])

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
        self.slice_offsets = [0.0, 0.0, 0.0]
        self.views = [
            View(image_data, self.implant_transform, axis=0, viewport=(0, 0, 1 / 3, 1), render_window=self.render_window),
            View(image_data, self.implant_transform, axis=1, viewport=(1 / 3, 0, 2 / 3, 1), render_window=self.render_window),
            View(image_data, self.implant_transform, axis=2, viewport=(2 / 3, 0, 1, 1), render_window=self.render_window)
        ]
        self.active_axis = 2  # default: along cylinder axis is y
        self.interactor.AddObserver("KeyPressEvent", self.on_key_press)

    def render(self):
        self.render_window.Render()
        self.interactor.Initialize()
        self.interactor.Start()

    def on_key_press(self, obj, event):
        print("Active axis:", self.active_axis)
        key = self.interactor.GetKeySym()
        ctrl = self.interactor.GetControlKey()
        print(f"Key pressed: {key}, Ctrl: {ctrl}")
        # Move implant
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
        # Rotate implant (ctrl for inverse)
        elif key in ('x', 'y', 'z'):
            center = self.implant_transform.GetPosition()
            axis = {'x': [1, 0, 0], 'y': [0, 1, 0], 'z': [0, 0, 1]}[key]
            angle = -5 if ctrl else 5
            self.implant_transform.Translate(-center[0], -center[1], -center[2])
            self.implant_transform.RotateWXYZ(angle, *axis)
            self.implant_transform.Translate(center[0], center[1], center[2])
        # Reslice axis selection and scrolling
        elif key in ["1", "2", "3"]:
            self.active_axis = int(key) - 1
            print(f"Active axis changed to: {self.active_axis}")
        elif key == "equal" or key == "plus":
            self.slice_offsets[self.active_axis] += 1
            self.views[self.active_axis].slice_offset = self.slice_offsets[self.active_axis]
            print(f"Slice offset[{self.active_axis}] = {self.slice_offsets[self.active_axis]}")
        elif key == "minus":
            self.slice_offsets[self.active_axis] -= 1
            self.views[self.active_axis].slice_offset = self.slice_offsets[self.active_axis]
            print(f"Slice offset[{self.active_axis}] = {self.slice_offsets[self.active_axis]}")
        # Update all views after any change
        for view in self.views:
            view.update_reslice()
            view.update_crosshair_lines(self.slice_offsets)
        self.render_window.Render()

if __name__ == '__main__':
    image = load_mhd_file("data/L1.mhd")
    manager = ViewManager(image)
    manager.render()
