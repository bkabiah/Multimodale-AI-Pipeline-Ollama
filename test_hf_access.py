import os
from dotenv import load_dotenv
from huggingface_hub import whoami, model_info

load_dotenv()
token = os.getenv("HF_TOKEN")

if not token or token == "dein_huggingface_token_hier":
    print("❌ FEHLER: Bitte trage deinen echten HF_TOKEN in die .env Datei ein!")
else:
    try:
        # 1. Prüfen, ob der Token gültig ist
        user = whoami(token)
        print(f"✅ Eingeloggt als: {user['name']}")
        
        # 2. Prüfen, ob wir das spezifische Llama Modell sehen dürfen
        print("🔄 Prüfe Zugriff auf Llama-3.2-11B-Vision-Instruct...")
        info = model_info("meta-llama/Llama-3.2-11B-Vision-Instruct", token=token)
        print(f"✅ ERFOLG! Du hast Zugriff auf das Modell (ID: {info.id}).")
        print("🚀 Du kannst mit Phase 2 fortfahren!")
        
    except Exception as e:
        print(f"❌ ZUGRIFF VERWEIGERT oder FEHLER: {e}")
        print("💡 Tipp: Gehe zur Modell-Seite, lade die Seite neu (F5) und suche nach einem 'Agree' Button. Falls keiner da ist, erstelle einen NEUEN Token in deinen HF Settings.")
