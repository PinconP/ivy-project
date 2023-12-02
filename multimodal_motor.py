# Le moteur de fusion multi modale est un outil permettant de récupére 
#les instructions passées sur le bus Ivy par les autrs agants pour créer une trame 
#compréhensible par la palette pour afficher les formes. Il ddoit également être capable 
# de récupérer les clics souris sur la palette pour déplacer les formes par exemple 
#(forme sélectionnée + lieu de déplacement)


from ivy.ivy import IvyServer
import time
import random


class Etats : 
    INITIAL = "Init"
    STRING_PROCESS = "string_processing"
    DETECT_FORME = "detect_forme"
    DEPLACEMENT = "deplacement"
    SUPPRIMER = "Suppression de forme"
    MODIFIER = "Modification de forme"
    RECHERCHE_FORME = "recherche_forme"
    COLOR = "recheche_couleur"
    RAND_COLOR = "random_color"
    POS = "position"
    RAND_POS = "random_position"
    DRAW = "draw_form"
    
class multimodalMotorAgent(IvyServer):
    def __init__(self, name: str):
        #Ivy Agent
        IvyServer.__init__(self, "AgentMoteurDeFusion")
        self.name = name
        self.start("127.255.255.255:2010")

        self.init_vars()

    def init_vars (self) : 

        self.current_state = Etats.INITIAL
        self.prevous_state = Etats.INITIAL
        self.next_state = Etats.STRING_PROCESS

        self.current_speech = None  
        self.previous_speech = None

        #Variables à récupérer et envoyer à la palette 
        self.draw_mode = "" #dessiner ou déplacer
        self.form = None
        self.color = None
        self.pos = ""
        self.deplacer = False
        self.supprimer = False
        self.modifier = False
        self.phrase_to_send = ""

        self.drawn = False

        self.waiting_answer = False

        self.message_received = False ###########################################################################################
        
        self.go_rand_color = False ######## Dit si l'on doit donner une couleur au hasard

    def transitions(self):
        #INITIAL OK 
        if (self.current_state == Etats.INITIAL) and True:
            self.current_state = Etats.STRING_PROCESS
            self.previous_state = Etats.INITIAL
            print(self.current_state)
        
        #STRING PROCESS 
        #dessiner ok
        if (self.current_state == Etats.STRING_PROCESS) and ( "dessiner" in self.draw_mode) : 
            print(" YES on est rentré dans dessiner > GO DETECT FORME")
            self.current_state = Etats.DETECT_FORME
            self.previous_state = Etats.STRING_PROCESS
        elif (self.current_state == Etats.STRING_PROCESS) and ("deplacer" in self.draw_mode)  : 
            print("DEPLACEMENT DETECTE > GO DRAW")
            self.current_state = Etats.DRAW
            self.previous_state = Etats.STRING_PROCESS
            print(self.current_state)
        elif (self.current_state == Etats.STRING_PROCESS) and ("supprimer" in self.draw_mode)  : 
            print("DEPLACEMENT DETECTE > GO SUPPRIMER")
            self.current_state = Etats.DRAW
            self.previous_state = Etats.STRING_PROCESS
            print(self.current_state)
        elif (self.current_state == Etats.STRING_PROCESS) and ("modifier" in self.draw_mode)  : 
            print("DEPLACEMENT DETECTE > GO MODIFIER")
            self.current_state = Etats.MODIFIER
            self.previous_state = Etats.STRING_PROCESS
            print(self.current_state)
        
        #DEPLACEMENT
        if (self.current_state == Etats.DEPLACEMENT) and True: 
            print("ON RENTRE DANS DEPLACEMENT")
            self.current_state = Etats.DETECT_FORME
            self.previous_state = Etats.DEPLACEMENT
            print(self.current_state)
        
        #SUPPRIMER
        if (self.current_state == Etats.SUPPRIMER) and True: 
            print("ON RENTRE DANS SUPPRIMER")
            self.current_state = Etats.DETECT_FORME
            self.previous_state = Etats.SUPPRIMER
            print(self.current_state)

        #MODIFIER 
        if (self.current_state == Etats.MODIFIER) and True: 
            print("ON RENTRE DANS DEPLACEMENT")
            self.current_state = Etats.COLOR
            self.previous_state = Etats.MODIFIER
            print(self.current_state)

        #DETECT_FORME (savoir si la forme est connue dès le premier speech reçu ou si l'on est dans un cas de multimodalité)
        if (self.current_state == Etats.DETECT_FORME) and ("ceci" in self.form) : 
            print("ON RENTRE DANS DETECT FORME > GO RECHERCHE FORME ")
            self.current_state = Etats.RECHERCHE_FORME
            self.previous_state = Etats.DETECT_FORME
        #OK 
        elif (self.current_state == Etats.DETECT_FORME) and self.form != None : 
            print(" ON CONNAIT LA FORME -> GO COLOR")
            self.current_state = Etats.COLOR
            self.previous_state = Etats.DETECT_FORME
            print(self.current_state)

        #RECHERCHE_FORME
        if (self.current_state == Etats.RECHERCHE_FORME) and not("ceci" in self.form) : 
            print("ON RENTRE DANS RECHERCHE FORME -> GO COLOR ")
            self.current_state = Etats.COLOR
            self.previous_state = Etats.RECHERCHE_FORME
            print(self.current_state)
        
        #COLOR 
        if (self.current_state == Etats.COLOR) and self.color == None and self.go_rand_color : 
            print("ON A PAS LA COULEUR -> GO RAND COLOR")
            self.current_state = Etats.RAND_COLOR
            self.previous_state = Etats.COLOR

        elif (self.current_state == Etats.COLOR) and self.color != None and self.color != "": 
            print("ON A LA COULEUR -> GO POS")
            self.current_state = Etats.POS
            self.previous_state = Etats.COLOR
            print(self.current_state)

        #RAND_COLOR
        if (self.current_state == Etats.RAND_COLOR) and self.color != None : 
            self.current_state = Etats.POS
            self.previous_state = Etats.RAND_COLOR
            print(self.current_state)
         
        #POS
        if (self.current_state == Etats.POS) and ("ici" in self.pos or self.pos != None) : 
            self.current_state = Etats.DRAW                                   # gestion de l'attente du clic oour récupérer la position
            self.previous_state = Etats.POS
        elif (self.current_state == Etats.POS) and "aleat" in self.pos : 
            self.current_state = Etats.RAND_POS
            self.previous_state = Etats.POS
            print(self.current_state)

        #RANDOM_POS
        if (self.current_state == Etats.RAND_POS) and not("aleat" in self.pos): 
            self.current_state = Etats.DRAW
            self.previous_state = Etats.RAND_POS
            print(self.current_state)
        
        #DRAW
        if (self.current_state == Etats.DRAW) and self.drawn == True: 
            self.current_state = Etats.INITIAL
            self.previous_state = Etats.DRAW
            print(self.current_state)
                   
    #A programmer, les actions sur etat
    def actions(self): 
        #INITIAL
        if self.current_state == Etats.INITIAL : 
            self.init_vars()
        
        #STRING_PROCESS
        if self.current_state == Etats.STRING_PROCESS : 
            #Attente d'un message
            self.bind_msg(self.string_preprocessing, '^message : (.*)') 
        
        #DEPLACEMENT 
        if self.current_state == Etats.DEPLACEMENT : 
            self.deplacer = True

        #SUPPRIMER
        if self.current_state == Etats.DEPLACEMENT : 
            self.supprimer = True
        
        #MODIFIER 
        if self.current_state == Etats.DEPLACEMENT : 
            self.modifier = True


        #DETECT_FORME
        #Pas d'actions sur detect_forme

        #RECHERCHE_FORME (Testter s'il est nécessier d'envoyer ce message )
        if self.current_state == Etats.RECHERCHE_FORME :

            if self.waiting_answer == False: 
                self.send_msg('need forme')
                self.waiting_answer = True
    
            self.bind_msg(self.str_wait_form, '^forme(.*)')
        
        #COLOR 
        if self.current_state == Etats.COLOR :
            if self.waiting_answer == False : 
                self.send_msg("color needed") 
                self.waiting_answer = True
            else : 
                self.bind_msg(self.str_wait_color, "^colorAnswer(.*)")

        #RAND_COLOR 
        if self.current_state == Etats.RAND_COLOR : 
            # Liste de couleurs
            couleurs_disponibles = ["rouge", "vert", "bleu", "jaune", "orange", "violet", "maron"]
            # Choisir une couleur aléatoire
            self.color = random.choice(couleurs_disponibles) + " "
        
        #POS 
        #PAS d'action 

        #RAND_POS 
        if self.current_state == Etats.RAND_POS and self.pos == "aleat": 
            # Définir les plages pour x et y
            min_x, max_x = 0, 600  # Exemple : plage de 0 à 800 pour x
            min_y, max_y = 0, 300  # Exemple : plage de 0 à 600 pour y

            # Générer des coordonnées aléatoires
            x_aleatoire = random.randint(min_x, max_x)
            y_aleatoire = random.randint(min_y, max_y)

            self.pos = f"{x_aleatoire},{y_aleatoire}"
            
        #DRAW
        if self.current_state == Etats.DRAW : 
            self.bind_msg(self.form_drawn, '^drawn(.*)')

            if  ("deplacer" in self.draw_mode or "supprimer" in self.draw_mode)  and self.waiting_answer == False : 
                self.send_msg("To draw :"+self.draw_mode)
                print("Message pour déplacer ou supprimer: " + self.draw_mode)
                self.waiting_answer = True

            elif ("modifier" in self.draw_mode) and self.waiting_answer == False :
                self.send_msg("To draw :"+self.draw_mode + self.color)
                print("Message pour déplacer ou supprimer: " + self.draw_mode + self.color)
                self.waiting_answer = True
            
            else : 

                if("ici" in self.pos):
                    self.bind_msg(self.str_wait_pos, '^Position :(.*)')

                if not('ici' in self.pos) and (self.pos != "" ) and self.waiting_answer == False : 
                    self.send_msg("To draw :" + self.draw_mode + self.form + self.color + self.pos)
                    self.waiting_answer = True




    def form_drawn (self, agent, *args) : 
        self.waiting_answer = False
        self.drawn = True
    
    def str_wait_form (self, agent, *args) : 
        forme = ''.join(args)
        forme = forme.replace(" ", "")
        self.waiting_answer = False
        print("Args : ", forme)
        self.form = forme +" "

    def str_wait_pos (self, agent, *args) : 
        print("Position reçue: ", args)
        self.pos = ",".join(str(arg) for arg in args) # contient la position sous forme d'une stringù
        self.pos = self.pos.replace(" ", "")
        print("Position traitee: " + self.pos)

    def str_wait_color(self, agent, *args): 
        print("Couleur reçue: ", args)
        self.color = ''.join(args)
        
        if 'non' in self.color :
            
            # Liste de couleurs
            couleurs_disponibles = ["rouge", "vert", "bleu", "jaune", "orange", "violet", "maron"]
            # Choisir une couleur aléatoire
            self.color = random.choice(couleurs_disponibles) + " "
        
        self.waiting_answer = False

    def string_preprocessing(self, agent, *args):

        formes_possibles = ["cercle", "triangle", "rectangle", "losange"]
        couleurs = ["vert", "rouge", "jaune", "bleu", "marron", "orange", "violet"]

        # plusieurs cas on va couper la string aux espaces
        init_string = ' '.join(args)

        if self.draw_mode == "" : 
            if any(mot in init_string for mot in ["créer", "crée", "dessiner", "dessiné", "dessinez", "dessine"]):
                self.draw_mode = "dessiner "
                print("Draw mode : ", self.draw_mode)  # debug

            elif any(mot in init_string for mot in ["deplacer", "deplace"]):
                self.draw_mode = "deplacer "
                print("Draw mode : ", self.draw_mode)  # debug

            elif "supprimer" in init_string :
                self.draw_mode = "supprimer"
                print("Draw mode : ", self.draw_mode)  # debug
            
            elif "modifier" in init_string :
                self.draw_mode = "modifier"
                print("Draw mode : ", self.draw_mode)  # debug

            else:
                self.draw_mode = "dessiner "  # Par défaut, on dessine
                print("Draw mode : ", self.draw_mode)  # debug

        if any(couleur in init_string for couleur in couleurs):
            self.color = [couleur for couleur in couleurs if couleur in init_string][0] + " "
            print("couleur détectée : ", self.color)  # debug
        else : 
            self.color = ""

        if any(forme in init_string for forme in formes_possibles):
            self.form = [forme for forme in formes_possibles if forme in init_string][0] + " "
            print("forme détectée : ", self.form)  # debug
        else:
            if self.form == None : 
                self.form = "ceci "  # Dans ce cas, c'est le n_dollar qui enverra le message au clic sur recognize par exemple

        if "ici" in init_string:
            self.pos = "ici "
            print("ICI : ", self.pos)  # debug
        else : 
            self.pos = " aleat"

        print(f"[Agent {self.name}] Args: {args[0]}") ################################################################################

        # Mettez à jour self.message_received lorsque le message attendu est reçu
        if args[0] != None:                           ########################################################################"######"
            self.message_received = True              ################################################################################

    def multimodalFusionMotor(self):
        while True:
            self.transitions()
            self.actions()
            time.sleep(1)  # Pause de 1 seconde entre chaque vérification
            if self.current_state == Etats.DETECT_FORME : 
                print("One loop", self.current_state)

            #TESTS 
            print("\n####################\n")
            print("Etat :", self.current_state)
            print("Position :", self.pos)
            print("Attente de réponse :", self.waiting_answer)
            print("Draw mode :", self.draw_mode) #dessiner ou déplacer
            print("Forme :", self.form)
            print("Color :", self.color)
 
            
        # Réinitialisez self.message_received pour la prochaine itération
        self.message_received = False

if __name__ == "__main__":
    print("Agent moteur de fusion :")
    m = multimodalMotorAgent('Moteur de Fusion')
    m.multimodalFusionMotor()