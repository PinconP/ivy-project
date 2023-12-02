import pygame
import math
from abc import ABC, abstractmethod
from enum import Enum
import time
from matplotlib import colors
from googletrans import Translator
import random


from ivy.ivy import IvyServer
import math
from typing import List

class FSM(Enum):
    INITIAL = "Etat Initial"
    AFFICHER_FORMES = "Afficher Formes"
    DEPLACER_FORMES_SELECTION = "Deplacer Formes Selection"
    DEPLACER_FORMES_DESTINATION = "Deplacer Formes Destination"
    SUPPRIMER_FORME = "Supprimer Forme"
    MODIFIER_FORME = "Modifier formes"


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
    def __init__(self, win,  x, y, color = (127, 127, 127)):
        super().__init__(x, y)
        self.rayon = 80
        self.win = win 
        self.set_color(color)


    def update(self):
        pygame.draw.circle(self.win, self.color, self.origin, self.rayon)

    def is_clicked(self, pos):
        dx = pos[0] - self.origin[0] ######################################
        dy = pos[1] - self.origin[1] ######################################
        distance = math.sqrt(dx ** 2 + dy ** 2)

        return distance <= self.rayon // 2

    def perimetre(self):
        return 2 * math.pi * self.rayon

    def aire(self):
        return math.pi * self.rayon ** 2

class Rectangle(Forme):
    def __init__(self, win, x, y, color = (127, 127, 127)):
        super().__init__(x, y)
        self.longueur = 60
        self.win = win
        self.set_color(color)

    def update(self):
        pygame.draw.rect(self.win, self.color, (self.origin[0], self.origin[1],
                         self.longueur, self.longueur))

    def is_clicked(self, pos):
        x, y = pos
        x0, y0 = self.origin[0], self.origin[1] ##################################
        if (x > x0) and (x < x0 + self.longueur) and (y > y0) and (y < y0 + self.longueur):
            return True
        else:
            return False

    def perimetre(self):
        return self.longueur * 4

    def aire(self):
        return self.longueur * self.longueur

class Triangle(Forme):
    def __init__(self, win, x, y, color=(127, 127, 127)):
        self.origin = (x, y)
        self.color = color  # Default color: grey

        self.A = (x, y)
        self.B = (x + 40, y + 60)
        self.C = (x - 40, y + 60)

        self.win = win

    def set_location(self, x, y):
        self.origin = (x, y)
        self.A = (x, y)
        self.B = (x + 40, y + 60)
        self.C = (x - 40, y + 60)

    def update(self):
        pygame.draw.polygon(self.win, self.color, [self.A, self.B, self.C])

    def is_clicked(self, pos):
        x, y = pos
        if (x > self.C[0]) and (x < self.B[0]) and (y > self.A[1]) and (y < self.B[1]):
            return True
        else:
            return False

    def perimetre(self):
        def distance(A, B):
            return math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)

        return distance(self.A, self.B) + distance(self.B, self.C) + distance(self.C, self.A)

    def aire(self):
        s = self.perimetre() / 2
        return math.sqrt(s * (s - distance(self.A, self.B)) * (s - distance(self.B, self.C)) * (s - distance(self.C, self.A)))

class Losange(Forme):
    def __init__(self, win, x, y, color = (127, 127, 127)):
        super().__init__(x, y)
        self.A = (x, y)
        self.B = (x + 40, y + 60)
        self.C = (x, y + 120)
        self.D = (x - 40, y + 60)
        self.win = win
        self.set_color(color)

    def set_location(self, x, y):
        super().set_location(x, y)
        self.A = (x, y)
        self.B = (x + 40, y + 60)
        self.C = (x, y + 120)
        self.D = (x - 40, y + 60)

    def update(self):
        pygame.draw.polygon(self.win, self.color, [self.A, self.B, self.C, self.D])

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

class Agent(IvyServer):
    def __init__(self, name: str):
        #Ivy agent
        IvyServer.__init__(self, "AgentPalette")
        self.name = name
        self.start("127.255.255.255:2010")

        # Initialize pygame
        pygame.init()
        # Window settings
        width, height = 600,300 #1600, 1200
        self.win = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Palette multimodale")

        self.mae = FSM.INITIAL  # Finite State Machine
        self.formes : List[Forme] = []  # List of shapes (le type est contraint)
        self.indice_forme = -1  # Index of the active shape

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # Initialize an empty string for command input
        self.command_input = ""

        self.recieved_message = ""

        self.need_message = True

        self.x = None
        self.y = None 

        self.mode = ""
        self.forme = ""
        self.couleur = ""
        self.pos = ""

        self.selected_shape = None
        self.original_position = None

        self.form_deplaced = False
   
    def init_vars(self) : 
        self.recieved_message = ""

        self.x = None
        self.y = None 

        self.mode = ""
        self.forme = ""
        self.couleur = ""
        self.pos = ""

        self.form_deplaced = False


    def run(self) : 
        while True:
            pygame.time.delay(100)  # Attente de 100 millisecondes

            if (self.need_message == True) : 
                self.bind_msg(self.handle_ToDraw_message, '^To draw :(.*)')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    x, y = pygame.mouse.get_pos()
                    if event.key == pygame.K_q:  # Fermer l'application
                        pygame.quit()
                        exit()
                    elif event.key == pygame.K_r:  # Créer un rectangle
                        f = Rectangle(self.win, x, y)
                        self.formes.append(f)
                        self.mae = FSM.AFFICHER_FORMES
                        print('r pressé')
                    elif event.key == pygame.K_c:  # Créer un cercle
                        f = Cercle(self.win, x, y)
                        self.formes.append(f)
                        self.mae = FSM.AFFICHER_FORMES
                        print('c pressé')
                    elif event.key == pygame.K_t:  # Créer un triangle
                        f = Triangle(self.win, x, y)
                        self.formes.append(f)
                        print('t pressé')
                        self.mae = FSM.AFFICHER_FORMES
                    elif event.key == pygame.K_l:  # Créer un losange
                        f = Losange(self.win, x, y)
                        self.formes.append(f)
                        self.mae = FSM.AFFICHER_FORMES
                        print('l pressé')
                    elif event.key == pygame.K_m:  # Déplacer la forme sélectionnée
                        self.mae = FSM.DEPLACER_FORMES_SELECTION
                        print('m pressé')
                    elif event.key == pygame.K_s:  # Supprimer la forme sélectionnée
                        self.mae = FSM.SUPPRIMER_FORME
                        print('s pressé')
                    elif event.key == pygame.K_a:  # Modifier la forme sélectionnée
                        self.mae = FSM.MODIFIER_FORME
                        print('s pressé')

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 :  # Clic gauche
                        if self.mode == "deplacer" and  self.mae == FSM.DEPLACER_FORMES_SELECTION:
                            for forme in reversed(self.formes):
                                if forme.is_clicked(event.pos):
                                    self.selected_shape = forme
                                    self.original_position = event.pos
                                    self.mae = FSM.DEPLACER_FORMES_DESTINATION
                                
                        elif self.mode == "deplacer" and  self.mae == FSM.DEPLACER_FORMES_DESTINATION: 
                            if event.type == pygame.MOUSEMOTION and self.selected_shape is not None:
                                # Mise à jour temporaire de l'emplacement de la forme en fonction du mouvement de la souris
                                self.selected_shape.set_location(event.pos[0], event.pos[1])

                            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                # Au deuxième clic, déplacez la forme à la position du clic
                                self.selected_shape.set_location(event.pos[0], event.pos[1])
                                self.mae = FSM.AFFICHER_FORMES
                                self.selected_shape = None
                                self.original_position = None
                                self.send_msg('drawn') 
                                self.init_vars()
                    
                        #### Supprimer forme
                        elif self.mae == FSM.SUPPRIMER_FORME : 
                            for forme in reversed(self.formes):
                                if forme.is_clicked(event.pos):
                                    self.selected_shape = forme
                                    self.formes.remove(forme)
                                    self.mae = FSM.AFFICHER_FORMES
                                    self.send_msg('drawn') 
                                    self.init_vars()
                    
                        ###Changer couleur 
                        elif self.mae == FSM.SUPPRIMER_FORME :
                            for forme in reversed(self.formes):
                                if forme.is_clicked(event.pos):
                                    forme.set_color(self.couleur)
                                    self.mae = FSM.AFFICHER_FORMES
                                    self.send_msg('drawn') 
                                    self.init_vars()

                        else : 
                            self.x, self.y = event.pos
                            print("Clic à la position :", (self.x, self.y))
                            pos =  f"({self.x}, {self.y})"
                            pos = pos.replace("(", "").replace(")", "")
                            self.send_msg("Position :" + pos)

            ## Foncitonnement par messages Ivy  : 
            if self.mode == "dessiner" : 
                self.form_drawing(self.forme, self.couleur, self.pos)
            
            if self.mode == "deplacer": 
                print("ON PASSE BIEN DANS DEPLACER")
                #self.form_deplace()
                self.mae = FSM.DEPLACER_FORMES_SELECTION
                self.mode = ""

            if self.mode == "supprimer" : 
                print("Mode supression")
                self.mae = FSM.SUPPRIMER_FORME
                self.mode = ""

            if self.mode == "modifier" : 
                print("Mode modification")
                self.mae = FSM.MODIFIER_FORME
                self.mode = ""

            if self.mae == FSM.INITIAL:
                self.win.fill(self.WHITE)
                # Drawing text and other initial state components here

            elif self.mae == FSM.AFFICHER_FORMES:
                # Display the shapes
                self.win.fill(self.WHITE)
                for forme in self.formes:
                    forme.update()

            elif self.mae == FSM.DEPLACER_FORMES_SELECTION:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        for forme in reversed(self.formes):
                            if forme.is_clicked(event.pos):
                                self.selected_shape = forme
                                self.original_position = event.pos
                                self.mae = FSM.DEPLACER_FORMES_DESTINATION

            elif self.mae == FSM.DEPLACER_FORMES_DESTINATION:
                if event.type == pygame.MOUSEMOTION and self.selected_shape is not None:
                    # Mise à jour temporaire de l'emplacement de la forme en fonction du mouvement de la souris
                    self.selected_shape.set_location(event.pos[0], event.pos[1])

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Au deuxième clic, déplacez la forme à la position du clic
                    self.selected_shape.set_location(event.pos[0], event.pos[1])
                    self.mae = FSM.AFFICHER_FORMES
                    self.selected_shape = None
                    self.original_position = None
                    self.form_deplaced = True
                    self.mae = FSM.AFFICHER_FORMES
                    self.send_msg('drawn') 
                    self.init_vars()
 

            elif self.mae == FSM.SUPPRIMER_FORME : 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        for forme in reversed(self.formes):
                            if forme.is_clicked(event.pos):
                                self.selected_shape = forme
                                self.formes.remove(forme)
                                self.mae = FSM.AFFICHER_FORMES
                                self.send_msg('drawn') 
                                self.init_vars()


            elif self.mae == FSM.MODIFIER_FORME : 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        for forme in reversed(self.formes):
                            if forme.is_clicked(event.pos):
                                forme.set_color(self.couleur)
                                self.mae = FSM.AFFICHER_FORMES
                                self.send_msg('drawn') 
                                self.init_vars()
                                

            print("State : ", self.mae)
            print("Listre de formes :", self.formes)
            pygame.display.update()

    def handle_ToDraw_message(self, agent, *args) :
        couleur = "" 
        print("Message reçu :", args)
        self.recieved_message = args
        self.recieved_message = ''.join(args)
        print(type(self.recieved_message))
        print("Message traite :", args)
        if "deplacer" in self.recieved_message : 
            self.mode = "deplacer"
        elif "supprimer" in self.recieved_message : 
            self.mode = "supprimer"
        elif "modifier" in self.recieved_message : 
            self.mode = "modifier"
            couleur = self.recieved_message.replace("modifier", "")
            print("couleur en lettres : ", couleur)
            couleur = self.recieved_message.replace(" ", "")
            print("couleur sans espaces")
            translator = Translator()
            translated = translator.translate(couleur, src= 'fr', dest='en')
            couleur =colors.to_rgb(translated.text )
            self.color = tuple(int(x * 255) for x in self.color) 
            print("Couleur de modification :", self.color)

        else : 
            self.mode, self.forme, self.couleur, self.pos = self.recieved_message.split()

    def form_drawing (self, form, color, pos):
        #Couleur 
        translator = Translator()
        translated = translator.translate(color, src= 'fr', dest='en')
        color_rgb =colors.to_rgb(translated.text )
        color_rgb = tuple(int(x * 255) for x in color_rgb) 

        #Position
        if "aleat" in self.pos :
            # Définir les plages pour x et y
            min_x, max_x = 0, 600  # Exemple : plage de 0 à 800 pour x
            min_y, max_y = 0, 300  # Exemple : plage de 0 à 600 pour y

            # Générer des coordonnées aléatoires
            x_aleatoire = random.randint(min_x, max_x)
            y_aleatoire = random.randint(min_y, max_y)

            self.pos = (x_aleatoire , y_aleatoire) 
            (self.x, self.y) = (x_aleatoire , y_aleatoire) 
            print("Pos aleat :", self.pos)
        else : 
            parties = pos.split(',')
            (self.x, self.y)  = tuple(map(int, parties))

        #Forme
        if form == "rectangle" : 
            f = Rectangle(self.win, self.x, self.y, color_rgb)
            self.formes.append(f)
            self.mae = FSM.AFFICHER_FORMES
            print('Rectangle dessiné')
        elif form == "cercle": 
            f = Cercle(self.win, self.x, self.y, color_rgb)
            self.formes.append(f)
            self.mae = FSM.AFFICHER_FORMES
            print('Cercle dessiné')
        elif form == "losange" : 
            f = Losange(self.win, self.x, self.y, color_rgb)
            self.formes.append(f)
            self.mae = FSM.AFFICHER_FORMES
            print('Losange dessiné')

        elif form == "triangle" : 
            f = Triangle(self.win, self.x, self.y, color_rgb)
            self.formes.append(f)
            print('Triangle dessiné')
            self.mae = FSM.AFFICHER_FORMES

        self.send_msg('drawn') 
        self.init_vars()
    
    def form_deplace (self): 
        print("ON RENTRE DANS DEPLACEMENT") 
        self.mae = FSM.DEPLACER_FORMES_SELECTION
        if self.form_deplaced : 
            print('Forme Deplacee')
            self.send_msg('drawn') 
            self.init_vars()


# Helper function for distance calculation

def distance(A, B):
    return math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2)

if __name__ == "__main__":
    agent = Agent("Palette")
    agent.run()
    
    