import vtkmodules.all as vtk

# Define the path to your MHD file
mhd_file_path = "data/decompressionvolume.mhd"

# Create a reader for the MHD file
reader = vtk.vtkMetaImageReader()
reader.SetFileName(mhd_file_path)
reader.Update()

# Get the output of the reader
image_data = reader.GetOutput()

# Get the dimensions of the image data
dims = image_data.GetDimensions()

# Open a file for writing
# output_file_path = "mask_values.txt"
# with open(output_file_path, "w") as f:
#     # Iterate through the image data and write the values to the file
#     for z in range(dims[2]):
#         f.write("Slice {}\n".format(z))
#         for y in range(dims[1]):
#             for x in range(dims[0]):
#                 val = image_data.GetScalarComponentAsFloat(x, y, z, 0)
#                 f.write("{:.2f} ".format(val))  # Adjust the format as needed
#             f.write("\n")  # Newline for new row
#         f.write("\n")  # Newline for new slice

# print("Pixel values written to", output_file_path)

# Iterate through the image data and print out the values
# for z in range(dims[2]):
#     print("Slice", z)
#     for y in range(dims[1]):
#         for x in range(dims[0]):
#             val = image_data.GetScalarComponentAsFloat(x, y, z, 0)
#             print(val, end=" ")
#         print()  # Newline for new row
#     print()  # Newline for new slice

# Apply threshold filter to isolate the region of interest (mask with value 1)
threshold = vtk.vtkThreshold()
threshold.SetInputData(image_data)
threshold.SetUpperThreshold(1.1)
threshold.SetLowerThreshold(0.9)
threshold.Update()

# Create a mapper
mapper = vtk.vtkDataSetMapper()
mapper.SetInputConnection(threshold.GetOutputPort())

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(1, 1, 1)  # Set background to white

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create an interactor
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Start the rendering loop
render_window.Render()
render_window_interactor.Start()
