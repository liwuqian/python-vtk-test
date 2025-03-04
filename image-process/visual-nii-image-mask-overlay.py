import vtkmodules.all as vtk

'''
This script demonstrates how to overlay a mask on top of an image using the vtkImageActor class.
The mask image is displayed with a transparent background.
The user can scroll through the slices of the original image using the 'w' and 's' keys.
'''

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
            # self.slice = (self.slice + 1) % self.max_slices
            self.slice = 1
        elif key == "s":  # Scroll backward
            # self.slice = (self.slice - 1) % self.max_slices
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
reslice_image.SetInterpolationModeToCubic()  # Cubic for image data
reslice_image.Update()

reslice_mask = vtk.vtkImageReslice()
reslice_mask.SetInputConnection(reader_mask.GetOutputPort())
reslice_mask.SetOutputDimensionality(2)
reslice_mask.SetResliceAxes(resliceAxes)
reslice_mask.SetResliceAxesOrigin(reader_mask.GetOutput().GetCenter())
reslice_mask.SetInterpolationModeToNearestNeighbor()  # Nearest neighbor for mask data
reslice_mask.Update()

# print reslice mask pixel values
# mask_image = reslice_mask.GetOutput()
# dimensions = mask_image.GetDimensions()
# for i in range(dimensions[0]):
#     for j in range(dimensions[1]):
#         pixel = mask_image.GetScalarComponentAsDouble(i, j, 0, 0)
#         print(f"Pixel ({i}, {j}): {pixel}")
#         # if pixel > 0:
#         #     print(f"Pixel ({i}, {j}): {pixel}")


# Get the image dimensions (number of slices)
dimensions = reader_image.GetOutput().GetDimensions()
max_slices = dimensions[2]

# Set up the lookup table for different masks
lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(33)  # 0 to 32 (33 values)
lut.SetRange(0, 32)
lut.Build()
# Very important to set the background color to transparent
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

# Set up the image actor for the mask image
mask_actor = vtk.vtkImageActor()
mask_actor.GetMapper().SetInputConnection(color_map.GetOutputPort())
mask_actor.SetOpacity(0.7)

# Set up the image actor for the original image
image_actor = vtk.vtkImageActor()
image_actor.GetMapper().SetInputConnection(reslice_image.GetOutputPort())

# Set up the renderer, render window, and interactor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.SetSize(600, 600)
render_window.SetPosition(600, 500)
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Add the image actors to the renderer
renderer.AddActor(image_actor)
renderer.AddActor(mask_actor)
renderer.SetBackground(0.1, 0.1, 0.1)

# Initialize the reslice callback for mouse scroll events
reslice_callback_image = ResliceCallback(reslice_image, image_actor, max_slices)
# because they share the same reslice axes, we can use one callback for both
# reslice_callback_mask = ResliceCallback(reslice_mask, mask_actor, max_slices)

# Attach the callback to the interactor
interactor.AddObserver("KeyPressEvent", reslice_callback_image.execute)
# interactor.AddObserver("KeyPressEvent", reslice_callback_mask.execute)

# Initialize and start the rendering loop
render_window.Render()
interactor.Start()