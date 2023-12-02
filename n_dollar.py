import math
import tkinter as tk
from tkinter import simpledialog, messagebox
from point import Point
from gesture import Gesture
from ivy.ivy import IvyServer
import pickle

# Constants
NumPoints = 64
SquareSize = 250.0
HalfDiagonal = 0.5 * math.sqrt(250 * 250 + 250 * 250)
AngleRange = 45.0
AnglePrecision = 2.0
Phi = 0.5 * (-1.0 + math.sqrt(5.0))  # Golden Ratio
GENERAL_THRESHOLD = 5000.0  # Must be tuned according to the

# Global variables
strokes = []
current_stroke = []
templates = []

# Distance between points


class MyAgentNDollar(IvyServer):
    def __init__(self, name):
        IvyServer.__init__(self, "MonAgentNDollar")
        self.name = name
        self.start("127.255.255.255:2010")

        self.need_form = False
        self.canvas = None  # Ajoutez cette ligne pour initialiser self.canvas

        # Charger les templates existants au démarrage
        self.templates = self.load_templates()

        self.bind_msg(self.handle_form_request, "^need form(.*)")

    def set_canvas(self, canvas):
        self.canvas = canvas

    def handle_form_request(self, agent, arg):
        print("J'ai reçu need form")
        self.need_form = True
        print("Need form :", self.need_form)

        #################################################################
        # Commencer la reconnaissance de la forme
        self.recognizing_form = True
        print("Commence à reconnaître la forme...")
        #################################################################

    # Resample points in a gesture

    def resample(self, points):
        I = self.path_length(points) / (NumPoints - 1)
        D = 0.0
        new_points = [points[0]]
        i = 1
        while i < len(points):
            d = self.distance(points[i - 1], points[i])
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

    # Scale the points to fit within a square of size SquareSize
    def scale(self, points):
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
    def translate_to_origin(self, points):
        centroid_x = sum(p.x for p in points) / len(points)
        centroid_y = sum(p.y for p in points) / len(points)

        new_points = []
        for p in points:
            qx = p.x - centroid_x
            qy = p.y - centroid_y
            new_points.append(Point(qx, qy))

        return new_points

    # Recognize a gesture based on the current strokes
    def recognize_gesture(self):
        global strokes, templates, recognized_gesture_name

        if not strokes or not templates:
            return

        points = [point for stroke in strokes for point in stroke]
        points = self.resample(points)
        points = self.scale(points)
        points = self.translate_to_origin(points)
        gesture = Gesture("unknown", points)
        name, min_distance = self.recognize(gesture, templates)

        if min_distance < GENERAL_THRESHOLD:
            confidence = (1.0 - min_distance / GENERAL_THRESHOLD) * 100

            if confidence >= 70.0:
                messagebox.showinfo(
                    "Recognized", f"Gesture recognized as {name} with {confidence:.2f}% confidence")
                recognized_gesture_name = name

                # Envoyer un message sur le bus Ivy
                self.send_msg("forme " + recognized_gesture_name)
                print("Forme envoyée")

            else:
                messagebox.showinfo(
                    "Not recognized", f"Gesture does not meet confidence threshold (confidence: {confidence:.2f}%). Please Try again.")
                recognized_gesture_name = ""
        else:
            messagebox.showinfo("Not recognized", "Gesture not recognized")

        # Before returning, update the recognized_gesture_name with the gesture name
        recognized_gesture_name = name
        self.clear_canvas()
        self.recognizing_form = False

    # Clear the canvas and strokes
    def clear_canvas(self):
        global strokes
        self.canvas.delete("all")
        strokes = []

    def distance(self, p1, p2):
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        return math.sqrt(dx * dx + dy * dy)

    # Compute the path length of a list of points
    def path_length(self, points):
        d = 0.0
        for i in range(1, len(points)):
            d += self.distance(points[i - 1], points[i])
        return d

    # Recognize a gesture
    def recognize(self, gesture, templates):
        min_distance = float("inf")
        best_match = None

        for template in templates:
            d = self.distance_at_best_angle(gesture.points, template)
            if d < min_distance:
                min_distance = d
                best_match = template.name

        return best_match, min_distance

    def distance_at_best_angle(self, points, template):
        Phi = 0.5 * (-1.0 + (5.0**0.5))
        theta_a = -45.0
        theta_b = 45.0
        threshold = 2.0

        d1 = self.distance_at_angle(points, template, Phi *
                                    theta_a + (1 - Phi) * theta_b)
        d2 = self.distance_at_angle(points, template, (1 - Phi)
                                    * theta_a + Phi * theta_b)

        while abs(theta_a - theta_b) > threshold:
            if d1 < d2:
                theta_b = Phi * theta_a + (1 - Phi) * theta_b
                d2 = d1
                d1 = self.distance_at_angle(
                    points, template, Phi * theta_a + (1 - Phi) * theta_b
                )
            else:
                theta_a = (1 - Phi) * theta_a + Phi * theta_b
                d1 = d2
                d2 = self.distance_at_angle(
                    points, template, (1 - Phi) * theta_a + Phi * theta_b
                )

        return min(d1, d2)

    # Helper function for distance_at_best_angle
    def distance_at_angle(self, points, template, theta):
        new_points = self.rotate_by(points, theta)
        d = self.path_distance(new_points, template.points)
        return d

    # Rotate points by a given angle
    def rotate_by(self, points, theta):
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

    def path_distance(self, points1, points2):
        d = 0
        # Take the length of the shorter list
        n = min(len(points1), len(points2))
        for i in range(n):
            d += self.distance(points1[i], points2[i])
        return d

    # Capture points when the mouse is pressed and dragged
    def on_drag(self, event):
        x, y = event.x, event.y
        canvas.create_oval(x, y, x + 5, y + 5, fill="black")
        current_stroke.append(Point(x, y))

    # End the current stroke when the mouse is released
    def on_release(self, event):
        global strokes, current_stroke
        if current_stroke:
            strokes.append(current_stroke)
            current_stroke = []

    # Charger les templates à partir d'un fichier (au démarrage de l'application)
    def load_templates(self):
        try:
            with open("templates.pkl", "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            print("Templates file not found, starting with empty templates")
            return []
        except Exception as e:
            print("Error loading templates:", e)
            return []

    # Sauvegarder les templates dans un fichier
    def save_templates(self):
        global templates
        try:
            with open("templates.pkl", "wb") as file:
                pickle.dump(templates, file)
        except Exception as e:
            print("Error saving templates:", e)

    # Save a new gesture template

    def save_template(self):
        global strokes, templates
        if not strokes:
            return
        name = simpledialog.askstring("Input", "Enter gesture name:")
        if name:
            points = [point for stroke in strokes for point in stroke]
            points = self.resample(points)
            points = self.scale(points)
            points = self.translate_to_origin(points)
            templates.append(Gesture(name, points))
            self.save_templates()  # Save the updated list of templates
        self.clear_canvas()

    def show_and_edit_templates(self):
        global templates

        def delete_template(self):
            global templates
            selected_index = listbox.curselection()
            if selected_index:
                selected_template = templates[selected_index[0]]
                templates.remove(selected_template)
                listbox.delete(selected_index)
                self.save_templates()  # Update the saved file after deletion

        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Templates")

        listbox = tk.Listbox(edit_window, selectmode=tk.SINGLE)
        for template in templates:
            listbox.insert(tk.END, template.name)
        listbox.pack(pady=10)

        delete_button = tk.Button(
            edit_window, text="Delete Template", command=delete_template)
        delete_button.pack(pady=5)

        close_button = tk.Button(
            edit_window, text="Close", command=edit_window.destroy)
        close_button.pack(pady=5)

        edit_window.mainloop()


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

# canvas est la référence à votre objet canvas créé dans l'interface graphique
a.set_canvas(canvas)

# Bind mouse events to the canvas
canvas.bind("<B1-Motion>", a.on_drag)
canvas.bind("<ButtonRelease-1>", a.on_release)

# Create a label to display the recognized gesture
gesture_label = tk.Label(
    root, textvariable=gesture_var, font=('Helvetica', 16))
gesture_label.pack(pady=20)

# Add buttons
save_button = tk.Button(root, text="Save Gesture", command=a.save_template)
save_button.pack(side=tk.LEFT, padx=10, pady=10)

recognize_button = tk.Button(
    root, text="Recognize Gesture", command=a.recognize_gesture)
recognize_button.pack(side=tk.LEFT, padx=10, pady=10)

clear_button = tk.Button(root, text="Clear", command=a.clear_canvas)
clear_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Other buttons (V2)
# Ajouter un bouton pour afficher et éditer la base de données
edit_button = tk.Button(root, text="Edit Templates",
                        command=a.show_and_edit_templates)
edit_button.pack(side=tk.LEFT, padx=10, pady=10)


root.mainloop()
