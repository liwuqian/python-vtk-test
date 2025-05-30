import vtkmodules.all as vtk
import numpy as np

# Load the MHD file using VTK
def load_mhd_file(file_path):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(file_path)
    reader.Update()
    return reader.GetOutput()

# Create reslice matrix for reslicing along a trajectory
def create_reslice_matrix(normal, view_up, center):
    normal = np.array(normal)
    view_up = np.array(view_up)

    normal = normal / np.linalg.norm(normal)
    x_axis = np.cross(view_up, normal)
    x_axis = x_axis / np.linalg.norm(x_axis)
    y_axis = np.cross(normal, x_axis)
    y_axis = y_axis / np.linalg.norm(y_axis)

    matrix = vtk.vtkMatrix4x4()
    for i in range(3):
        matrix.SetElement(i, 0, x_axis[i])
        matrix.SetElement(i, 1, y_axis[i])
        matrix.SetElement(i, 2, normal[i])
        matrix.SetElement(i, 3, center[i])
    return matrix

# Create reslice filter
def create_reslice(image_data, normal, view_up, center):
    reslice = vtk.vtkImageReslice()
    reslice.SetInputData(image_data)
    reslice_matrix = create_reslice_matrix(normal, view_up, center)
    reslice.SetResliceAxes(reslice_matrix)
    reslice.SetOutputDimensionality(2)
    reslice.SetInterpolationModeToLinear()
    reslice.SetOutputSpacing(1.0, 1.0, 1.0)
    return reslice, reslice_matrix

# Apply window-level colormap
def apply_window_level(reslice_output, window, level):
    color_map = vtk.vtkImageMapToWindowLevelColors()
    color_map.SetInputConnection(reslice_output.GetOutputPort())
    color_map.SetWindow(window)
    color_map.SetLevel(level)
    color_map.Update()
    return color_map

def create_cylinder_actor(center):
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetCenter(center)
    cylinder.SetRadius(5)
    cylinder.SetHeight(100)
    cylinder.SetResolution(50)
    cylinder.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cylinder.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.8, 0.6, 0.3)
    # actor.GetProperty().SetOpacity(0.9)
    return actor

# Apply inverse of reslice matrix to actor
def apply_reslice_transform_to_actor(actor, reslice_matrix):
    inverse_matrix = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Invert(reslice_matrix, inverse_matrix)
    transform = vtk.vtkTransform()
    transform.SetMatrix(inverse_matrix)
    actor.SetUserTransform(transform)

# Display the image and handle interactions
def display_with_interaction(image_data, window, level):
    center = list(image_data.GetCenter())
    spacing = 1.0

    # Define trajectory directions
    trajectory_directions = {
        "x": ([1, 0, 0], [0, 0, 1]),
        "y": ([0, 1, 0], [0, 0, 1]),
        "z": ([0, 0, 1], [0, 1, 0])
    }
    current_axis = 'z'

    # Create reslice + colormap
    reslice, reslice_matrix = create_reslice(image_data, *trajectory_directions[current_axis], center)
    color_map = apply_window_level(reslice, window, level)

    image_actor = vtk.vtkImageActor()
    image_actor.GetMapper().SetInputConnection(color_map.GetOutputPort())

    # Create and place cylinder
    cylinder_actor = create_cylinder_actor(center)
    apply_reslice_transform_to_actor(cylinder_actor, reslice_matrix)

    # Renderer & Window
    renderer = vtk.vtkRenderer()
    renderer.AddActor(image_actor)
    renderer.AddActor(cylinder_actor)
    renderer.SetBackground(0.1, 0.1, 0.1)

    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(50, 50, 50)
    renderer.AddActor(axes)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Key interaction
    def keypress_callback(obj, event):
        nonlocal current_axis, center, reslice, reslice_matrix, color_map

        key = obj.GetKeySym()
        updated = False

        if key in trajectory_directions:
            print(f"Switched to {key.upper()} trajectory")
            current_axis = key
            updated = True
        elif key == "Up":
            for i in range(3):
                center[i] += trajectory_directions[current_axis][0][i] * spacing
            updated = True
        elif key == "Down":
            for i in range(3):
                center[i] -= trajectory_directions[current_axis][0][i] * spacing
            updated = True

        if updated:
            reslice.SetResliceAxes(create_reslice_matrix(*trajectory_directions[current_axis], center))
            reslice.Update()
            color_map.Update()
            # Update cylinder position
            apply_reslice_transform_to_actor(cylinder_actor, reslice.GetResliceAxes())
            render_window.Render()

    interactor.AddObserver("KeyPressEvent", keypress_callback)

    # Camera
    renderer.GetActiveCamera().SetParallelProjection(True)
    renderer.ResetCamera()
    render_window.Render()
    interactor.Start()

# Main
if __name__ == "__main__":
    file_path = "data/L1.mhd"  # change to your MHD path
    image_data = load_mhd_file(file_path)
    display_with_interaction(image_data, window=400, level=40)
