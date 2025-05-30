import vtkmodules.all as vtk
import numpy as np

# Load the MHD file

def load_mhd_file(file_path):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(file_path)
    reader.Update()
    return reader.GetOutput()

# Create a reslice matrix from implant transform

def create_reslice_matrix_from_transform(transform):
    matrix = transform.GetMatrix()
    axes = vtk.vtkMatrix4x4()
    for i in range(3):
        for j in range(3):
            axes.SetElement(i, j, matrix.GetElement(i, j))
        axes.SetElement(i, 3, matrix.GetElement(i, 3))
    return axes

# Create reslice filter

def create_reslice(image_data, transform):
    reslice = vtk.vtkImageReslice()
    reslice.SetInputData(image_data)
    axes_matrix = create_reslice_matrix_from_transform(transform)
    reslice.SetResliceAxes(axes_matrix)
    reslice.SetOutputDimensionality(2)
    reslice.SetInterpolationModeToLinear()
    reslice.SetOutputSpacing(1.0, 1.0, 1.0)
    return reslice, axes_matrix

# Window-level colormap

def apply_window_level(reslice_output, window, level):
    color_map = vtk.vtkImageMapToWindowLevelColors()
    color_map.SetInputConnection(reslice_output.GetOutputPort())
    color_map.SetWindow(window)
    color_map.SetLevel(level)
    color_map.Update()
    return color_map

# Create a cylinder actor

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

# Compute final transform in reslice space and apply to actor
def apply_reslice_transform_to_actor(actor, reslice_matrix, implant_matrix):
    inverse_reslice = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Invert(reslice_matrix, inverse_reslice)

    final_matrix = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(inverse_reslice, implant_matrix, final_matrix)

    actor.SetUserMatrix(final_matrix)

# Display function
def display_with_interaction(image_data, window, level):
    center = np.array(image_data.GetCenter())

    # Create transform to represent implant pose in DICOM
    implant_transform = vtk.vtkTransform()
    implant_transform.PostMultiply()
    implant_transform.Translate(center)

    # Reslice
    reslice, _ = create_reslice(image_data, implant_transform)
    color_map = apply_window_level(reslice, window, level)

    image_actor = vtk.vtkImageActor()
    image_actor.GetMapper().SetInputConnection(color_map.GetOutputPort())

    # Implant (cylinder)
    implant_actor = create_cylinder_actor()
    # implant_actor.SetUserMatrix(implant_transform.GetMatrix())
    apply_reslice_transform_to_actor(implant_actor, reslice.GetResliceAxes(), implant_transform.GetMatrix())

    # Renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(image_actor)
    renderer.AddActor(implant_actor)

    axes = vtk.vtkAxesActor()
    axes.SetTotalLength(60, 60, 60)
    # set the label: X Y Z small size
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(10)
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(10)
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(10)
    axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()

    renderer.AddActor(axes)
    renderer.SetBackground(0.1, 0.1, 0.1)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Interaction
    def keypress_callback(obj, event):
        key = obj.GetKeySym()

        if key == 'w':
            implant_transform.Translate(0, 1, 0)
        elif key == 's':
            implant_transform.Translate(0, -1, 0)
        elif key == 'a':
            implant_transform.Translate(-1, 0, 0)
        elif key == 'd':
            implant_transform.Translate(1, 0, 0)
        elif key == 'Up':
            implant_transform.Translate(0, 0, -1)
        elif key == 'Down':
            implant_transform.Translate(0, 0, 1)

        elif key in ('x', 'y', 'z'):
            # Rotate around implant's local axis at its current center
            center = implant_transform.GetPosition()
            if key == 'x':
                axis = [1, 0, 0]
            elif key == 'y':
                axis = [0, 1, 0]
            elif key == 'z':
                axis = [0, 0, 1]
            else:
                axis = [0, 0, 0]
            # Translate to center, rotate, translate back
            implant_transform.PostMultiply()
            implant_transform.Translate(-center[0], -center[1], -center[2])
            implant_transform.RotateWXYZ(5, *axis)
            implant_transform.Translate(center[0], center[1], center[2])

        # Update reslice to align with implant
        new_reslice_matrix = create_reslice_matrix_from_transform(implant_transform)
        reslice.SetResliceAxes(new_reslice_matrix)
        reslice.Update()
        color_map.Update()

        # Apply the new transform to the actor
        apply_reslice_transform_to_actor(implant_actor, new_reslice_matrix, implant_transform.GetMatrix())

        render_window.Render()

    interactor.AddObserver("KeyPressEvent", keypress_callback)

    renderer.GetActiveCamera().SetParallelProjection(True)
    renderer.ResetCamera()
    render_window.Render()
    interactor.Start()

# Main
if __name__ == "__main__":
    file_path = "data/L1.mhd"  # Adjust this path to your data
    image_data = load_mhd_file(file_path)
    display_with_interaction(image_data, window=400, level=40)
