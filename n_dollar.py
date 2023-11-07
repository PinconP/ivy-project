import math
import tkinter as tk
from tkinter import simpledialog, messagebox
from point import Point
from gesture import Gesture
from ivy.ivy import IvyServer

# Constants
NumPoints = 64
SquareSize = 250.0
HalfDiagonal = 0.5 * math.sqrt(250 * 250 + 250 * 250)
AngleRange = 45.0
AnglePrecision = 2.0
Phi = 0.5 * (-1.0 + math.sqrt(5.0))  # Golden Ratio
GENERAL_THRESHOLD = 5000.0  # Must be tuned according to the

# Distance between points


def distance(p1, p2):
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.sqrt(dx * dx + dy * dy)


# Resample points in a gesture


def resample(points):
    I = path_length(points) / (NumPoints - 1)
    D = 0.0
    new_points = [points[0]]
    i = 1
    while i < len(points):
        d = distance(points[i - 1], points[i])
        if D + d >= I:
            qx = points[i - 1].x + ((I - D) / d) * \
                (points[i].x - points[i - 1].x)
            qy = points[i - 1].y + ((I - D) / d) * \
                (points[i].y - points[i - 1].y)
            q = Point(qx, qy)
            new_points.append(q)
            points.insert(i, q)
            D = 0.0
        else:
            D += d
        i += 1
    return new_points


# Compute the path length of a list of points


def path_length(points):
    d = 0.0
    for i in range(1, len(points)):
        d += distance(points[i - 1], points[i])
    return d


# Scale the points to fit within a square of size SquareSize


def scale(points):
    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)

    scale_factor = SquareSize / max(max_x - min_x, max_y - min_y)

    new_points = []
    for p in points:
        qx = p.x * scale_factor
        qy = p.y * scale_factor
        new_points.append(Point(qx, qy))

    return new_points


# Translate points to the origin


def translate_to_origin(points):
    centroid_x = sum(p.x for p in points) / len(points)
    centroid_y = sum(p.y for p in points) / len(points)

    new_points = []
    for p in points:
        qx = p.x - centroid_x
        qy = p.y - centroid_y
        new_points.append(Point(qx, qy))

    return new_points


# Recognize a gesture


def recognize(gesture, templates):
    min_distance = float("inf")
    best_match = None

    for template in templates:
        d = distance_at_best_angle(gesture.points, template)
        if d < min_distance:
            min_distance = d
            best_match = template.name

    return best_match, min_distance


def distance_at_best_angle(points, template):
    Phi = 0.5 * (-1.0 + (5.0**0.5))
    theta_a = -45.0
    theta_b = 45.0
    threshold = 2.0

    d1 = distance_at_angle(points, template, Phi *
                           theta_a + (1 - Phi) * theta_b)
    d2 = distance_at_angle(points, template, (1 - Phi)
                           * theta_a + Phi * theta_b)

    while abs(theta_a - theta_b) > threshold:
        if d1 < d2:
            theta_b = Phi * theta_a + (1 - Phi) * theta_b
            d2 = d1
            d1 = distance_at_angle(
                points, template, Phi * theta_a + (1 - Phi) * theta_b
            )
        else:
            theta_a = (1 - Phi) * theta_a + Phi * theta_b
            d1 = d2
            d2 = distance_at_angle(
                points, template, (1 - Phi) * theta_a + Phi * theta_b
            )

    return min(d1, d2)


# Helper function for distance_at_best_angle


def distance_at_angle(points, template, theta):
    new_points = rotate_by(points, theta)
    d = path_distance(new_points, template.points)
    return d


# Rotate points by a given angle


def rotate_by(points, theta):
    centroid_x = sum(p.x for p in points) / len(points)
    centroid_y = sum(p.y for p in points) / len(points)

    angle = math.radians(theta)
    cos_val = math.cos(angle)
    sin_val = math.sin(angle)

    new_points = []
    for p in points:
        qx = (p.x - centroid_x) * cos_val - \
            (p.y - centroid_y) * sin_val + centroid_x
        qy = (p.x - centroid_x) * sin_val + \
            (p.y - centroid_y) * cos_val + centroid_y
        new_points.append(Point(qx, qy))

    return new_points


def path_distance(points1, points2):
    d = 0
    n = min(len(points1), len(points2))  # Take the length of the shorter list
    for i in range(n):
        d += distance(points1[i], points2[i])
    return d


# Global variables
strokes = []
current_stroke = []
templates = []

# Capture points when the mouse is pressed and dragged


def on_drag(event):
    x, y = event.x, event.y
    canvas.create_oval(x, y, x + 5, y + 5, fill="black")
    current_stroke.append(Point(x, y))


# End the current stroke when the mouse is released


def on_release(event):
    global strokes, current_stroke
    if current_stroke:
        strokes.append(current_stroke)
        current_stroke = []


# Clear the canvas and strokes


def clear_canvas():
    global strokes
    canvas.delete("all")
    strokes = []


# Save a new gesture template


def save_template():
    global strokes, templates
    if not strokes:
        return
    name = simpledialog.askstring("Input", "Enter gesture name:")
    if name:
        points = [point for stroke in strokes for point in stroke]
        points = resample(points)
        points = scale(points)
        points = translate_to_origin(points)
        templates.append(Gesture(name, points))
    clear_canvas()


# Recognize a gesture based on the current strokes


def recognize_gesture():
    global strokes, templates, recognized_gesture_name
    if not strokes or not templates:
        return
    points = [point for stroke in strokes for point in stroke]
    points = resample(points)
    points = scale(points)
    points = translate_to_origin(points)
    gesture = Gesture("unknown", points)
    name, min_distance = recognize(gesture, templates)
    if name and min_distance < GENERAL_THRESHOLD:
        messagebox.showinfo("Recognized", f"Gesture recognized as {name}")
    else:
        messagebox.showinfo("Not recognized", "Gesture not recognized")
    # Before returning, update the recognized_gesture_name with the gesture name
    recognized_gesture_name = name
    clear_canvas()


class MyAgentNDollar(IvyServer):
    def __init__(self, name):
        IvyServer.__init__(self, "MonAgentNDollar")
        self.name = name
        self.start("127.255.255.255:2010")
        self.bind_msg(self.handle_hello, "^ping(.*)")

    def handle_hello(self, agent, arg):
        print("[Agent %s] GOT pinged from %r" % (self.name, agent))
        self.send_msg(recognized_gesture_name)


a = MyAgentNDollar("NDollar")
recognized_gesture_name = ""  # Global variable to store the gesture name

# Create the Tkinter GUI
root = tk.Tk()
root.title("Gesture Recognizer")

# Create a string variable to hold the recognized gesture text
gesture_var = tk.StringVar()

# Create canvas to draw gestures
canvas = tk.Canvas(root, bg="white", width=400, height=400)
canvas.pack(pady=20)

# Bind mouse events to the canvas
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)

# Create a label to display the recognized gesture
gesture_label = tk.Label(
    root, textvariable=gesture_var, font=('Helvetica', 16))
gesture_label.pack(pady=20)

# Add buttons
save_button = tk.Button(root, text="Save Gesture", command=save_template)
save_button.pack(side=tk.LEFT, padx=10, pady=10)

recognize_button = tk.Button(
    root, text="Recognize Gesture", command=recognize_gesture)
recognize_button.pack(side=tk.LEFT, padx=10, pady=10)

clear_button = tk.Button(root, text="Clear", command=clear_canvas)
clear_button.pack(side=tk.RIGHT, padx=10, pady=10)


root.mainloop()
