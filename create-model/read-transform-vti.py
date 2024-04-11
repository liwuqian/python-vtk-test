import vtkmodules.all as vtk

# Load VTK image data
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName("data/output_custom.vti")  # Set the file name
reader.Update()

# Get the loaded image data
image_data = reader.GetOutput()

import time
start_time = time.time()
# Example transformation: translation
translation = vtk.vtkTransform()
translation.Translate(10, 0, 0)  # Translate by 10 units along x-axis

# Apply the transformation to the image data
transform_filter = vtk.vtkTransformFilter()
transform_filter.SetInputData(image_data)
transform_filter.SetTransform(translation)
transform_filter.Update()

# Get the transformed image data
transformed_data = transform_filter.GetOutput()
print("run transform--- %s seconds ---" % (time.time() - start_time))
# print(transformed_data)
# print points of transformed data
points = transformed_data.GetPoints()
# for i in range(points.GetNumberOfPoints()):
#     print(points.GetPoint(i))
# print point loop x,y,z of transformed data
for z in range(10):
    for y in range(10):
        for x in range(10):
            transformed_data
            value = points.GetPoint(x + y * 10 + z * 100)
            # print(f'x:{x}, y:{y}, z:{z}, value:{value}')

# Optionally, you can write the transformed data to a file
# writer = vtk.vtkXMLImageDataWriter()
# writer.SetFileName("data/output_transform.vti")  # Set the output file name
# writer.SetInputData(transformed_data)
# writer.Write()
