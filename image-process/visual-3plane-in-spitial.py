import vtkmodules.all as vtk

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

# Load a sample volume dataset
filename = "data/origin.mhd"
reader = vtk.vtkMetaImageReader()
reader.SetFileName(filename)  # Replace with your volume file
reader.Update()

# Get volume properties
image_data = reader.GetOutput()
dims = image_data.GetDimensions()  # (X, Y, Z)
spacing = image_data.GetSpacing()  # (mm per voxel)
origin = image_data.GetOrigin()  # (World coordinates of voxel (0,0,0))

# Initialize reslice origin (start at volume center)
reslice_origin = [
    origin[0] + (dims[0] * spacing[0]) / 2,
    origin[1] + (dims[1] * spacing[1]) / 2,
    origin[2] + (dims[2] * spacing[2]) / 2
]

# Create renderer, render window, and interactor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Function to create reslice filter for each plane
def create_reslice(reslice_matrix):
    reslice = vtk.vtkImageReslice()
    reslice.SetInputConnection(reader.GetOutputPort())
    reslice.SetResliceAxes(reslice_matrix)
    reslice.SetInterpolationModeToLinear()
    reslice.SetOutputDimensionality(2)
    reslice.Update()
    return reslice

# Function to create an image actor and set its user matrix
def create_image_actor(reslice, reslice_matrix):
    actor = vtk.vtkImageActor()
    actor.GetMapper().SetInputConnection(reslice.GetOutputPort())

    # Apply reslice matrix as UserMatrix
    user_matrix = vtk.vtkMatrix4x4()
    user_matrix.DeepCopy(reslice_matrix)
    actor.SetUserMatrix(user_matrix)

    return actor

# Define reslice matrices
matrix_axial = vtk.vtkMatrix4x4()
matrix_coronal = vtk.vtkMatrix4x4()
matrix_sagittal = vtk.vtkMatrix4x4()

# Axial (XY Plane)
matrix_axial.DeepCopy((1, 0, 0, reslice_origin[0],
                       0, 1, 0, reslice_origin[1],
                       0, 0, 1, reslice_origin[2],
                       0, 0, 0, 1))

# Coronal (XZ Plane)
matrix_coronal.DeepCopy((1, 0, 0, reslice_origin[0],
                         0, 0, 1, reslice_origin[1],
                         0, -1, 0, reslice_origin[2],
                         0, 0, 0, 1))

# Sagittal (YZ Plane)
matrix_sagittal.DeepCopy((0, 0, 1, reslice_origin[0],
                          0, 1, 0, reslice_origin[1],
                          1, 0, 0, reslice_origin[2],
                          0, 0, 0, 1))

# Create reslice filters
reslice_axial = create_reslice(matrix_axial)
reslice_coronal = create_reslice(matrix_coronal)
reslice_sagittal = create_reslice(matrix_sagittal)

# Create image actors (with correct transforms)
axial_actor = create_image_actor(reslice_axial, matrix_axial)
coronal_actor = create_image_actor(reslice_coronal, matrix_coronal)
sagittal_actor = create_image_actor(reslice_sagittal, matrix_sagittal)

# Function to update reslice planes
def update_reslice_planes(plane_id, step_value):
    if plane_id == 'axial':
        matrix = matrix_axial
        reslice = reslice_axial
        actor = axial_actor
        # translation_vector = [0, 0, step_value]  # Move along plane's Z axis
    elif plane_id == 'coronal':
        matrix = matrix_coronal
        reslice = reslice_coronal
        actor = coronal_actor
        # translation_vector = [0, step_value, 0]  # Move along plane's Y axis
    elif plane_id == 'sagittal':
        matrix = matrix_sagittal
        reslice = reslice_sagittal
        actor = sagittal_actor
        # translation_vector = [step_value, 0, 0]  # Move along plane's X axis
    else:
        return
    print(f"Moving {plane_id} plane by {step_value} mm")
    # Translate in the reslice matrix coordinate system
    translation_vector = [0, 0, step_value, 1]
    matrix.MultiplyPoint(translation_vector, translation_vector)
    matrix.SetElement(0, 3, translation_vector[0])
    matrix.SetElement(1, 3, translation_vector[1])
    matrix.SetElement(2, 3, translation_vector[2])

    # Update reslice filter
    reslice.Update()

    # Update actor transformation
    user_matrix = vtk.vtkMatrix4x4()
    user_matrix.DeepCopy(matrix)
    # print(user_matrix)
    actor.SetUserMatrix(user_matrix)

    # Refresh display
    render_window.Render()

# Keyboard interaction for moving planes
def on_key_press(obj, event):
    key = obj.GetKeySym()
    step_value = spacing[2]  # Step size (voxel size in Z)
    print(key)

    if key == "Up":
        update_reslice_planes('coronal', step_value)  # Move Coronal Up
    elif key == "Down":
        update_reslice_planes('coronal', -step_value)  # Move Coronal Down
    elif key == "Right":
        update_reslice_planes('sagittal', step_value)  # Move Sagittal Right
    elif key == "Left":
        update_reslice_planes('sagittal', -step_value)  # Move Sagittal Left
    elif key == "Prior":  # Page Up
        update_reslice_planes('axial', step_value)  # Move Axial Up
    elif key == "Next":   # Page Down
        update_reslice_planes('axial', -step_value)  # Move Axial Down

# Add observer for keyboard interaction
interactor.AddObserver("KeyPressEvent", on_key_press)

# add volume rendering
volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
volume_mapper.SetInputConnection(reader.GetOutputPort())
volume_property = vtk.vtkVolumeProperty()
set_volume_properties_default(volume_property)
volume = vtk.vtkVolume()
volume.SetMapper(volume_mapper)
volume.SetProperty(volume_property)

# Add image actors to renderer
renderer.AddVolume(volume)
renderer.AddActor(axial_actor)
renderer.AddActor(coronal_actor)
renderer.AddActor(sagittal_actor)

# add axes to the renderer
axes = vtk.vtkAxesActor()
axes.SetTotalLength(10, 10, 10)
# set axes label size
axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
axes.GetXAxisCaptionActor2D().GetTextActor().SetHeight(0.02)
axes.GetYAxisCaptionActor2D().GetTextActor().SetHeight(0.02)
axes.GetZAxisCaptionActor2D().GetTextActor().SetHeight(0.02)
renderer.AddActor(axes)

# Render and start interaction
renderer.ResetCamera()
render_window.Render()
interactor.Initialize()
interactor.Start()
