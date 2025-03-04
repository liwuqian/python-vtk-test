import vtkmodules.all as vtk

'''
This script demonstrates how to visualize a NIFTI image with multiple masks using the vtkDiscreteMarchingCubes class.
The masks are used to segment the original image, and the segmented regions are visualized as isosurfaces.
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

# Read the NIFTI file (.nii.gz)
reader = vtk.vtkNIFTIImageReader()
# reader.SetFileName("data/liver_57.nii.gz")
reader.SetFileName("data/liver_57_multilabel.nii.gz")
reader.Update()

# render the mask image using different color for each label
# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Create a color lookup table to assign different colors to each mask index
lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(33)  # 0 to 32 (33 values)
lut.SetRange(0, 32)
lut.Build()

for i in range(1, 33):
    color = distinct_colors[i - 1]
    lut.SetTableValue(i, color[0], color[1], color[2], 1.0)
    # print(f"Color for mask {i}: {lut.GetTableValue(i)}")

# Assign random colors to each mask index
# import random
# for i in range(1, 33):
#     lut.SetTableValue(i, random.random(), random.random(), random.random(), 1.0)

# Use vtkDiscreteMarchingCubes to extract isosurfaces for each mask index
discrete_marching_cubes = vtk.vtkDiscreteMarchingCubes()
discrete_marching_cubes.SetInputConnection(reader.GetOutputPort())
discrete_marching_cubes.GenerateValues(25, 1, 25)  # Generate isosurfaces for mask indices 1 to 25

# Create a mapper and actor for the isosurfaces
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(discrete_marching_cubes.GetOutputPort())
mapper.SetLookupTable(lut)
mapper.SetScalarRange(1, 25)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Add the actor to the renderer
renderer.AddActor(actor)

# Set up the renderer, render window, and interactor
# renderer.SetBackground(0.1, 0.2, 0.4)  # Background color
render_window.SetSize(800, 600)
render_window.Render()
render_window_interactor.Start()
