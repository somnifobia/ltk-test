import webbrowser
import json
import requests
import time
from core import Rengar

class ChampionSelectNotFoundError(Exception):
    pass

def reveal():

    rengar = Rengar()
    
    try:
        champ_select = rengar.lcu_request("GET", "/lol-champ-select/v1/session", "")
        
        if champ_select.status_code != 200 or "RPC_ERROR" in champ_select.text:
            print("❌ Você não está em champion select")
            return None
            
        champ_select_data = champ_select.json()
        summ_names = []
        is_ranked = False
        
        if "myTeam" not in champ_select_data:
            print("⚠️ Dados do time não disponíveis")
            return None
        
        for player in champ_select_data["myTeam"]:
            if player.get("nameVisibilityType") == "HIDDEN":
                is_ranked = True
                print("🔒 Lobby ranked detectado - usando método alternativo")
                break
        
        if is_ranked:
            try:
                participants = rengar.riot_request("GET", "/chat/v5/participants", "")
                
                if participants.status_code == 200:
                    participants_data = participants.json()
                    
                    if "participants" in participants_data:
                        for participant in participants_data["participants"]:
                            cid = participant.get("cid", "")
                            
                            if "champ-select" in cid:
                                game_name = participant.get("game_name", "")
                                game_tag = participant.get("game_tag", "")
                                
                                if game_name and game_tag:
                                    summ_name = f"{game_name}%23{game_tag}"
                                    summ_names.append(summ_name)
                                    print(f"✅ Jogador encontrado: {game_name}#{game_tag}")
                    
                    if not summ_names:
                        print("⚠️ Nenhum jogador encontrado via chat API")
                else:
                    print(f"⚠️ Erro ao obter participantes: {participants.status_code}")
                    
            except Exception as e:
                print(f"❌ Erro ao buscar participantes ranked: {e}")
        
        else:
            print("🔓 Lobby normal detectado - usando método direto")
            
            for player in champ_select_data["myTeam"]:
                summoner_id = player.get("summonerId")
                
                if not summoner_id or summoner_id == "0":
                    continue
                
                try:
                    summoner = rengar.lcu_request("GET", f"/lol-summoner/v1/summoners/{summoner_id}", "")
                    
                    if summoner.status_code == 200:
                        summoner_data = summoner.json()
                        game_name = summoner_data.get("gameName", "")
                        tag_line = summoner_data.get("tagLine", "")
                        
                        if game_name and tag_line:
                            summ_name = f"{game_name}%23{tag_line}"
                            summ_names.append(summ_name)
                            print(f"✅ Jogador encontrado: {game_name}#{tag_line}")
                    else:
                        print(f"⚠️ Erro ao obter summoner {summoner_id}: {summoner.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Erro ao processar summoner {summoner_id}: {e}")
        
        if not summ_names:
            print("❌ Nenhum jogador encontrado no lobby")
            return None
        
        region = ""
        try:
            get_region = rengar.lcu_request("GET", "/riotclient/region-locale", "")
            
            if get_region.status_code == 200:
                region_data = get_region.json()
                region = region_data.get("webRegion", "")
                print(f"🌍 Região detectada: {region}")
            else:
                print(f"⚠️ Erro ao obter região: {get_region.status_code}")
                region = "br1"  
                
        except Exception as e:
            print(f"⚠️ Erro ao buscar região: {e}")
            region = "br1"  
        
        if not region:
            print("❌ Não foi possível determinar a região")
            return None
        
        summ_names_str = ",".join(summ_names)
        url = f"https://porofessor.gg/pregame/{region}/{summ_names_str}"
        
        print(f"\n🚀 Abrindo Porofessor...")
        print(f"🔗 URL: {url}\n")
        
        webbrowser.open(url)
        return url
        
    except ChampionSelectNotFoundError:
        print("❌ Champion select não encontrado")
        return None
        
    except Exception as e:
        print(f"❌ Erro no Lobby Reveal: {e}")
        import traceback
        traceback.print_exc()
        return None


def open_porofessor():
    return reveal()