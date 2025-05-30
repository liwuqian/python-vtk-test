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


def build_line_actor(p1, p2, color=(1, 1, 1), linewidth=2):
    line = vtk.vtkLineSource()
    line.SetPoint1(p1)
    line.SetPoint2(p2)
    line.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(line.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetLineWidth(linewidth)
    return actor


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
        self.crosshair_default_endpoints = [
            [0, 0, -100], [0, 0, 100],  # along (axis+1)%3
            [0, -100, 0], [0, 100, 0]   # along (axis+2)%3
        ]
        colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        for i, actor in enumerate(self.crosshair_lines):
            actor.GetProperty().SetLineWidth(2)
            actor.GetProperty().SetColor(colors[(self.axis + 1 + i) % 3])
            self.renderer.AddActor(actor)

        self.update_reslice()
        self.renderer.ResetCamera()

    def update_reslice(self):
        # Build the reslice axes matrix with offset for slice scrolling
        base_reslice_matrix = create_reslice_matrix_from_transform(self.implant_transform, self.axis)

        # Modify the origin along the slice axis to apply the slice offset:
        # The slice axis in the reslice matrix corresponds to the 3rd column (index 2)
        origin = [base_reslice_matrix.GetElement(i, 3) for i in range(3)]
        axis_vector = [base_reslice_matrix.GetElement(i, 2) for i in range(3)]
        # Add offset along the normal direction of the reslice plane:
        offset = [self.slice_offset * v for v in axis_vector]
        new_origin = [origin[i] + offset[i] for i in range(3)]

        for i in range(3):
            base_reslice_matrix.SetElement(i, 3, new_origin[i])

        self.reslice.SetResliceAxes(base_reslice_matrix)
        self.reslice.Update()
        self.color_map.Update()

        # Update implant actor position & orientation relative to reslice plane
        apply_reslice_transform_to_actor(
            self.implant_actor,
            base_reslice_matrix,
            self.implant_transform.GetMatrix()
        )

        # Update crosshair lines in this view based on implant transform and slice offset
        self.update_crosshair_lines(base_reslice_matrix)
        # Get crosshair lines default endpoints from actor geometry
        for i, actor in enumerate(self.crosshair_lines):
            polydata = actor.GetMapper().GetInput()
            p1 = list(polydata.GetPoint(0))
            p2 = list(polydata.GetPoint(1))
            self.crosshair_default_endpoints[i * 2] = p1
            self.crosshair_default_endpoints[i * 2 + 1] = p2

    def update_crosshair_lines(self, reslice_matrix):
        # The two crosshair lines lie along implant axes perpendicular to this view axis
        # We'll build them centered at the crosshair center in reslice space,
        # which is the intersection point on the reslice plane

        # Center in world coordinates = implant position translated along slice offset axis
        implant_pos = self.implant_transform.GetPosition()
        axis_vec = [reslice_matrix.GetElement(i, 2) for i in range(3)]
        center_world = [implant_pos[i] + self.slice_offset * axis_vec[i] for i in range(3)]

        # Transform center to reslice space
        inverse = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Invert(reslice_matrix, inverse)
        center_reslice = list(inverse.MultiplyDoublePoint(center_world + [1]))[:3]

        # Direction vectors for the two lines in reslice space (axes perpendicular to the slice axis)
        # We get them from implant_transform matrix columns corresponding to these axes, then transform to reslice space
        def get_direction_vec(col):
            v = [self.implant_transform.GetMatrix().GetElement(i, col) for i in range(3)] + [0.0]
            v_reslice = list(inverse.MultiplyDoublePoint(v))[:3]
            norm = vtk.vtkMath.Norm(v_reslice)
            if norm > 0:
                v_reslice = [c / norm for c in v_reslice]
            return v_reslice

        dir1 = get_direction_vec((self.axis + 1) % 3)
        dir2 = get_direction_vec((self.axis + 2) % 3)

        length = 100  # crosshair line half-length in reslice space

        # Update each crosshair line actor with new geometry
        for actor, direction in zip(self.crosshair_lines, [dir1, dir2]):
            # define self crosshair default line endpoints for the two directions
            p1 = [center_reslice[i] - length * direction[i] for i in range(3)]
            p2 = [center_reslice[i] + length * direction[i] for i in range(3)]
            line_source = vtk.vtkLineSource()
            line_source.SetPoint1(p1)
            line_source.SetPoint2(p2)
            line_source.Update()
            actor.SetMapper(vtk.vtkPolyDataMapper())
            actor.GetMapper().SetInputConnection(line_source.GetOutputPort())
    
    def update_one_crosshair_line(self, idx, slice_offset, direction):
        # Fix: Get endpoints from the polydata using GetPoint
        # polydata = self.crosshair_lines[idx].GetMapper().GetInput()
        # p1 = list(polydata.GetPoint(0))
        # p2 = list(polydata.GetPoint(1))
        # using the default endpoints instead
        p1 = self.crosshair_default_endpoints[idx * 2]
        p2 = self.crosshair_default_endpoints[idx * 2 + 1]
        # Update the crosshair line geometry based on the new slice offset
        new_p1 = [p1[i] + slice_offset * direction[i] for i in range(3)]
        new_p2 = [p2[i] + slice_offset * direction[i] for i in range(3)]
        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(new_p1)
        line_source.SetPoint2(new_p2)
        line_source.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(line_source.GetOutputPort())
        self.crosshair_lines[idx].SetMapper(mapper)

    def update_crosshair_line_for_axis(self, active_axis, slice_offset):
        """
        Update one of this view's crosshair lines corresponding to implant axis 'axis',
        given the slice offset along that axis.
        This method is called by other views when they scroll slices.
        """
        print('===================================================')
        print("slice_offset:", slice_offset)
        # We only have two crosshair lines: along (self.axis+1)%3 and (self.axis+2)%3 axes
        # If 'axis' is not one of those, this view doesn't show that axis line, so ignore
        crosshair_axes = [(self.axis + 1) % 3, (self.axis + 2) % 3]
        if active_axis not in crosshair_axes:
            return  # nothing to update in this view

        # Figure out which crosshair line to update:
        idx = crosshair_axes.index(active_axis)
        print("identified crosshair line index:", idx)
        # but we need to update another line
        idx = (idx + 1) % 2  # switch to the other line
        print("crosshair line index to update:", idx)

        # Build reslice matrix WITHOUT slice offset on this view (keep own slice offset)
        base_reslice_matrix = create_reslice_matrix_from_transform(self.implant_transform, self.axis)

        # Calculate world coordinate of crosshair line center using slice_offset along 'axis'
        implant_pos = self.implant_transform.GetPosition()
        print("implant_pos (world):", implant_pos)
        # Axis vector of implant axis 'axis' in world coords (column of implant matrix)
        axis_vec = [self.implant_transform.GetMatrix().GetElement(i, active_axis) for i in range(3)]
        print("axis_vec (world):", axis_vec)

        # Center position in world coords is implant position + slice_offset * axis_vec
        center_world = [implant_pos[i] + slice_offset * axis_vec[i] for i in range(3)]
        print("center_world:", center_world)

        # Transform center to reslice space of this view
        inverse = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Invert(base_reslice_matrix, inverse)
        center_reslice = list(inverse.MultiplyDoublePoint(center_world + [1]))[:3]
        print("center_reslice:", center_reslice)

        # Direction vector of this crosshair line (axis) in reslice space:
        v = [self.implant_transform.GetMatrix().GetElement(i, active_axis) for i in range(3)] + [0.0]
        print("v (world):", v)
        v_reslice = list(inverse.MultiplyDoublePoint(v))[:3]
        print("v_reslice (before normalization):", v_reslice)
        norm = vtk.vtkMath.Norm(v_reslice)
        if norm > 0:
            v_reslice = [c / norm for c in v_reslice]
        print("v_reslice (normalized):", v_reslice)
        print("self axis:", self.axis, "line idx:", idx)
        print('===================================================')
        self.update_one_crosshair_line(idx, slice_offset, v_reslice)


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

        # Slice offsets for each implant axis
        self.slice_offsets = [0.0, 0.0, 0.0]

        # Three views, each reslicing along one implant axis
        self.views = [
            View(image_data, self.implant_transform, axis=0, viewport=(0, 0, 1 / 3, 1), render_window=self.render_window),
            View(image_data, self.implant_transform, axis=1, viewport=(1 / 3, 0, 2 / 3, 1), render_window=self.render_window),
            View(image_data, self.implant_transform, axis=2, viewport=(2 / 3, 0, 1, 1), render_window=self.render_window)
        ]

        self.active_axis = 2  # along cylinder axis is y

        self.interactor.AddObserver("KeyPressEvent", self.on_key_press)

    def render(self):
        self.render_window.Render()
        self.interactor.Initialize()
        self.interactor.Start()

    def on_key_press(self, obj, event):
        key = self.interactor.GetKeySym()
        print(f"Key pressed: {key}")
        if key in ["1", "2", "3"]:
            self.active_axis = int(key) - 1
            print(f"Active axis changed to: {self.active_axis}")
        elif key == "equal" or key == "plus":
            self.slice_offsets[self.active_axis] += 1
            print(f"Slice offset[{self.active_axis}] = {self.slice_offsets[self.active_axis]}")
            self.update_views()
        elif key == "minus":
            self.slice_offsets[self.active_axis] -= 1
            print(f"Slice offset[{self.active_axis}] = {self.slice_offsets[self.active_axis]}")
            self.update_views()

    def update_views(self):
        # Update main view along active_axis
        self.views[self.active_axis].slice_offset = self.slice_offsets[self.active_axis]
        self.views[self.active_axis].update_reslice()

        # Update crosshair lines in other views
        for i in range(3):
            if i == self.active_axis:
                continue
            self.views[i].update_crosshair_line_for_axis(self.active_axis, self.slice_offsets[self.active_axis])

        self.render_window.Render()


if __name__ == '__main__':
    image = load_mhd_file("data/L1.mhd")
    manager = ViewManager(image)
    manager.render()
