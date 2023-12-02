import tkinter as tk
from threading import Thread
import time
from typing import Optional
import speech_recognition as sr 
from ivy.ivy import IvyServer

class SpeechRecognizerAgent(IvyServer):
    def __init__(self, agent_name: str):
        IvyServer.__init__(self, 'SpeechRecognizerAgent')
        self.name = agent_name
        self.start('127.255.255.255:2010')  # connexion de l'agent
        self.bind_msg(self.send_color, '^color needed(.*)') 

        self.current_speech = ""
        self.previous_speech = ""
        self.draw_mode = ""  # dessiner ou déplacer
        self.form = ""
        self.color = ""
        self.here = ""

    def send_color (self, agent, *args): 
        print("Souhaitez-vous préciser la couleur de l'objet ? Vous avez 20 secondes ") 

        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Veuillez dire quelque chose :")

            recognizer.adjust_for_ambient_noise(source)
            try:
                audio_data = recognizer.listen(
                    source, timeout=20, phrase_time_limit=5)

                self.current_speech = recognizer.recognize_google(audio_data, language='fr-FR')

                print(f"Vous avez dit : {self.current_speech}")

                print("Reponse :", "color answer" + self.current_speech)

                self.send_msg("colorAnswer"+ self.current_speech)

            except sr.WaitTimeoutError:
                print("Délai d'attente écoulé : Aucun discours détecté. La couleur sera définie aléatoirement.")
                self.send_msg("colorAnsweraleat")

                self.erase_current_speech()

    def erase_current_speech(self):
        self.previous_speech = self.current_speech
        self.current_speech = ""
        self.draw_mode = ""
        self.form = ""
        self.color = ""
        self.here = ""

    def string_preprocessing(self, init_string: str):
        formes_possibles = ["cercle", "triangle", "rectangle", "losange"]
        couleurs = ["vert", "rouge", "jeune", "bleu", "maron", "orange", "violet"]

        # Mode de fonctionnement ( Dessin, déplacement, supression, modification)
        if any(mot in init_string for mot in ["créer", "crée", "dessiner", "dessiné", "dessinez", "dessine"]):
            self.draw_mode = "dessiner"
        elif any(mot in init_string for mot in ["déplacer", "déplace", "déplacé", "déplacement"]):
            self.draw_mode = "deplacer "
        elif any(mot in init_string for mot in ["supprimer", "supprimé", "suppression", "supprime"]):
            self.draw_mode = "supprimer"
        elif any(mot in init_string for mot in ["modofier", "modifié", "modification", "modifie"]):
            self.draw_mode = "modifier"        
        else:
            self.draw_mode = "dessiner"
        print("Mode choisi : ", self.draw_mode)  # debugg

        # Couleur à envoyer
        if any(couleur in init_string for couleur in couleurs):
            self.color = [couleur for couleur in couleurs if couleur in init_string][0] + " "
            print("couleur détectée : ", self.color)  # debugg
        else : 
            self.color = ""
        # Forme choisie
        if any(forme in init_string for forme in formes_possibles):
            self.form = [forme for forme in formes_possibles if forme in init_string][0] + " "
            print("forme détectée : ", self.form)  # debugg
        else:
            self.form = "ceci"

        # Position
        if "ici" in init_string:
            self.here = "ici"
        else :
            self.here = ""

    def speech_recognizer(self):
        recognizer = sr.Recognizer()

        with sr.Microphone() as source:
            print("Veuillez dire quelque chose :")

            recognizer.adjust_for_ambient_noise(source)
            try:
                audio_data = recognizer.listen(
                    source, timeout=20, phrase_time_limit=5)

                self.current_speech = recognizer.recognize_google(audio_data, language='fr-FR')

                print(f"Vous avez dit : {self.current_speech}")

                self.string_preprocessing(self.current_speech)

                self.send_msg("message : " + self.draw_mode + self.form + self.color + self.here)

            except sr.WaitTimeoutError:
                print("Délai d'attente écoulé : Aucun discours détecté.")
            except sr.UnknownValueError:
                print("Désolé, je n'ai pas compris l'audio.")
            except sr.RequestError as e:
                print(f"Impossible de demander des résultats ; {e}")

                self.erase_current_speech()


class SpeechRecognizerApp(tk.Tk):
    def __init__(self, agent: SpeechRecognizerAgent, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Speech Recognizer App")
        self.agent = agent

        self.button = tk.Button(self, text="Lancer la reconnaissance vocale", command=self.start_recognition)
        self.button.pack(pady=20)

    def start_recognition(self):
        self.button.config(state="disabled")
        recognition_thread = Thread(target=self.run_recognition)
        recognition_thread.start()

    def run_recognition(self):
        self.agent.speech_recognizer()
        self.button.config(state="active")


if __name__ == "__main__":
    agent = SpeechRecognizerAgent('SpeechRecognizerAgent')
    app = SpeechRecognizerApp(agent)
    app.mainloop()
