import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import subprocess
import json
from ttkthemes import ThemedTk

# Fichier pour sauvegarder les paramètres
CONFIG_FILE = 'config.json'

# Liste des IDE et leurs exécutables typiques
possible_ides = {
    "Visual Studio Code": ["Code.exe", "code.exe"],
    "PyCharm": ["pycharm.exe"],
    "Sublime Text": ["sublime_text.exe", "sublime_text"],
    "IntelliJ IDEA": ["idea64.exe", "idea.exe"]
}

def load_config():
    """Charge les paramètres depuis le fichier config.json. Créé un fichier par défaut si nécessaire."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showwarning("Avertissement", "Le fichier de configuration est invalide. Création d'un nouveau fichier.")
            return {"code_editor": "", "custom_commands": {}}
    else:
        return {"code_editor": "", "custom_commands": {}}  # Valeur par défaut

def save_config(config):
    """Sauvegarde les paramètres dans le fichier config.json."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except IOError as e:
        messagebox.showerror("Erreur", f"Impossible de sauvegarder les paramètres : {e}")



config = load_config()

def find_ides_on_drive(drive, ides):
    """Recherche des IDE sur un disque donné."""
    found_ides = {}
    for root, dirs, files in os.walk(drive):
        for ide_name, executables in ides.items():
            for executable in executables:
                if executable in files:
                    path = os.path.join(root, executable)
                    found_ides[ide_name] = path
                    break
        if found_ides:
            break
    return found_ides

def detect_ides():
    """Détecte les IDE installés sur tous les disques durs."""
    ides = {}
    drives = [f"{d}:\\" for d in range(ord('C'), ord('Z')+1) if os.path.exists(f"{chr(d)}:\\")]
    for drive in drives:
        print(f"Recherche sur le disque {drive}...")
        found_ides = find_ides_on_drive(drive, possible_ides)
        ides.update(found_ides)
    return ides

def open_terminal():
    try:
        if os.name == 'nt':  # Windows
            os.startfile('cmd.exe')
        elif os.name == 'posix':  # Linux / macOS
            subprocess.Popen(['gnome-terminal'])  # Pour GNOME Terminal
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le terminal : {e}")

def open_code_editor():
    try:
        if config["code_editor"]:
            subprocess.Popen([config["code_editor"]])
        else:
            messagebox.showwarning("Avertissement", "Aucun éditeur de code configuré.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir l'éditeur de code : {e}")

def run_command(command):
    try:
        subprocess.Popen(command, shell=True)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'exécuter la commande : {e}")

def open_settings():
    def save_settings():
        editor = editor_var.get()
        if editor:
            config["code_editor"] = editor
            save_config(config)
            settings_window.destroy()
        else:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un IDE valide.")

    def add_custom_editor():
        path = filedialog.askopenfilename(title="Sélectionner l'IDE", filetypes=[("Executables", "*.exe")])
        if path:
            config["code_editor"] = path
            save_config(config)
            editor_var.set(path)
            messagebox.showinfo("Info", "IDE ajouté avec succès.")
        else:
            messagebox.showwarning("Avertissement", "Aucun fichier sélectionné.")

    def add_custom_command():
        def save_command():
            command_name = command_name_var.get()
            command = command_var.get()
            if command_name and command:
                config["custom_commands"][command_name] = command
                save_config(config)
                command_window.destroy()
                messagebox.showinfo("Info", "Commande ajoutée avec succès.")
            else:
                messagebox.showwarning("Avertissement", "Veuillez remplir tous les champs.")

        command_window = tk.Toplevel()
        command_window.title("Ajouter Commande Personnalisée")
        command_window.geometry("400x200")
        command_window.configure(bg="#2e2e2e")

        tk.Label(command_window, text="Nom de la Commande :", bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 12)).pack(pady=5)
        command_name_var = tk.StringVar()
        tk.Entry(command_window, textvariable=command_name_var, width=50).pack(pady=5)

        tk.Label(command_window, text="Commande :", bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 12)).pack(pady=5)
        command_var = tk.StringVar()
        tk.Entry(command_window, textvariable=command_var, width=50).pack(pady=5)

        tk.Button(command_window, text="Sauvegarder", command=save_command, bg="#28a745", fg="#ffffff", font=("Helvetica", 12, "bold"), relief="flat").pack(pady=10)

    settings_window = tk.Toplevel()
    settings_window.title("Paramètres")
    settings_window.geometry("400x400")
    settings_window.configure(bg="#2e2e2e")

    tk.Label(settings_window, text="Éditeur de Code :", bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 14, "bold")).pack(pady=10)

    ides = detect_ides()
    if not ides:
        tk.Label(settings_window, text="Aucun IDE détecté. Vous pouvez en ajouter manuellement.", bg="#2e2e2e", fg="#ff0000", font=("Helvetica", 12)).pack(pady=10)
        options = []
    else:
        options = list(ides.keys())
    
    editor_var = tk.StringVar(value=config.get("code_editor", ""))

    if options:
        editor_menu = tk.OptionMenu(settings_window, editor_var, *options)
    else:
        editor_menu = tk.OptionMenu(settings_window, editor_var, "Aucun IDE détecté")
        editor_menu.config(state=tk.DISABLED)
    editor_menu.config(bg="#444444", fg="#ffffff", highlightbackground="#888888")
    editor_menu.pack(pady=10)

    tk.Button(settings_window, text="Ajouter un IDE personnalisé", command=add_custom_editor, bg="#007bff", fg="#ffffff", font=("Helvetica", 12, "bold"), relief="flat").pack(pady=10)
    tk.Button(settings_window, text="Ajouter une Commande Personnalisée", command=add_custom_command, bg="#17a2b8", fg="#ffffff", font=("Helvetica", 12, "bold"), relief="flat").pack(pady=10)
    tk.Button(settings_window, text="Sauvegarder", command=save_settings, bg="#28a745", fg="#ffffff", font=("Helvetica", 12, "bold"), relief="flat").pack(pady=10)

def about_app():
    about_window = tk.Toplevel()
    about_window.title("À propos")
    about_window.geometry("400x300")
    about_window.configure(bg="#2e2e2e")
    
    # Chargez une image de logo si vous en avez un
    try:
        logo_image = Image.open("logo.png").resize((100, 100))
        logo_photo = ImageTk.PhotoImage(logo_image)
    except FileNotFoundError:
        logo_photo = None

    tk.Label(about_window, text="À propos de l'application", bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 16, "bold")).pack(pady=10)

    if logo_photo:
        tk.Label(about_window, image=logo_photo, bg="#2e2e2e").pack(pady=10)
    
    info_text = (
        "Version 1.0.0\n\n"
        "Développé par Louanne\n\n"
        "Pour plus d'infos, <Iris-Cin> sur Github"
    )
    tk.Label(about_window, text=info_text, bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 12), justify=tk.LEFT).pack(pady=10, padx=20)

    tk.Button(about_window, text="Fermer", command=about_window.destroy, bg="#dc3545", fg="#ffffff", font=("Helvetica", 12, "bold"), relief="flat").pack(pady=10)

def create_gui():
    root = ThemedTk(theme="breeze")  # Utilisation du thème Breeze
    root.title("Interface de Raccourcis Développeur")
    root.geometry("800x600")

    # Barre de navigation
    sidebar = tk.Frame(root, bg="#343a40", width=200, relief="raised", bd=2)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="Navigation", bg="#343a40", fg="#ffffff", font=("Helvetica", 14, "bold")).pack(pady=10)

    # Icônes pour les boutons (utilisez des images par défaut ou remplacez-les par vos propres images)
    try:
        settings_icon = Image.open("gear_icon.png").resize((24, 24))
        settings_icon = ImageTk.PhotoImage(settings_icon)
    except FileNotFoundError:
        settings_icon = None

    settings_button = tk.Button(sidebar, text=" Paramètres", image=settings_icon, compound=tk.LEFT, command=open_settings, bg="#28a745", fg="#ffffff", font=("Helvetica", 12, "bold"), relief="flat")
    settings_button.pack(pady=10, padx=10, fill=tk.X)

    try:
        about_icon = Image.open("info_icon.png").resize((24, 24))
        about_icon = ImageTk.PhotoImage(about_icon)
    except FileNotFoundError:
        about_icon = None

    about_button = tk.Button(sidebar, text=" À propos", image=about_icon, compound=tk.LEFT, command=about_app, bg="#17a2b8", fg="#ffffff", font=("Helvetica", 12, "bold"), relief="flat")
    about_button.pack(pady=10, padx=10, fill=tk.X)

    # Contenu principal
    main_frame = tk.Frame(root, bg="#2e2e2e")
    main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # En-tête
    tk.Label(main_frame, text="Interface de Raccourcis Développeur", bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 18, "bold")).pack(pady=20)

    # Boutons principaux
    tk.Button(main_frame, text="Ouvrir Terminal", command=open_terminal, bg="#007bff", fg="#ffffff", font=("Helvetica", 14, "bold"), relief="flat").pack(pady=10)
    tk.Button(main_frame, text="Ouvrir Éditeur de Code", command=open_code_editor, bg="#28a745", fg="#ffffff", font=("Helvetica", 14, "bold"), relief="flat").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
