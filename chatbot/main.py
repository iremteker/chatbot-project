import os
import sys

# Proje kök dizinini sys.path'e ekle
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from agents.orchestrator import OrchestratorAgent

def main():
    print("Chatbot başlatıldı...")
    agent = OrchestratorAgent()

    while True:
        user_input = input("Sen: ")

        if user_input.lower() in ["çıkış", "exit", "quit"]:
            print("Chatbot kapatılıyor...")
            break

        response = agent.run(user_input)
        print("Chatbot:", response)


if __name__ == "__main__":
    main()