import itk

input_filename = "data/origin.mhd"

image = itk.imread(input_filename)

median = itk.median_image_filter(image, radius=2)

# itk.imwrite(median, output_filename)