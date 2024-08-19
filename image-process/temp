#include <iostream>
#include <vector>
#include <queue>
#include <tuple>

// Define a 3D point
struct Point3D {
    int x, y, z;
    Point3D(int x_, int y_, int z_) : x(x_), y(y_), z(z_) {}
};

// Function to perform region growing in 3D
std::vector<std::vector<std::vector<int>>> regionGrowing(
    const std::vector<std::vector<std::vector<int>>> &mask, 
    const std::vector<Point3D> &seeds, 
    int connectivity) {
    
    int depth = mask.size();
    int height = mask[0].size();
    int width = mask[0][0].size();
    std::vector<std::vector<std::vector<int>>> grownRegion(depth, std::vector<std::vector<int>>(height, std::vector<int>(width, 0)));
    std::queue<Point3D> pointQueue;
    
    // Add seed points to the queue
    for (const auto& seed : seeds) {
        if (mask[seed.z][seed.y][seed.x] > 0) {
            pointQueue.push(seed);
            grownRegion[seed.z][seed.y][seed.x] = 1;
        }
    }

    // Define connectivity
    std::vector<Point3D> neighbors;
    if (connectivity == 6) {
        neighbors = {Point3D(1,0,0), Point3D(-1,0,0), Point3D(0,1,0), Point3D(0,-1,0), Point3D(0,0,1), Point3D(0,0,-1)};
    } else if (connectivity == 18) {
        for (int dz = -1; dz <= 1; ++dz) {
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dx = -1; dx <= 1; ++dx) {
                    if (abs(dx) + abs(dy) + abs(dz) == 2) {
                        neighbors.push_back(Point3D(dx, dy, dz));
                    }
                }
            }
        }
    } else { // 26-connectivity
        for (int dz = -1; dz <= 1; ++dz) {
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dx = -1; dx <= 1; ++dx) {
                    if (dx != 0 || dy != 0 || dz != 0) {
                        neighbors.push_back(Point3D(dx, dy, dz));
                    }
                }
            }
        }
    }

    // Perform region growing
    while (!pointQueue.empty()) {
        Point3D currentPoint = pointQueue.front();
        pointQueue.pop();

        for (const auto& neighbor : neighbors) {
            int nx = currentPoint.x + neighbor.x;
            int ny = currentPoint.y + neighbor.y;
            int nz = currentPoint.z + neighbor.z;

            if (nx >= 0 && nx < width && ny >= 0 && ny < height && nz >= 0 && nz < depth &&
                mask[nz][ny][nx] > 0 && grownRegion[nz][ny][nx] == 0) {
                
                grownRegion[nz][ny][nx] = 1;
                pointQueue.push(Point3D(nx, ny, nz));
            }
        }
    }

    return grownRegion;
}

// Function to isolate the largest connected component in a 3D mask
std::vector<std::vector<std::vector<int>>> isolateLargestComponent(
    const std::vector<std::vector<std::vector<int>>> &mask, 
    int connectivity) {
    
    int depth = mask.size();
    int height = mask[0].size();
    int width = mask[0][0].size();
    
    std::vector<std::vector<std::vector<int>>> labeledMask(depth, std::vector<std::vector<int>>(height, std::vector<int>(width, 0)));
    std::vector<int> componentSizes;
    
    int currentLabel = 1;
    std::queue<Point3D> pointQueue;
    std::vector<Point3D> neighbors;
    if (connectivity == 6) {
        neighbors = {Point3D(1,0,0), Point3D(-1,0,0), Point3D(0,1,0), Point3D(0,-1,0), Point3D(0,0,1), Point3D(0,0,-1)};
    } else if (connectivity == 18) {
        for (int dz = -1; dz <= 1; ++dz) {
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dx = -1; dx <= 1; ++dx) {
                    if (abs(dx) + abs(dy) + abs(dz) == 2) {
                        neighbors.push_back(Point3D(dx, dy, dz));
                    }
                }
            }
        }
    } else { // 26-connectivity
        for (int dz = -1; dz <= 1; ++dz) {
            for (int dy = -1; dy <= 1; ++dy) {
                for (int dx = -1; dx <= 1; ++dx) {
                    if (dx != 0 || dy != 0 || dz != 0) {
                        neighbors.push_back(Point3D(dx, dy, dz));
                    }
                }
            }
        }
    }
    
    for (int z = 0; z < depth; ++z) {
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                if (mask[z][y][x] > 0 && labeledMask[z][y][x] == 0) {
                    int componentSize = 0;
                    pointQueue.push(Point3D(x, y, z));
                    labeledMask[z][y][x] = currentLabel;
                    
                    while (!pointQueue.empty()) {
                        Point3D currentPoint = pointQueue.front();
                        pointQueue.pop();
                        ++componentSize;
                        
                        for (const auto& neighbor : neighbors) {
                            int nx = currentPoint.x + neighbor.x;
                            int ny = currentPoint.y + neighbor.y;
                            int nz = currentPoint.z + neighbor.z;

                            if (nx >= 0 && nx < width && ny >= 0 && ny < height && nz >= 0 && nz < depth &&
                                mask[nz][ny][nx] > 0 && labeledMask[nz][ny][nx] == 0) {
                                
                                labeledMask[nz][ny][nx] = currentLabel;
                                pointQueue.push(Point3D(nx, ny, nz));
                            }
                        }
                    }
                    
                    componentSizes.push_back(componentSize);
                    ++currentLabel;
                }
            }
        }
    }
    
    int largestComponentLabel = std::distance(componentSizes.begin(), std::max_element(componentSizes.begin(), componentSizes.end())) + 1;
    std::vector<std::vector<std::vector<int>>> largestComponent(depth, std::vector<std::vector<int>>(height, std::vector<int>(width, 0)));
    
    for (int z = 0; z < depth; ++z) {
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                if (labeledMask[z][y][x] == largestComponentLabel) {
                    largestComponent[z][y][x] = 1;
                }
            }
        }
    }
    
    return largestComponent;
}

int main() {
    // Load your 3D mask
    // Assuming mask is a 3D volume with 0 for background and 1 for foreground
    // Example mask initialization
    int depth = 100, height = 100, width = 100;
    std::vector<std::vector<std::vector<int>>> mask(depth, std::vector<std::vector<int>>(height, std::vector<int>(width, 0)));

    // Add your 3D mask data loading here

    // Define seed points for the neighboring vertebrae
    std::vector<Point3D> neighborSeeds = {Point3D(50, 50, 50), Point3D(80, 80, 80)}; // Example seeds

    // Perform region growing to segment neighboring parts
    std::vector<std::vector<std::vector<int>>> neighborRegion = regionGrowing(mask, neighborSeeds, 26);

    // Invert the neighbor region to isolate the target vertebra
    std::vector<std::vector<std::vector<int>>> isolated;

    TargetVertebra = mask;
        for (int z = 0; z < depth; ++z) {
            for (int y = 0; y < height; ++y) {
                for (int x = 0; x < width; ++x) {
                    if (neighborRegion[z][y][x] == 1) {
                    TargetVertebra[z][y][x] = 0;
                }
            }
        }
    }
    // Post-process to isolate the largest component
    std::vector<std::vector<std::vector<int>>> isolatedTargetVertebra = isolateLargestComponent(TargetVertebra, 26);

    // Save or use the result as needed

    return 0;

}
