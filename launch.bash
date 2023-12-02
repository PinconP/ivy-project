#!/bin/bash

# Trouver le chemin vers l'interpréteur Python
python=$(command -v python3)

# Répertoire du script bash
script_dir=$(dirname "$(readlink -f "$0")")

# Noms des scripts Python à exécuter
script1=speech_recognizer.py
script2=multimodal_motor.py
script3=palette.py
script4=n_dollar.py

# Commande pour exécuter les scripts Python en parallèle
$python "$script_dir/$script1" &
$python "$script_dir/$script2" &
$python "$script_dir/$script3" &
$python "$script_dir/$script4" &

# Pause pour voir les messages avant que la fenêtre ne se ferme
read -p "Appuyez sur Entrée pour quitter"