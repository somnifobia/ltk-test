"""
Script para compilar o Tiamat League Toolkit em executável
Uso: python build_exe.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# ================================
# CONFIGURAÇÃO NOVA
# ================================
# Pasta onde *todas* as pastas de saída serão criadas
# Exemplo: "C:/TiamatBuilds"  ou  "output"
CUSTOM_OUTPUT_ROOT = "output_build"   # << ALTERE AQUI

# Pastas finais:
OUTPUT_DIR = os.path.join(CUSTOM_OUTPUT_ROOT, "dist")
BUILD_DIR = os.path.join(CUSTOM_OUTPUT_ROOT, "build")
# ================================

PROJECT_NAME = "LeagueToolKit"
MAIN_FILE = "main.py"
ICON_FILE = "tiamat.ico"


# Cores terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def check_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    try:
        import PyInstaller
        print_success(f"PyInstaller encontrado: v{PyInstaller.__version__}")
        return True
    except ImportError:
        print_warning("PyInstaller não encontrado")
        print_info("Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print_success("PyInstaller instalado com sucesso!")
            return True
        except Exception as e:
            print_error(f"Erro ao instalar PyInstaller: {e}")
            return False


def check_icon():
    """Verifica se o ícone existe"""
    if os.path.exists(ICON_FILE):
        print_success(f"Ícone encontrado: {ICON_FILE}")
        return True
    else:
        print_warning(f"Ícone não encontrado: {ICON_FILE}")
        print_info("O .exe será criado sem ícone personalizado")
        return False


def clean_build():
    """Limpa diretórios anteriores"""
    print_info("Limpando builds anteriores...")

    if os.path.exists(CUSTOM_OUTPUT_ROOT):
        try:
            shutil.rmtree(CUSTOM_OUTPUT_ROOT)
            print_success(f"Removido: {CUSTOM_OUTPUT_ROOT}")
        except Exception as e:
            print_warning(f"Não foi possível remover {CUSTOM_OUTPUT_ROOT}: {e}")

    # Remove arquivos .spec na raiz
    for spec_file in Path(".").glob("*.spec"):
        try:
            spec_file.unlink()
            print_success(f"Removido: {spec_file}")
        except Exception as e:
            print_warning(f"Não foi possível remover {spec_file}: {e}")


def get_data_files():
    data_files = []

    folders_to_include = [
        "ui", "core", "automation", "views",
        "icons", "themes", "assets", "resources",
    ]

    for folder in folders_to_include:
        if os.path.exists(folder):
            data_files.append(f"--add-data={folder};{folder}")
            print_success(f"Pasta incluída: {folder}")

    files_to_include = ["tiamat.ico", "config.json", "themes.json", "README.md"]

    for file in files_to_include:
        if os.path.exists(file):
            data_files.append(f"--add-data={file};.")
            print_success(f"Arquivo incluído: {file}")

    return data_files


def build_exe():
    print_header("COMPILANDO TIAMAT")

    # Cria pastas caso não existam
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(BUILD_DIR, exist_ok=True)

    cmd = [
        "pyinstaller",
        "--name=Tiamat",
        "--onefile",
        "--windowed",
        "--clean",
        f"--distpath={OUTPUT_DIR}",
        f"--workpath={BUILD_DIR}",
    ]

    if check_icon():
        cmd.append(f"--icon={ICON_FILE}")

    cmd.extend(get_data_files())

    hidden_imports = [
        "customtkinter", "PIL", "PIL._tkinter_finder", "requests",
        "urllib3", "certifi", "charset_normalizer", "idna",
    ]

    for module in hidden_imports:
        cmd.append(f"--hidden-import={module}")

    cmd.append(MAIN_FILE)

    print_info("Comando PyInstaller:")
    print(f"{Colors.OKCYAN}{' '.join(cmd)}{Colors.ENDC}\n")

    try:
        subprocess.check_call(cmd)
        print_success("Compilação concluída!")
        return True
    except Exception as e:
        print_error(f"Erro durante a compilação: {e}")
        return False


def create_batch_launcher():
    batch_path = os.path.join(OUTPUT_DIR, "Launch_Tiamat.bat")
    batch_content = f"""@echo off
title Tiamat League Toolkit
cd /d "%~dp0"
start "" "Tiamat.exe"
"""

    try:
        with open(batch_path, "w") as f:
            f.write(batch_content)
        print_success(f"Launcher criado: {batch_path}")
    except Exception as e:
        print_warning(f"Falha ao criar launcher: {e}")


def show_results():
    exe_path = os.path.join(OUTPUT_DIR, "Tiamat.exe")

    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 ** 2)

        print_header("RESULTADO")
        print_success(f"Executável criado: {exe_path}")
        print_info(f"Tamanho: {size_mb:.2f} MB")
        print_info(f"Pasta raiz: {os.path.abspath(CUSTOM_OUTPUT_ROOT)}")

        return True

    print_error("Executável não foi criado!")
    return False


def main():
    print_header("TIAMAT BUILD SCRIPT v1.1")

    if not os.path.exists(MAIN_FILE):
        print_error(f"Arquivo {MAIN_FILE} não encontrado!")
        return False

    print_success(f"Diretório do projeto: {os.getcwd()}")

    if not check_pyinstaller():
        return False

    clean_build()

    if not build_exe():
        return False

    create_batch_launcher()
    return show_results()


if __name__ == "__main__":
    try:
        success = main()
        print_header("BUILD COMPLETO!" if success else "BUILD FALHOU")
        input("\nPressione ENTER para sair...")
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print_error("Build cancelado.")
        sys.exit(1)
