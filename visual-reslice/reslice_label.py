import vtkmodules.all as vtk
import numpy as np

# Convert VTK matrix column to numpy array
def get_axis(reslice_axes: vtk.vtkMatrix4x4, col: int) -> np.ndarray:
    return np.array([reslice_axes.GetElement(r, col) for r in range(3)])

# Compute anatomical label (L/R, A/P, S/I) for a direction
def get_anatomical_label(direction: np.ndarray) -> str:
    direction = direction / np.linalg.norm(direction)
    axes = {
        "L": np.array([1, 0, 0]),
        "R": np.array([-1, 0, 0]),
        "P": np.array([0, 1, 0]),
        "A": np.array([0, -1, 0]),
        "S": np.array([0, 0, 1]),
        "I": np.array([0, 0, -1]),
    }

    max_dot = -np.inf
    best_label = ""
    for label, axis in axes.items():
        dot = np.dot(direction, axis)
        if dot > max_dot:
            max_dot = dot
            best_label = label
    return best_label

# Add a label to the screen using vtkTextActor
def add_label(renderer, label, x, y):
    text_actor = vtk.vtkTextActor()
    text_actor.SetInput(label)
    text_actor.GetTextProperty().SetFontSize(24)
    text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
    text_actor.SetPosition(x, y)
    renderer.AddActor2D(text_actor)
    return text_actor

# Add L/R/A/P/S/I labels based on reslice axes orientation
def add_anatomical_labels(reslice_axes, renderer, window_size):
    x_axis = get_axis(reslice_axes, 0)     # X-axis (left-right)
    y_axis = get_axis(reslice_axes, 1)     # Y-axis (top-bottom)

    # Opposite directions
    left_dir = -x_axis
    right_dir = x_axis
    top_dir = -y_axis
    bottom_dir = y_axis

    # Get labels
    left_label = get_anatomical_label(left_dir)
    right_label = get_anatomical_label(right_dir)
    top_label = get_anatomical_label(top_dir)
    bottom_label = get_anatomical_label(bottom_dir)

    w, h = window_size

    # Position labels around viewport
    add_label(renderer, left_label, 10, h // 2)
    add_label(renderer, right_label, w - 30, h // 2)
    add_label(renderer, top_label, w // 2, h - 30)
    add_label(renderer, bottom_label, w // 2, 10)

# Setup VTK renderer and render window
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(512, 512)

# Dummy reslice axes for oblique orientation
reslice_axes = vtk.vtkMatrix4x4()
reslice_axes.Identity()
reslice_axes.SetElement(0, 0, 0.707)  # X axis pointing diagonally
reslice_axes.SetElement(1, 0, 0.707)
reslice_axes.SetElement(2, 0, 0.0)

reslice_axes.SetElement(0, 1, -0.5)   # Y axis also oblique
reslice_axes.SetElement(1, 1, 0.5)
reslice_axes.SetElement(2, 1, 0.707)

# Add labels
add_anatomical_labels(reslice_axes, renderer, render_window.GetSize())

# Show window
render_window.Render()
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)
interactor.Initialize()
interactor.Start()
