import threading
import time
import random
from core import Rengar


class InstalockAutoban:
    def __init__(self):
        self.champ_dict = {}
        self.instalock_enabled = False
        self.instalock_champion = "None"
        self.instalock_backup_2 = "None"  # 2º pick backup
        self.instalock_backup_3 = "None"  # 3º pick backup
        self.auto_ban_enabled = False
        self.auto_ban_champion = "None"
        self.rengar = Rengar()
        self.monitor_thread = None
        self.is_running = True
        
        # Tenta carregar campeões na inicialização
        print("🔄 Loading champion data...")
        success = self.update_champion_list()
        if not success:
            print("⚠️  Champion list will be loaded when League Client is available")

    def update_champion_list(self):
        """
        Atualiza a lista de campeões obtendo seus IDs e nomes da API LCU.
        """
        try:
            # Tenta o endpoint principal
            response = self.rengar.lcu_request("GET", "/lol-champ-select/v1/all-grid-champions", "")
            
            if response.status_code == 200:
                champion_data = response.json()
                for champ in champion_data:
                    champ_id = champ.get("id")
                    champ_name = champ.get("name")
                    if champ_id and champ_name:
                        self.champ_dict[champ_name.lower()] = champ_id
                print(f"✓ Champion list loaded: {len(self.champ_dict)} champions available")
                return True
            else:
                # Tenta endpoint alternativo
                response = self.rengar.lcu_request("GET", "/lol-champions/v1/inventories/local-player/champions", "")
                if response.status_code == 200:
                    champion_data = response.json()
                    for champ in champion_data:
                        champ_id = champ.get("id")
                        champ_name = champ.get("name")
                        if champ_id and champ_name and champ_id != -1:
                            self.champ_dict[champ_name.lower()] = champ_id
                    print(f"✓ Champion list loaded: {len(self.champ_dict)} champions available")
                    return True
                else:
                    return False
        except Exception as e:
            return False

    def champ_name_to_id(self, champ_name):
        """
        Converte o nome de um campeão para o ID correspondente.
        """
        if not self.champ_dict:
            self.update_champion_list()
        
        champ_name = champ_name.lower().strip()
        champ_id = self.champ_dict.get(champ_name, -1)
        
        # Se não encontrou, tenta buscar por correspondência parcial
        if champ_id == -1:
            for name, id in self.champ_dict.items():
                if champ_name in name or name in champ_name:
                    return id
        
        return champ_id
    
    def get_champion_suggestions(self, partial_name):
        """Retorna sugestões de campeões baseado em nome parcial"""
        if not self.champ_dict:
            return []
        partial = partial_name.lower().strip()
        suggestions = [name.title() for name in self.champ_dict.keys() if partial in name]
        return suggestions[:5]
    
    def is_champion_banned(self, champion_id):
        """Verifica se um campeão está banido na sessão atual"""
        try:
            response = self.rengar.lcu_request("GET", "/lol-champ-select/v1/session", "")
            if response.status_code == 200:
                session_data = response.json()
                
                # Verifica em todas as ações de ban
                for actions in session_data.get("actions", []):
                    if isinstance(actions, list):
                        for action in actions:
                            if action.get("type") == "ban" and action.get("completed"):
                                if action.get("championId") == champion_id:
                                    return True
                
                # Verifica bans no objeto bans (se existir)
                bans = session_data.get("bans", {})
                if isinstance(bans, dict):
                    for team_bans in bans.values():
                        if isinstance(team_bans, list):
                            for ban in team_bans:
                                if ban == champion_id:
                                    return True
            
            return False
        except:
            return False

    def get_available_champion(self):
            """
            Retorna o primeiro campeão disponível (não banido) da lista:
            1º pick -> 2º pick backup -> 3º pick backup -> Nenhum (escolha manual)
            """
            # Se é random, retorna um campeão aleatório
            if self.instalock_champion == "Random":
                if self.champ_dict:
                    return random.choice(list(self.champ_dict.values()))
                return -1
            
            # Tenta o 1º pick
            champion_id = self.champ_name_to_id(self.instalock_champion)
            if champion_id != -1 and not self.is_champion_banned(champion_id):
                print(f"✓ Picking 1st choice: {self.instalock_champion}")
                return champion_id
            elif champion_id != -1:
                print(f"⚠️  1st choice {self.instalock_champion} is BANNED")
            
            # Tenta o 2º pick backup
            if self.instalock_backup_2 != "None":
                backup2_id = self.champ_name_to_id(self.instalock_backup_2)
                if backup2_id != -1 and not self.is_champion_banned(backup2_id):
                    print(f"✓ Picking 2nd choice (backup): {self.instalock_backup_2}")
                    return backup2_id
                elif backup2_id != -1:
                    print(f"⚠️  2nd choice {self.instalock_backup_2} is BANNED")
            
            # Tenta o 3º pick backup
            if self.instalock_backup_3 != "None":
                backup3_id = self.champ_name_to_id(self.instalock_backup_3)
                if backup3_id != -1 and not self.is_champion_banned(backup3_id):
                    print(f"✓ Picking 3rd choice (backup): {self.instalock_backup_3}")
                    return backup3_id
                elif backup3_id != -1:
                    print(f"⚠️  3rd choice {self.instalock_backup_3} is BANNED")
            
            # Se todos estão banidos, retorna -1 (não escolhe nada - escolha manual)
            print("🚫 All your champions are banned! Please pick manually.")
            return -1

    def set_instalock_champion(self, champion_name):
        """Define o campeão para instalock"""
        champion_name = champion_name.strip()
        
        if champion_name == "99" or champion_name.lower() == "disable":
            self.instalock_enabled = False
            self.instalock_champion = "None"
            return True
        else:
            if champion_name.lower() == "random":
                if not self.champ_dict:
                    print("⚠️  Champion list not loaded yet. Please wait...")
                    self.update_champion_list()
                    if not self.champ_dict:
                        return False
                self.instalock_champion = "Random"
                self.instalock_enabled = True
                return True
            else:
                champ_id = self.champ_name_to_id(champion_name)
                if champ_id == -1:
                    suggestions = self.get_champion_suggestions(champion_name)
                    if suggestions:
                        print(f"💡 Did you mean: {', '.join(suggestions)}?")
                    if self.champ_dict:
                        print(f"📊 Total champions loaded: {len(self.champ_dict)}")
                    else:
                        print(f"⚠️  Champion list not loaded. Make sure League Client is running!")
                    return False
                else:
                    # Encontra o nome correto do campeão (com capitalização)
                    correct_name = next((name for name in self.champ_dict.keys() if name == champion_name.lower()), champion_name.lower())
                    self.instalock_champion = correct_name
                    self.instalock_enabled = True
                    return True
    
    def set_instalock_backup_2(self, champion_name):
        """Define o 2º campeão backup para instalock"""
        champion_name = champion_name.strip()
        
        if champion_name == "99" or champion_name.lower() == "disable" or champion_name.lower() == "none":
            self.instalock_backup_2 = "None"
            print("✓ 2nd backup cleared")
            return True
        else:
            champ_id = self.champ_name_to_id(champion_name)
            if champ_id == -1:
                suggestions = self.get_champion_suggestions(champion_name)
                if suggestions:
                    print(f"💡 Did you mean: {', '.join(suggestions)}?")
                return False
            else:
                correct_name = next((name for name in self.champ_dict.keys() if name == champion_name.lower()), champion_name.lower())
                self.instalock_backup_2 = correct_name
                print(f"✓ 2nd backup set: {correct_name}")
                return True
    
    def set_instalock_backup_3(self, champion_name):
        """Define o 3º campeão backup para instalock"""
        champion_name = champion_name.strip()
        
        if champion_name == "99" or champion_name.lower() == "disable" or champion_name.lower() == "none":
            self.instalock_backup_3 = "None"
            print("✓ 3rd backup cleared")
            return True
        else:
            champ_id = self.champ_name_to_id(champion_name)
            if champ_id == -1:
                suggestions = self.get_champion_suggestions(champion_name)
                if suggestions:
                    print(f"💡 Did you mean: {', '.join(suggestions)}?")
                return False
            else:
                correct_name = next((name for name in self.champ_dict.keys() if name == champion_name.lower()), champion_name.lower())
                self.instalock_backup_3 = correct_name
                print(f"✓ 3rd backup set: {correct_name}")
                return True

    def set_auto_ban_champion(self, champion_name):
        """Define o campeão para auto ban"""
        champion_name = champion_name.strip()
        
        if champion_name == "99" or champion_name.lower() == "disable":
            self.auto_ban_enabled = False
            self.auto_ban_champion = "None"
            return True
        else:
            champ_id = self.champ_name_to_id(champion_name)
            if champ_id == -1:
                suggestions = self.get_champion_suggestions(champion_name)
                if suggestions:
                    print(f"💡 Did you mean: {', '.join(suggestions)}?")
                if self.champ_dict:
                    print(f"📊 Total champions loaded: {len(self.champ_dict)}")
                else:
                    print(f"⚠️  Champion list not loaded. Make sure League Client is running!")
                return False
            else:
                # Encontra o nome correto do campeão (com capitalização)
                correct_name = next((name for name in self.champ_dict.keys() if name == champion_name.lower()), champion_name.lower())
                self.auto_ban_champion = correct_name
                self.auto_ban_enabled = True
                return True

    def monitor_champ_select(self):
        """
        Monitora continuamente o estado da seleção de campeões e executa
        Instalock ou AutoBan quando apropriado.
        """
        last_action_id = None
        champion_list_updated = False
        
        while self.is_running:
            try:
                # Atualiza lista de campeões se ainda não foi feito
                if not champion_list_updated and not self.champ_dict:
                    if self.update_champion_list():
                        champion_list_updated = True
                
                champ_select_resp = self.rengar.lcu_request("GET", "/lol-champ-select/v1/session", "")
                
                # Verifica se está em seleção de campeões
                if champ_select_resp.status_code != 200 or "RPC_ERROR" in champ_select_resp.text:
                    time.sleep(0.5)
                    last_action_id = None
                    continue

                root_champ_select = champ_select_resp.json()
                cell_id = root_champ_select.get("localPlayerCellId")

                if cell_id is None:
                    time.sleep(0.3)
                    continue

                # Processa as ações disponíveis
                for actions in root_champ_select.get("actions", []):
                    if not isinstance(actions, list):
                        continue
                    
                    for action in actions:
                        # Verifica se é a vez do jogador local
                        if action.get("actorCellId") != cell_id:
                            continue
                        
                        # Evita processar a mesma ação múltiplas vezes
                        action_id = action.get("id")
                        if action.get("completed", False) or action_id == last_action_id:
                            continue
                        
                        # INSTALOCK - Pick de campeão (com sistema de backup)
                        if self.instalock_enabled and action.get("type") == "pick" and action.get("isInProgress", False):
                            champion_id = self.get_available_champion()

                            if champion_id != -1:
                                try:
                                    patch_resp = self.rengar.lcu_request(
                                        "PATCH",
                                        f"/lol-champ-select/v1/session/actions/{action_id}",
                                        {"completed": True, "championId": champion_id}
                                    )
                                    
                                    if patch_resp.status_code in [204, 200]:
                                        last_action_id = action_id
                                        print(f"✓ Champion picked successfully! (ID: {champion_id})")
                                except Exception as e:
                                    print(f"⚠️  Error picking champion: {e}")
                        
                        # AUTO BAN - Ban de campeão
                        elif self.auto_ban_enabled and action.get("type") == "ban" and action.get("isInProgress", False):
                            champion_id = self.champ_name_to_id(self.auto_ban_champion)

                            if champion_id != -1:
                                try:
                                    patch_resp = self.rengar.lcu_request(
                                        "PATCH",
                                        f"/lol-champ-select/v1/session/actions/{action_id}",
                                        {"completed": True, "championId": champion_id}
                                    )
                                    
                                    if patch_resp.status_code in [204, 200]:
                                        last_action_id = action_id
                                        print(f"✓ Champion banned successfully! ({self.auto_ban_champion})")
                                except Exception as e:
                                    print(f"⚠️  Error banning champion: {e}")

                time.sleep(0.2)
                
            except Exception as e:
                time.sleep(0.5)

    def toggle_instalock(self):
        """Alterna o estado do Instalock"""
        self.instalock_enabled = not self.instalock_enabled
        return self.instalock_enabled

    def toggle_auto_ban(self):
        """Alterna o estado do AutoBan"""
        self.auto_ban_enabled = not self.auto_ban_enabled
        return self.auto_ban_enabled

    def start_monitor(self):
        """Inicia o monitoramento em uma única thread"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self.monitor_champ_select, daemon=True)
            self.monitor_thread.start()

    def start_threads(self):
        """Método mantido para compatibilidade - inicia o monitor"""
        self.start_monitor()
    
    def stop(self):
        """Para o monitoramento"""
        self.is_running = False
    
    def get_instalock_status(self):
        """Retorna o status completo do instalock com backups"""
        status = f"{self.instalock_champion}"
        
        backups = []
        if self.instalock_backup_2 != "None":
            backups.append(f"2nd: {self.instalock_backup_2}")
        if self.instalock_backup_3 != "None":
            backups.append(f"3rd: {self.instalock_backup_3}")
        
        if backups:
            status += f" ({', '.join(backups)})"
        
        return status