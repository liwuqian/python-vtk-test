import vtk
import os

'''
This script demonstrates how to extract and save a volume of interest (VOI) for each label in a mask.
First, segment the original image using a multi-label mask.
Second, extract the VOI for each segmented label to reduce the image size.
The VOI is saved as a separate MHD file for each label.
'''

def find_label_bounds_vtk_sequential(image_data):
    """
    Finds bounding boxes for all labels in a single pass using VTK.
    
    Args:
        image_data: vtkImageData representing the mask.
    
    Returns:
        Dictionary of label bounds in voxel index space.
    """
    dims = image_data.GetDimensions()
    scalars = image_data.GetPointData().GetScalars()
    num_points = scalars.GetNumberOfTuples()

    label_bounds_temp = {}
    for idx in range(num_points):
        label = int(scalars.GetTuple1(idx))
        if label == 0:  # Skip background
            continue

        z = idx // (dims[0] * dims[1])
        y = (idx % (dims[0] * dims[1])) // dims[0]
        x = idx % dims[0]

        if label not in label_bounds_temp:
            label_bounds_temp[label] = [x, x, y, y, z, z]
        else:
            bounds = label_bounds_temp[label]
            bounds[0] = min(bounds[0], x)
            bounds[1] = max(bounds[1], x)
            bounds[2] = min(bounds[2], y)
            bounds[3] = max(bounds[3], y)
            bounds[4] = min(bounds[4], z)
            bounds[5] = max(bounds[5], z)

    label_bounds = {label: tuple(bounds) for label, bounds in label_bounds_temp.items()}
    return label_bounds

def process_image_and_mask(image_file, mask_file, output_dir):
    """
    Process image and mask to extract and save VOI for each label.
    """
    # Read image
    reader_image = vtk.vtkNIFTIImageReader()
    reader_image.SetFileName(image_file)
    reader_image.Update()
    image_data = reader_image.GetOutput()
    origin = image_data.GetOrigin()
    spacing = image_data.GetSpacing()
    dims = image_data.GetDimensions()
    print(f"Image origin: {origin}, spacing: {spacing}, dims: {dims}")

    # Read mask
    reader_mask = vtk.vtkNIFTIImageReader()
    reader_mask.SetFileName(mask_file)
    reader_mask.Update()
    mask_data = reader_mask.GetOutput()
    mask_dims = mask_data.GetDimensions()
    print(f"Mask dims: {mask_dims}")

    # Ensure image and mask dimensions match
    if dims != mask_dims:
        raise ValueError("Image and mask dimensions do not match!")

    # Find bounds
    print("Begin find_label_bounds_vtk_sequential")
    bounds_dict = find_label_bounds_vtk_sequential(mask_data)
    print("End find_label_bounds_vtk_sequential")

    for label, bounds in bounds_dict.items():
        min_x, max_x, min_y, max_y, min_z, max_z = bounds
        print(f"Label {label}: bounds (voxel indices) {bounds}")

        # Validate bounds against image dimensions
        if (min_x < 0 or max_x >= dims[0] or 
            min_y < 0 or max_y >= dims[1] or 
            min_z < 0 or max_z >= dims[2]):
            print(f"Skipping label {label}: Bounds out of range")
            continue

        # Use bounds directly as VOI (no conversion needed)
        voi_extent = [min_x, max_x, min_y, max_y, min_z, max_z]
        print(f"Label {label}: VOI extent {voi_extent}")

        # Threshold mask for this label
        threshold = vtk.vtkImageThreshold()
        threshold.SetInputConnection(reader_mask.GetOutputPort())
        threshold.ThresholdBetween(label, label)
        threshold.SetInValue(1)
        threshold.SetOutValue(0)
        threshold.Update()

        # Apply mask to extracted image
        image_mask = vtk.vtkImageMask()
        image_mask.SetInputConnection(0, reader_image.GetOutputPort())
        image_mask.SetInputConnection(1, threshold.GetOutputPort())
        image_mask.SetMaskedOutputValue(image_data.GetScalarRange()[0])
        image_mask.Update()

        # Extract VOI from image
        extract_voi = vtk.vtkExtractVOI()
        extract_voi.SetInputConnection(image_mask.GetOutputPort())
        extract_voi.SetVOI(voi_extent)
        extract_voi.Update()

        # Save output
        output_file = f"{output_dir}/label_{label}_voi.mhd"
        writer = vtk.vtkMetaImageWriter()
        writer.SetFileName(output_file)
        writer.SetInputConnection(extract_voi.GetOutputPort())
        writer.Write()
        print(f"Saved label {label} to {output_file}")

if __name__ == "__main__":
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    process_image_and_mask("data/liver_57.nii.gz", "data/liver_57_multilabel.nii.gz", output_dir)