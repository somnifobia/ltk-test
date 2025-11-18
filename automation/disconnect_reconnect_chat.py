from core import Rengar 

rengar = Rengar()

class Chat:
    def __init__(self):
        self.chat_state = self.return_disconnect()
        print(f"🔄 Chat inicializado")

    def return_disconnect(self):
        try:
            req = rengar.riot_request("GET", "/chat/v1/session", "")
            req_data = req.json()
            is_disconnected = req_data["state"] == "disconnected"
            return is_disconnected
        except Exception as e:
            print(f"⚠️ Erro ao verificar estado do chat: {e}")
            return False

    def disconnect(self):
        try:
            body = {"config": "disable"}
            response = rengar.riot_request("POST", "/chat/v1/suspend", body)
            print("❌ Chat desconectado - Você está OFFLINE")
            return response
        except Exception as e:
            print(f"⚠️ Erro ao desconectar chat: {e}")
            return None

    def reconnect(self):
        try:
            response = rengar.riot_request("POST", "/chat/v1/resume", "")
            print("✅ Chat reconectado - Você está ONLINE")
            return response
        except Exception as e:
            print(f"⚠️ Erro ao reconectar chat: {e}")
            return None

    def toggle_chat(self):

        current_state = self.return_disconnect()
        
        if current_state:
            print("🔄 Chat está OFFLINE, reconectando...")
            self.reconnect()
            self.chat_state = False 
        else:
            print("🔄 Chat está ONLINE, desconectando...")
            self.disconnect()
            self.chat_state = True  

    def return_state(self):
        current_state = self.return_disconnect()
        self.chat_state = current_state
        
        if current_state:
            return "OFFLINE"  
        else:
            return "ONLINE"   