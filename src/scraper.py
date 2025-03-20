import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from utilities import *
from datetime import datetime
import os
import threading
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(base_path, "..", relative_path))

img_path = resource_path(r"img\f1.png")

def atualizar_label(label_status, pontos):
    label_status.configure(text=f"Realizando consulta{'.' * pontos}")
    pontos = (pontos + 1) % 4
    label_status.after(1000, atualizar_label, label_status, pontos)

def iniciar_consulta(label_status, btn_consulta):
    season_year = entry.get().strip()

    if not season_year.isdigit():
        messagebox.showerror("Erro", "Por favor, insira um ano válido.")
        return

    season_year = int(season_year)
    if not (1950 <= season_year <= datetime.today().year):
        messagebox.showerror("Erro", f"Ano {season_year} inválido! Escolha entre 1950 e {datetime.today().year}.")
        return

    create_logger(project_name="Captura_Resultados_Scraper")

    label_status.configure(text="Realizando consulta")
    atualizar_label(label_status, 1)

    label_status.pack()
    btn_consulta.pack_forget()

    try:
        capture_scraper(season_year=season_year)
        label_status.after(0, label_status.configure, {"text": ""})
        messagebox.showinfo("Concluído", f"Captura da temporada {season_year} finalizada com sucesso!")
    except Exception as e:
        label_status.after(0, label_status.configure, {"text": ""})
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    finally:
        btn_consulta.pack(pady=10)
        label_status.pack_forget()

def iniciar_thread(label_status, btn_consulta):
    thread = threading.Thread(target=iniciar_consulta, args=(label_status, btn_consulta))
    thread.start()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Consulta de Temporadas F1 - Scraper")
root.geometry("400x300")
root.resizable(False, False)

if os.path.exists(img_path):
    try:
        img = Image.open(img_path)
        img = img.resize((256, 64), Image.LANCZOS)
        img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(256, 64))

        label_img = ctk.CTkLabel(root, text=" ", image=img_tk)
        label_img.image = img_tk
        label_img.pack(pady=10)
    except Exception as e:
        print(f"Erro ao carregar imagem: {e}")
else:
    print(f"Imagem não encontrada: {img_path}")

label_texto = ctk.CTkLabel(root, text="Insira o ano da temporada desejado", font=("Arial", 12))
label_texto.pack(pady=(5, 10))

entry = ctk.CTkEntry(root, font=("Arial", 12), justify="center")
entry.pack(pady=5)

btn_consulta = ctk.CTkButton(root, text="Iniciar Consulta", font=("Arial", 12), command=lambda: iniciar_thread(label_status, btn_consulta))
btn_consulta.pack(pady=10)

label_status = ctk.CTkLabel(root, text=" ", font=("Arial", 12))
label_status.pack(pady=10)

root.mainloop()
