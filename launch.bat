@echo off
rem Trouver le chemin vers l'interpréteur Python
for /f "delims=" %%i in ('where python.exe') do set python=%%i

rem Répertoire du script batch
set script_dir=%~dp0

rem Nom des scripts Python à exécuter
set script1=speech_recognizer.py
set script2=multimodal_motor.py
set script3=palette.py
set script4=n_dollar.py

rem Commande pour exécuter les scripts Python en parallèle
start %python% "%script_dir%\%script1%"
start %python% "%script_dir%\%script2%"
start %python% "%script_dir%\%script3%"
start %python% "%script_dir%\%script4%"

rem Pause pour voir les messages avant que la fenêtre ne se ferme
pause
