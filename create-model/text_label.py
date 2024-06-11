import vtkmodules.all as vtk

# Create the renderer
renderer = vtk.vtkRenderer()

# Create the render window
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

# Create the render window interactor
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)

# Create a text actor
textActor = vtk.vtkTextActor()
textActor.SetInput("This is a label")

# Set the text properties
textProperty = textActor.GetTextProperty()
textProperty.SetFontSize(24)
textProperty.SetColor(1.0, 0.0, 0.0)  # RGB color: red

# Set the position of the text (in pixels)
textActor.SetPosition(50, 50)

# Add the text actor to the renderer
renderer.AddActor2D(textActor)

axes = vtk.vtkAxesActor()
renderer.AddActor(axes)

# Initialize and start the render window interactor
renderWindow.Render()
renderWindowInteractor.Initialize()
renderWindowInteractor.Start()
