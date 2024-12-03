import vtkmodules.all as vtk

# Create a sphere as the object to be clipped
sphere_source = vtk.vtkSphereSource()
sphere_source.SetRadius(5.0)
sphere_source.SetThetaResolution(50)
sphere_source.SetPhiResolution(50)

# Define the near clipping plane
near_clip_plane = vtk.vtkPlane()
near_clip_plane.SetOrigin(0.0, 0.0, 1.0)  # Set near clipping distance from the origin
near_clip_plane.SetNormal(0.0, 0.0, 1.0)  # Normal points into the scene

# Define the far clipping plane
far_clip_plane = vtk.vtkPlane()
far_clip_plane.SetOrigin(0.0, 0.0, 4.0)  # Set far clipping distance from the origin
far_clip_plane.SetNormal(0.0, 0.0, -1.0)  # Normal points opposite to near plane

# Use vtkClipClosedSurface to apply both planes for closed surface clipping
clipper = vtk.vtkClipClosedSurface()
clipper.SetInputConnection(sphere_source.GetOutputPort())
clipper.SetClippingPlanes(vtk.vtkPlaneCollection())  # Create a collection of clipping planes
clipper.GetClippingPlanes().AddItem(near_clip_plane)
clipper.GetClippingPlanes().AddItem(far_clip_plane)

# Set options to ensure the surface is closed and smooth
clipper.SetGenerateFaces(True)  # Generates faces on the clipped regions
clipper.Update()

# Create a mapper and actor for the clipped object
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(clipper.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1.0, 0.6, 0.2)  # Orange color for the clipped surface

# Set up renderer, render window, and interactor
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.3)  # Background color

# add axes to the renderer
axes = vtk.vtkAxesActor()
axes.SetTotalLength(10, 10, 10)
renderer.AddActor(axes)


render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(800, 600)

render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Render and start interaction
render_window.Render()
render_window_interactor.Start()
