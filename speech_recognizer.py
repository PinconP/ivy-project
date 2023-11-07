import speech_recognition as sr


def main():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Veuillez dire quelque chose :")

        recognizer.adjust_for_ambient_noise(source)

        try:
            # Record audio for a max of 5 seconds after speech has been detected
            # If no speech is detected for 5 seconds, then it will timeout
            audio_data = recognizer.listen(
                source, timeout=5, phrase_time_limit=5)

            text = recognizer.recognize_google(audio_data, language='fr-FR')
            print(f"Vous avez dit : {text}")

        except sr.WaitTimeoutError:
            print("Délai d'attente écoulé : Aucun discours détecté.")

        except sr.UnknownValueError:
            print("Désolé, je n'ai pas compris l'audio.")

        except sr.RequestError as e:
            print(f"Impossible de demander des résultats ; {e}")


if __name__ == "__main__":
    main()
