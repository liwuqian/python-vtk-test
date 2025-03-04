import vtkmodules.all as vtk

'''
This script demonstrates how to reslice a NIFTI image in different orientations using the vtkImageReslice class.
The user can scroll through the slices of the resliced image using the 'w' and 's' keys.
'''

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
reader.SetFileName("data/liver_57.nii.gz")
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
# reslice.SetInterpolationModeToNearestNeighbor()  # Nearest neighbor for mask data
reslice.Update()

# Get the image dimensions (number of slices)
dimensions = reader.GetOutput().GetDimensions()
max_slices = dimensions[2]


# Apply the lookup table to map scalar values to colors
color_map = vtk.vtkImageMapToWindowLevelColors()
color_map.SetInputConnection(reslice.GetOutputPort())
color_map.Update()

# Set up the image actor with the color map
image_actor = vtk.vtkImageActor()
image_actor.GetMapper().SetInputConnection(color_map.GetOutputPort())

# Set up the renderer, render window, and interactor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
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
