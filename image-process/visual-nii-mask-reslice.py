import vtkmodules.all as vtk

'''
This script demonstrates how to reslice a NIFTI image with multiple masks in different orientations using the vtkImageReslice class.
The user can scroll through the slices of the resliced image using the 'w' and 's' keys.
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
        print("Offset:", offset)
        self.reslice.SetResliceAxesOrigin(offset[0], offset[1], offset[2])
        self.reslice.Update()
        self.image_actor.GetMapper().Update()


# Read the NIFTI file (.nii.gz)
reader = vtk.vtkNIFTIImageReader()
reader.SetFileName("data/liver_57_multilabel.nii.gz")
reader.Update()

# Reslice the image
resliceAxes = vtk.vtkMatrix4x4()
# resliceAxes.DeepCopy((1, 0, 0, 0,
#                       0, 1, 0, 0,
#                       0, 0, 1, 0,
#                       0, 0, 0, 1))
# sagittal view
resliceAxes.DeepCopy((0, 0, 1, 0,
                      1, 0, 0, 0,
                      0, 1, 0, 0,
                      0, 0, 0, 1))
# coronal view
# resliceAxes.DeepCopy((1, 0, 0, 0,
#                     0, 0, 1, 0,
#                     0, -1, 0, 0,
#                     0, 0, 0, 1))
reslice = vtk.vtkImageReslice()
reslice.SetInputConnection(reader.GetOutputPort())
reslice.SetOutputDimensionality(2)
reslice.SetResliceAxes(resliceAxes)
# set the origin to the center of the image
reslice.SetResliceAxesOrigin(reader.GetOutput().GetCenter())
reslice.SetInterpolationModeToNearestNeighbor()  # Nearest neighbor for mask data
# reslice.SetInterpolationModeToCubic()  # Cubic for image data
reslice.Update()

scalar_range = reslice.GetOutput().GetScalarRange()
print("Reslice Scalar Range:", scalar_range)

# print reslice pixel values
# reslice_image = reslice.GetOutput()
# dims = reslice_image.GetDimensions()
# for z in range(dims[2]):
#     print("Slice", z)
#     for y in range(dims[1]):
#         for x in range(dims[0]):
#             val = reslice_image.GetScalarComponentAsFloat(x, y, z, 0)
#             print(val, end=" ")
#         print()  # Newline for new row
#     print()  # Newline for new slice
# reslice_image = reslice.GetOutput()
# dims = reslice_image.GetDimensions()
# for y in range(dims[1]):
#     for x in range(dims[0]):
#         val = reslice_image.GetScalarComponentAsFloat(x, y, 0, 0)
#         print(val, end=" ")
#     print()  # Newline for new row


# Get the image dimensions (number of slices)
dimensions = reader.GetOutput().GetDimensions()
max_slices = dimensions[2]

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
    print(f"Color for mask {i}: {lut.GetTableValue(i)}")

# Assign distinct colors to each value from 1 to 32
# for i in range(1, 33):
#     lut.SetTableValue(i, i / 32.0, (32 - i) / 32.0, (i % 10) / 10.0, 1.0)
#     print(f"Color for mask {i}: {lut.GetTableValue(i)}")


# Assign random colors to each mask index
# import random
# for i in range(1, 30):
#     lut.SetTableValue(i, random.random(), random.random(), random.random(), 1.0)

# for i in range(31):
#     print("Color for mask", i, ":", lut.GetTableValue(i))

# Apply the lookup table to map scalar values to colors
color_map = vtk.vtkImageMapToColors()
color_map.SetInputConnection(reslice.GetOutputPort())
color_map.SetLookupTable(lut)
color_map.PassAlphaToOutputOn()
color_map.SetOutputFormatToRGBA()
color_map.Update()
color_mapped_output = color_map.GetOutput()
print("Color Map Output Scalar Range:", color_mapped_output.GetScalarRange())

# Set up the image actor with the color map
image_actor = vtk.vtkImageActor()
image_actor.GetMapper().SetInputConnection(color_map.GetOutputPort())

# Set up the renderer, render window, and interactor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.SetSize(600, 600)
render_window.SetPosition(600, 500)
render_window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Add the image actor to the renderer
renderer.AddActor(image_actor)
renderer.SetBackground(0.1, 0.1, 0.1)

# Initialize the reslice callback for mouse scroll events
reslice_callback = ResliceCallback(reslice, image_actor, max_slices)

# Attach the callback to the interactor
interactor.AddObserver("KeyPressEvent", reslice_callback.execute)

# Initialize and start the rendering loop
render_window.Render()
interactor.Start()
