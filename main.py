import asyncio
from gemini_robot import LiveGeminiRobot

async def main():
    print("--- Mode Robot Gemini Temps Réel ---")
    try:
        # Initialisation du robot Live
        # Utilise le modèle 2.0 Flash exp ou supérieur pour le mode live
        robot = LiveGeminiRobot(model_id='gemini-3.1-flash-live-preview')
        
        # Lancement de la session connectée
        await robot.run()
    except KeyboardInterrupt:
        print("\n[Robot] Arrêt manuel par l'utilisateur.")
    except Exception as e:
        print(f"\n[ERREUR] : {e}")

if __name__ == "__main__":
    asyncio.run(main())
