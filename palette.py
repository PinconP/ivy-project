import pygame
import math
from abc import ABC, abstractmethod
from enum import Enum
import time


class FSM(Enum):
    INITIAL = "Etat Initial"
    AFFICHER_FORMES = "Afficher Formes"
    DEPLACER_FORMES_SELECTION = "Deplacer Formes Selection"
    DEPLACER_FORMES_DESTINATION = "Deplacer Formes Destination"


class Forme(ABC):
    def __init__(self, x, y):
        self.origin = (x, y)
        self.color = (127, 127, 127)  # Default color as RGB tuple

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color

    @abstractmethod
    def update(self):
        pass

    def get_location(self):
        return self.origin

    def set_location(self, x, y):
        self.origin = (x, y)

    @abstractmethod
    def is_clicked(self, pos):
        pass

    def distance(self, A, B):
        dx = B[0] - A[0]
        dy = B[1] - A[1]
        return math.sqrt(dx ** 2 + dy ** 2)

    @abstractmethod
    def perimetre(self):
        pass

    @abstractmethod
    def aire(self):
        pass


class Cercle(Forme):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.rayon = 80

    def update(self):
        pygame.draw.circle(win, self.color, self.origin, self.rayon)

    def is_clicked(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        return distance <= self.rayon // 2

    def perimetre(self):
        return 2 * math.pi * self.rayon

    def aire(self):
        return math.pi * self.rayon ** 2


class Rectangle(Forme):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.longueur = 60

    def update(self):
        pygame.draw.rect(win, self.color, (self.origin[0], self.origin[1],
                         self.longueur, self.longueur))

    def is_clicked(self, pos):
        x, y = pos
        x0, y0 = self.x, self.y
        if (x > x0) and (x < x0 + self.longueur) and (y > y0) and (y < y0 + self.longueur):
            return True
        else:
            return False

    def perimetre(self):
        return self.longueur * 4

    def aire(self):
        return self.longueur * self.longueur


class Triangle:
    def __init__(self, p):
        self.origin = p
        self.color = (127, 127, 127)  # Default color: grey

        self.A = p
        self.B = (p[0] + 40, p[1] + 60)
        self.C = (p[0] - 40, p[1] + 60)

    def set_location(self, p):
        self.origin = p
        self.A = p
        self.B = (p[0] + 40, p[1] + 60)
        self.C = (p[0] - 40, p[1] + 60)

    def update(self):
        pygame.draw.polygon(win, self.color, [self.A, self.B, self.C])

    def is_clicked(self, M):
        # Calculate cross products to determine if point M is inside the triangle
        def cross_product(A, B):
            return A[0] * B[1] - A[1] * B[0]

        def dot_product(A, B):
            return A[0] * B[0] + A[1] * B[1]

        AB = (self.B[0] - self.A[0], self.B[1] - self.A[1])
        AC = (self.C[0] - self.A[0], self.C[1] - self.A[1])
        AM = (M[0] - self.A[0], M[1] - self.A[1])

        BA = (self.A[0] - self.B[0], self.A[1] - self.B[1])
        BC = (self.C[0] - self.B[0], self.C[1] - self.B[1])
        BM = (M[0] - self.B[0], M[1] - self.B[1])

        CA = (self.A[0] - self.C[0], self.A[1] - self.C[1])
        CB = (self.B[0] - self.C[0], self.B[1] - self.C[1])
        CM = (M[0] - self.C[0], M[1] - self.C[1])

        if dot_product(cross_product(AB, AM), cross_product(AM, AC)) >= 0 and \
           dot_product(cross_product(BA, BM), cross_product(BM, BC)) >= 0 and \
           dot_product(cross_product(CA, CM), cross_product(CM, CB)) >= 0:
            return True
        else:
            return False

    def perimeter(self):
        def distance(A, B):
            return math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)

        return distance(self.A, self.B) + distance(self.B, self.C) + distance(self.C, self.A)

    def area(self):
        s = self.perimeter() / 2
        return math.sqrt(s * (s - distance(self.A, self.B)) * (s - distance(self.B, self.C)) * (s - distance(self.C, self.A)))


class Losange(Forme):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.A = (x, y)
        self.B = (x + 40, y + 60)
        self.C = (x, y + 120)
        self.D = (x - 40, y + 60)

    def set_location(self, x, y):
        super().set_location(x, y)
        self.A = (x, y)
        self.B = (x + 40, y + 60)
        self.C = (x, y + 120)
        self.D = (x - 40, y + 60)

    def update(self):
        pygame.draw.polygon(win, self.color, [self.A, self.B, self.C, self.D])

    def is_clicked(self, pos):
        M = pos
        if round(self.aire_triangle(self.A, M, self.D) +
                 self.aire_triangle(self.A, M, self.B) +
                 self.aire_triangle(self.B, M, self.C) +
                 self.aire_triangle(self.C, M, self.D)) == round(self.aire()):
            return True
        else:
            return False

    def perimetre(self):
        return self.distance(self.A, self.B) * 2 + self.distance(self.B, self.C) * 2

    def aire(self):
        AC = self.distance(self.A, self.C)
        BD = self.distance(self.B, self.D)
        return (AC * BD) / 2

    def perimetre_triangle(self, I, J, K):
        return self.distance(I, J) + self.distance(J, K) + self.distance(K, I)

    def aire_triangle(self, I, J, K):
        s = self.perimetre_triangle(I, J, K) / 2
        aire = s * (s - self.distance(I, J)) * \
            (s - self.distance(J, K)) * (s - self.distance(K, I))
        return math.sqrt(aire)


"""# States
INITIAL = 0
AFFICHER_FORMES = 1
DEPLACER_FORMES_SELECTION = 2
DEPLACER_FORMES_DESTINATION = 3
"""
# Initialize pygame
pygame.init()

# Window settings
width, height = 1600, 1200
win = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Palette multimodale")

# Variables
formes = []  # List of shapes
mae = FSM.INITIAL  # Finite State Machine
indice_forme = -1  # Index of the active shape

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Helper function for distance calculation


def distance(A, B):
    return math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)


# Initialize an empty string for command input
command_input = ""

"""while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            # Capture the pressed keys and add them to the command_input string
            if event.unicode.isalpha() or event.unicode.isspace() and event.key != pygame.K_RETURN:
                command_input += event.unicode

            elif event.key == pygame.K_BACKSPACE:
                command_input = command_input[:-1]

            elif event.key == pygame.K_RETURN:  # Enter key

                x, y = pygame.mouse.get_pos()
                print
                # Process the complete command_input string
                if command_input == "draw rectangle here":
                    f = Rectangle(x, y)
                    formes.append(f)
                    current_state = FSM.AFFICHER_FORMES
                    print('Rectangle drawn')
                elif command_input == "draw circle here":
                    f = Cercle(x, y)
                    formes.append(f)
                    current_state = FSM.AFFICHER_FORMES
                    print('Circle drawn')
                elif command_input == "draw triangle here":
                    f = Triangle((x, y))
                    formes.append(f)
                    current_state = FSM.AFFICHER_FORMES
                    print('Triangle drawn')
                elif command_input == "draw losange here":
                    f = Losange(x, y)
                    formes.append(f)
                    current_state = FSM.AFFICHER_FORMES
                    print('Losange drawn')
                mae = current_state
                # Clear the command_input string
                command_input = ""

    if mae == FSM.INITIAL:
        win.fill(WHITE)
        # Drawing text and other initial state components here

    elif mae == FSM.AFFICHER_FORMES:
        # Display the shapes
        win.fill(WHITE)
        for forme in formes:
            forme.update()

    elif mae == FSM.DEPLACER_FORMES_SELECTION:
        # Code for moving the selected shape
        pass

    elif mae == FSM.DEPLACER_FORMES_DESTINATION:
        # Code for destination of the shape
        pass

    pygame.display.update()
"""

"""while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            x, y = pygame.mouse.get_pos()
            if event.key == pygame.K_r:  # Create Rectangle
                f = Rectangle(x, y)
                formes.append(f)
                current_state = FSM.AFFICHER_FORMES
                print('r pressed')
            elif event.key == pygame.K_c:  # Create Circle
                f = Cercle(x, y)
                formes.append(f)
                current_state = FSM.AFFICHER_FORMES
                print('c pressed')
            elif event.key == pygame.K_t:  # Create Triangle
                f = Triangle((x, y))
                formes.append(f)
                print('t pressed')
                current_state = FSM.AFFICHER_FORMES
            elif event.key == pygame.K_l:  # Create Losange
                f = Losange(x, y)
                formes.append(f)
                current_state = FSM.AFFICHER_FORMES
                print('l pressed')
            elif event.key == pygame.K_m:  # Move Shape
                current_state = FSM.DEPLACER_FORMES_SELECTION
                print('m pressed')
            mae = current_state

    if mae == FSM.INITIAL:
        win.fill(WHITE)
        # Drawing text and other initial state components here

    elif mae == FSM.AFFICHER_FORMES:
        # Display the shapes
        win.fill(WHITE)
        for forme in formes:
            forme.update()

    elif mae == FSM.DEPLACER_FORMES_SELECTION:
        # Code for moving the selected shape
        pass

    elif mae == FSM.DEPLACER_FORMES_DESTINATION:
        # Code for destination of the shape
        pass

    pygame.display.update()
"""

last_time_checked = 0
check_interval = 1  # in seconds


def get_command():
    time.sleep(3)
    return "draw rectangle here"


while True:
    current_time = time.time()

    if current_time - last_time_checked > check_interval:
        last_time_checked = time.time()
        command_input = get_command()
        x, y = pygame.mouse.get_pos()

        # Process the complete command_input string
        if command_input == "draw rectangle here":
            f = Rectangle(x, y)
            formes.append(f)
            current_state = FSM.AFFICHER_FORMES
            print('Rectangle drawn')
        elif command_input == "draw circle here":
            f = Cercle(x, y)
            formes.append(f)
            current_state = FSM.AFFICHER_FORMES
            print('Circle drawn')
        elif command_input == "draw triangle here":
            f = Triangle((x, y))
            formes.append(f)
            current_state = FSM.AFFICHER_FORMES
            print('Triangle drawn')
        elif command_input == "draw losange here":
            f = Losange(x, y)
            formes.append(f)
            current_state = FSM.AFFICHER_FORMES
            print('Losange drawn')
        mae = current_state
        # Clear the command_input string
        command_input = ""

    if mae == FSM.INITIAL:
        win.fill(WHITE)
        # Drawing text and other initial state components here

    elif mae == FSM.AFFICHER_FORMES:
        # Display the shapes
        win.fill(WHITE)
        for forme in formes:
            forme.update()

    elif mae == FSM.DEPLACER_FORMES_SELECTION:
        # Code for moving the selected shape
        pass

    elif mae == FSM.DEPLACER_FORMES_DESTINATION:
        # Code for destination of the shape
        pass

    pygame.display.update()
