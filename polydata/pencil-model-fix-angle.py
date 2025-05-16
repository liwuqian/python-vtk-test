import math
import vtkmodules.all as vtk
from vtkmodules.util.colors import tomato
from vtkmodules.vtkInteractionWidgets import vtkSliderRepresentation2D, vtkSliderWidget

# === Initial Parameters ===
initial_radius = 1.0
initial_total_height = 10.0
cone_angle_deg = 30  # Fixed tip angle

# === Create Pencil Geometry Function ===
def create_pencil(radius, total_height, cone_angle_deg):
    # Compute cone height from angle
    half_angle_rad = math.radians(cone_angle_deg / 2)
    cone_height = radius / math.tan(half_angle_rad)
    cylinder_height = total_height - cone_height
    if cylinder_height < 0:
        cylinder_height = 0.01  # Prevent invalid geometry

    # Cylinder
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetRadius(radius)
    cylinder.SetHeight(cylinder_height)
    cylinder.SetResolution(50)
    cylinder.SetCenter(0, -cylinder_height * 0.5, 0)
    cylinder.Update()

    # Cone
    cone = vtk.vtkConeSource()
    cone.SetRadius(radius)
    cone.SetHeight(cone_height)
    cone.SetResolution(50)
    cone.SetDirection(0, -1, 0)
    cone.SetCenter(0, -cylinder_height - cone_height * 0.5, 0)
    cone.Update()

    # Combine
    appendFilter = vtk.vtkAppendPolyData()
    appendFilter.AddInputConnection(cylinder.GetOutputPort())
    appendFilter.AddInputConnection(cone.GetOutputPort())
    appendFilter.Update()

    return appendFilter

# === Initial Pencil ===
pencil = create_pencil(initial_radius, initial_total_height, cone_angle_deg)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(pencil.GetOutput())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(tomato)

# === Renderer Setup ===
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.1, 0.1)

renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(800, 800)
renderWindow.SetPosition(500, 200)  # Set the window position

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(renderWindow)

# === Sliders ===
def create_slider(title, minval, maxval, value, pos_y, callback):
    sliderRep = vtkSliderRepresentation2D()
    sliderRep.SetMinimumValue(minval)
    sliderRep.SetMaximumValue(maxval)
    sliderRep.SetValue(value)
    sliderRep.SetTitleText(title)
    sliderRep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    sliderRep.GetPoint1Coordinate().SetValue(0.1, pos_y)
    sliderRep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    sliderRep.GetPoint2Coordinate().SetValue(0.9, pos_y)
    sliderRep.SetSliderLength(0.02)
    sliderRep.SetSliderWidth(0.03)
    sliderRep.SetEndCapLength(0.01)
    sliderRep.SetTitleHeight(0.02)
    sliderRep.SetLabelHeight(0.02)

    sliderWidget = vtkSliderWidget()
    sliderWidget.SetInteractor(interactor)
    sliderWidget.SetRepresentation(sliderRep)
    sliderWidget.SetAnimationModeToAnimate()
    sliderWidget.EnabledOn()
    sliderWidget.AddObserver("InteractionEvent", callback)
    return sliderWidget

# === Callback to Update Pencil ===
def update_pencil(obj, event):
    radius = radius_slider.GetRepresentation().GetValue()
    height = height_slider.GetRepresentation().GetValue()
    new_pencil = create_pencil(radius, height, cone_angle_deg)
    mapper.SetInputData(new_pencil.GetOutput())
    mapper.Update()
    renderWindow.Render()

# === Create Sliders ===
radius_slider = create_slider("Radius", 0.1, 2.0, initial_radius, 0.1, update_pencil)
height_slider = create_slider("Height", 2.0, 20.0, initial_total_height, 0.2, update_pencil)

# === Add Axes ===
axes = vtk.vtkAxesActor()
axes.SetTotalLength(5, 5, 5)
renderer.AddActor(axes)

# === Start Interaction ===
renderWindow.Render()
interactor.Start()
