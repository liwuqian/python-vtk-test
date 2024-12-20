import vtkmodules.all as vtk

# Load the MHD file using VTK
def load_mhd_file(file_path):
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(file_path)
    reader.Update()
    return reader.GetOutput()

# Configure the image reslice for viewing slices
def create_reslice(image_data):
    reslice = vtk.vtkImageReslice()
    reslice.SetInputData(image_data)
    reslice.SetOutputDimensionality(2)
    reslice.SetInterpolationModeToLinear()
    axial_rpl = [1, 0, 0, 
                 0, 1, 0, 
                 0, 0, 1]
    axial_lpr = [-1, 0, 0,
                 0, 1, 0,
                 0, 0, -1]
    axial_lpr2 = [  -1, 0, 0,
                    0, 1, 0,
                    0, 0, 1]
    reslice.SetResliceAxesDirectionCosines(axial_lpr2)
    # set image center as the reslice center
    image_center = list(image_data.GetCenter())
    print("image center: ", image_center)
    image_center[2] = image_center[2] - 15
    reslice.SetResliceAxesOrigin(image_center)
    return reslice

# Apply window-level colormap
def apply_window_level(reslice_output, window, level):
    color_map = vtk.vtkImageMapToWindowLevelColors()
    color_map.SetInputConnection(reslice_output.GetOutputPort())
    color_map.SetWindow(window)
    color_map.SetLevel(level)
    color_map.Update()
    return color_map.GetOutput()

# Display the image using VTK's rendering pipeline
def display_image(image_data):
    actor = vtk.vtkImageActor()
    actor.GetMapper().SetInputData(image_data)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.1, 0.1, 0.1)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(600, 600)
    render_window.SetPosition(500, 500)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    render_window.Render()
    # print cameara all information
    renderer.GetActiveCamera().SetParallelProjection(1)
    renderer.ResetCamera()
    render_window.Render()
    camera = renderer.GetActiveCamera()
    print("camera: ", camera.GetPosition(), camera.GetFocalPoint(), camera.GetViewUp())
    interactor.Start()

# Main function
if __name__ == "__main__":
    # Path to your .mhd file
    file_path = "data/L1.mhd"

    # Load the MHD file
    image_data = load_mhd_file(file_path)

    # Configure the reslice (default axial view)
    reslice = create_reslice(image_data)

    # Apply a window and level
    window = 400  # Width of the colormap
    level = 40    # Center of the colormap
    window_level_image = apply_window_level(reslice, window, level)

    # Display the image
    display_image(window_level_image)
