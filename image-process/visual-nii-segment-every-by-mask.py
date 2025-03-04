# segment a single label from a mask and display it with the original image
# if overlaying the mask on the original image, we must use lookup table to map the mask pixel values to colors
# the lookup table must be set up transparently for the background
# otherwise, the mask will be displayed with a black background and occlude the original image

import vtkmodules.all as vtk

# Define a list of distinct colors (RGB values)
distinct_colors = [
    (1.0, 0.0, 0.0),  # Red
    (0.0, 1.0, 0.0),  # Green
    (0.0, 0.0, 1.0),  # Blue
    (1.0, 1.0, 0.0),  # Yellow
    (1.0, 0.0, 1.0),  # Magenta
    (0.0, 1.0, 1.0),  # Cyan
    (0.5, 0.0, 0.0),  # Dark Red
    (0.0, 0.5, 0.0),  # Dark Green
    (0.0, 0.0, 0.5),  # Dark Blue
    (0.5, 0.5, 0.0),  # Olive
    (0.5, 0.0, 0.5),  # Purple
    (0.0, 0.5, 0.5),  # Teal
    (0.75, 0.25, 0.0),  # Orange
    (0.25, 0.75, 0.0),  # Lime
    (0.0, 0.75, 0.25),  # Spring Green
    (0.0, 0.25, 0.75),  # Azure
    (0.25, 0.0, 0.75),  # Violet
    (0.75, 0.0, 0.25),  # Rose
    (1.0, 0.5, 0.5),  # Light Red
    (0.5, 1.0, 0.5),  # Light Green
    (0.5, 0.5, 1.0),  # Light Blue
    (1.0, 0.5, 1.0),  # Light Magenta
    (0.5, 1.0, 1.0),  # Light Cyan
    (1.0, 1.0, 0.5),  # Light Yellow
    (0.5, 0.0, 0.0),  # Maroon
    (0.0, 0.5, 0.0),  # Dark Green
    (0.0, 0.0, 0.5),  # Navy
    (0.5, 0.5, 0.0),  # Olive
    (0.5, 0.0, 0.5),  # Purple
    (0.0, 0.5, 0.5),  # Teal
    (1.0, 0.5, 0.0),  # Bright Orange
    (0.5, 0.0, 1.0),  # Indigo
    (0.75, 0.75, 0.75),  # Light Gray
    (0.25, 0.25, 0.25),  # Dark Gray
]

class ResliceCallback:
    def __init__(self, reslice, image_actor, max_slices):
        self.reslice = reslice
        self.image_actor = image_actor
        self.slice = 0
        self.max_slices = max_slices

    def execute(self, obj, event):
        key = obj.GetKeyCode()
        if key == "w":  # Scroll forward
            self.slice = 1
        elif key == "s":  # Scroll backward
            self.slice = -1
        # print("Slice:", self.slice)
        self.update_slice()

    def update_slice(self):
        offset = [0, 0, self.slice, 1]
        # using reslice axes to translate the image
        self.reslice.GetResliceAxes().MultiplyPoint(offset, offset)
        # print("Offset:", offset)
        self.reslice.SetResliceAxesOrigin(offset[0], offset[1], offset[2])
        self.reslice.Update()
        self.image_actor.GetMapper().Update()

def write_image_to_mhd(image, filename):
    writer = vtk.vtkMetaImageWriter()
    writer.SetInputData(image)
    writer.SetFileName(filename)
    writer.Write()

# Read the original NIFTI file (.nii.gz)
reader_image = vtk.vtkNIFTIImageReader()
reader_image.SetFileName("data/liver_57.nii.gz")
reader_image.Update()

# Read the mask NIFTI file (.nii.gz)
reader_mask = vtk.vtkNIFTIImageReader()
reader_mask.SetFileName("data/liver_57_multilabel.nii.gz")
reader_mask.Update()

# Reslice the image
resliceAxes = vtk.vtkMatrix4x4()
# sagittal view
resliceAxes.DeepCopy((0, 0, 1, 0,
                      1, 0, 0, 0,
                      0, 1, 0, 0,
                      0, 0, 0, 1))

# reslice image and mask share the same reslice axes
reslice_image = vtk.vtkImageReslice()
reslice_image.SetInputConnection(reader_image.GetOutputPort())
reslice_image.SetOutputDimensionality(2)
reslice_image.SetResliceAxes(resliceAxes)
reslice_image.SetResliceAxesOrigin(reader_image.GetOutput().GetCenter())
reslice_image.SetInterpolationModeToLinear()
reslice_image.Update()

reslice_mask = vtk.vtkImageReslice()
reslice_mask.SetInputConnection(reader_mask.GetOutputPort())
reslice_mask.SetOutputDimensionality(2)
reslice_mask.SetResliceAxes(resliceAxes)
reslice_mask.SetResliceAxesOrigin(reader_mask.GetOutput().GetCenter())
reslice_mask.SetInterpolationModeToNearestNeighbor()  # Nearest neighbor for mask data
reslice_mask.Update()

# Get the image dimensions (number of slices)
dimensions = reader_image.GetOutput().GetDimensions()
max_slices = dimensions[2]

# Extract pixel values from the original image
image_data = reader_image.GetOutput()
scalar_range = image_data.GetScalarRange()

# Compute the minimum pixel value from the original image
min_pixel_value = scalar_range[0]
max_pixel_value = scalar_range[1]

# Set up the lookup table for different masks
lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(33)  # 0 to 32 (33 values)
lut.SetRange(0, 32)
lut.Build()

lut.SetTableValue(0, 0, 0, 0, 0)  # Background color (transparent)

# Set the colors in the lookup table
for i in range(1, 33):
    color = distinct_colors[i - 1]
    lut.SetTableValue(i, color[0], color[1], color[2], 1.0)
    # print(f"Color for mask {i}: {lut.GetTableValue(i)}")

# Apply the lookup table to map scalar values to colors for the mask
color_map = vtk.vtkImageMapToColors()
color_map.SetInputConnection(reslice_mask.GetOutputPort())
color_map.SetLookupTable(lut)
color_map.PassAlphaToOutputOn()
color_map.SetOutputFormatToRGBA()
color_map.Update()

# Create a renderer, render window, and interactor
renderer_0 = vtk.vtkRenderer()
renderer_0.SetLayer(0)
renderer_1 = vtk.vtkRenderer()
renderer_1.SetLayer(1)
renderer_1.SetBackgroundAlpha(0.1)
renderer_1.SetBackground(0.1, 0.1, 0.1)
# Enable blending on renderer_1 (the mask renderer)
renderer_1.SetUseDepthPeeling(True)
renderer_1.SetMaximumNumberOfPeels(100)
renderer_1.SetOcclusionRatio(0.1)

render_window = vtk.vtkRenderWindow()
render_window.SetAlphaBitPlanes(1)
render_window.SetSize(600, 600)
render_window.SetPosition(600, 500)
render_window.AddRenderer(renderer_0)
render_window.AddRenderer(renderer_1)
render_window.SetNumberOfLayers(2)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Add the original image actor
image_actor = vtk.vtkImageActor()
image_actor.GetMapper().SetInputConnection(reslice_image.GetOutputPort())
renderer_0.AddActor(image_actor)

# Segment and add each label as a separate actor
for label in range(1, 33):
    # Display only a single label
    # if label != 19:
    #     continue
    threshold = vtk.vtkImageThreshold()
    threshold.SetInputConnection(reslice_mask.GetOutputPort())
    threshold.ThresholdBetween(label, label)
    threshold.SetInValue(1)
    threshold.SetOutValue(min_pixel_value)
    threshold.Update()

    # Check if the mask exists
    mask_exists = threshold.GetOutput().GetScalarRange()[1] > 0
    if not mask_exists:
        continue
    print(f"Label {label} exists")
    print("threshold scaler range: ", threshold.GetOutput().GetScalarRange())
    image_mask = vtk.vtkImageMask()
    # set mask default value as min_pixel_value
    image_mask.SetMaskedOutputValue(min_pixel_value)
    image_mask.SetInputConnection(0, reslice_image.GetOutputPort())
    image_mask.SetInputConnection(1, threshold.GetOutputPort())
    # image_mask.SetMaskedOutputValue(max_pixel_value)
    # set background to fully transparent
    # image_mask.SetMaskedOutputValue(0, 0, 0)
    image_mask.Update()
    print("image_mask scaler range: ", image_mask.GetOutput().GetScalarRange())
    # print mask pixel values
    # the mask pixel values are real pixel values from the original image
    # mask_image = image_mask.GetOutput()
    # dims = mask_image.GetDimensions()
    # for z in range(dims[2]):
    #     print("Slice", z)
    #     for y in range(dims[1]):
    #         for x in range(dims[0]):
    #             val = mask_image.GetScalarComponentAsFloat(x, y, z, 0)
    #             if val == min_pixel_value:
    #                 continue
    #             print(val, end=" ")
    #     #     print()  # Newline for new row
    #     # print()  # Newline for new slice

    # this mapper will map the mask pixel(real pixel) values to colors
    # vtk_mask_mapper = vtk.vtkImageMapToWindowLevelColors()
    # vtk_mask_mapper.SetInputConnection(image_mask.GetOutputPort())

    vtk_mask_mapper = vtk.vtkImageMapToColors()
    vtk_mask_mapper.SetInputConnection(image_mask.GetOutputPort())
    # the pixel values bigger than the max of the lookup table will be set to the max of the lookup table
    vtk_mask_mapper.SetLookupTable(lut)
    vtk_mask_mapper.PassAlphaToOutputOn()
    vtk_mask_mapper.SetOutputFormatToRGBA()
    vtk_mask_mapper.Update()

    segmented_image_actor = vtk.vtkImageActor()
    segmented_image_actor.GetMapper().SetInputConnection(vtk_mask_mapper.GetOutputPort())
    # segmented_image_actor.GetProperty().SetOpacity(0.6)
    renderer_1.AddActor(segmented_image_actor)


# Set up the renderer background color
# renderer.SetBackground(0.1, 0.1, 0.1)

# Initialize the reslice callback for mouse scroll events
reslice_callback_image = ResliceCallback(reslice_image, image_actor, max_slices)

# Attach the callback to the interactor
interactor.AddObserver("KeyPressEvent", reslice_callback_image.execute)

# Initialize and start the rendering loop
render_window.Render()
interactor.Start()