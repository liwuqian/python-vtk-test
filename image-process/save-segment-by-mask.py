import vtkmodules.all as vtk

'''
This script demonstrates how to segment a 3D image using a multi-label mask.
The mask image is used to segment the original image.
The segmented image is saved as a separate MHD file for each label in the mask.
'''

# Read the original NIFTI file (.nii.gz)
reader_image = vtk.vtkNIFTIImageReader()
reader_image.SetFileName("data/liver_57.nii.gz")
reader_image.Update()

#  get minimal pixel value
image_data = reader_image.GetOutput()
scalar_range = image_data.GetScalarRange()
min_pixel_value = scalar_range[0]
max_pixel_value = scalar_range[1]

# Read the mask NIFTI file (.nii.gz)
reader_mask = vtk.vtkNIFTIImageReader()
reader_mask.SetFileName("data/liver_57_multilabel.nii.gz")
reader_mask.Update()

# Get the unique labels from the 3D mask
mask_data = reader_mask.GetOutput()
mask_range = mask_data.GetScalarRange()
min_label, max_label = int(mask_range[0]), int(mask_range[1])

print(f"Segmenting labels from {min_label} to {max_label}...")

for label in range(min_label, max_label + 1):
    if label == 0:
        continue  # Skip background
    # if label != 19:
    #     continue

    # Threshold to extract only the current label
    threshold = vtk.vtkImageThreshold()
    threshold.SetInputConnection(reader_mask.GetOutputPort())  # Use full 3D mask
    threshold.ThresholdBetween(label, label)  # Isolate this label
    threshold.SetInValue(1)  # Set label region to 1
    threshold.SetOutValue(0)
    threshold.Update()

    # Check if the mask exists
    mask_exists = threshold.GetOutput().GetScalarRange()[1] > 0
    if not mask_exists:
        continue
    
    print("threshold scaler range: ", threshold.GetOutput().GetScalarRange())
    image_mask = vtk.vtkImageMask()
    # set mask default value as min_pixel_value
    image_mask.SetMaskedOutputValue(min_pixel_value)
    image_mask.SetInputConnection(0, reader_image.GetOutputPort())
    image_mask.SetInputConnection(1, threshold.GetOutputPort())
    image_mask.Update()
    print("image_mask scaler range: ", image_mask.GetOutput().GetScalarRange())
    
    # Save the segmented mask for the current label
    mhd_writer = vtk.vtkMetaImageWriter()
    mhd_writer.SetFileName(f"output/liver_57_label_{label}.mhd")  # Output filename
    mhd_writer.SetInputConnection(image_mask.GetOutputPort())  # Save full 3D mask
    mhd_writer.Write()

    print(f"Saved segmented mask for label {label} as MHD.")

print("All labels segmented and saved successfully.")
