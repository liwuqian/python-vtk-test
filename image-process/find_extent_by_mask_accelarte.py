from numba import njit
import numpy as np
import vtk
from vtk.util import numpy_support

'''
    Find bounding boxes for all labels in a single pass by looping over pixels.
'''

@njit
def find_label_bounds_sequential(scalars):
    """
    Finds bounding boxes for all labels in a single pass by looping over pixels.
    
    Args:
        scalars: 3D NumPy array of the mask.
    
    Returns:
        Dictionary-like structure (array) with bounds for each label.
    """
    dims = scalars.shape
    # Temporary storage: {label: [min_x, max_x, min_y, max_y, min_z, max_z, count]}
    # Use a large enough array to hold all possible labels (adjust based on data)
    max_labels = 1000  # Adjust based on your max label value
    bounds_array = np.full((max_labels, 7), np.inf, dtype=np.float64)
    bounds_array[:, 1] = -np.inf  # max_x
    bounds_array[:, 3] = -np.inf  # max_y
    bounds_array[:, 5] = -np.inf  # max_z
    bounds_array[:, 6] = 0       # count (to track if label exists)

    # Single pass over all pixels
    for z in range(dims[2]):
        for y in range(dims[1]):
            for x in range(dims[0]):
                label = int(scalars[x, y, z])
                if label == 0 or label >= max_labels:
                    continue  # Skip background or out-of-range labels
                bounds = bounds_array[label]
                bounds[0] = min(bounds[0], x)  # min_x
                bounds[1] = max(bounds[1], x)  # max_x
                bounds[2] = min(bounds[2], y)  # min_y
                bounds[3] = max(bounds[3], y)  # max_y
                bounds[4] = min(bounds[4], z)  # min_z
                bounds[5] = max(bounds[5], z)  # max_z
                bounds[6] += 1                  # Increment count

    # Filter and convert to dictionary-like output
    valid_bounds = []
    for label in range(max_labels):
        if bounds_array[label, 6] > 0:  # If label exists (count > 0)
            valid_bounds.append([
                label,
                bounds_array[label, 0],  # min_x
                bounds_array[label, 1],  # max_x
                bounds_array[label, 2],  # min_y
                bounds_array[label, 3],  # max_y
                bounds_array[label, 4],  # min_z
                bounds_array[label, 5]   # max_z
            ])

    return np.array(valid_bounds, dtype=np.float64)

def get_label_bounds_sequential_wrapper(image_data):
    """
    Wrapper function to interface with VTK.
    
    Args:
        image_data: vtkImageData representing the mask.
    
    Returns:
        Dictionary of label bounds.
    """
    dims = image_data.GetDimensions()
    scalars = numpy_support.vtk_to_numpy(image_data.GetPointData().GetScalars())
    scalars = scalars.reshape(dims[2], dims[1], dims[0]).transpose(2, 1, 0)

    bounds_array = find_label_bounds_sequential(scalars)
    
    # Convert to dictionary
    label_bounds = {}
    for row in bounds_array:
        label = int(row[0])
        label_bounds[label] = (int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]))

    return label_bounds

# Example usage
if __name__ == "__main__":
    # Read mask
    reader_mask = vtk.vtkNIFTIImageReader()
    reader_mask.SetFileName("data/liver_57_multilabel.nii.gz")
    reader_mask.Update()

    # Get bounds
    bounds_dict = get_label_bounds_sequential_wrapper(reader_mask.GetOutput())
    for label, bounds in bounds_dict.items():
        print(f"Label {label}: {bounds}")