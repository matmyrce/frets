import os
import sys
import shlex
import webbrowser
import subprocess
import threading
import time
import datetime
import random as _random
import calendar as _calendar
import textwrap
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque

try:
    import tkinter as tk
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter import simpledialog
    import tkinter.font as tkfont
except Exception as e:  # pragma: no cover
    print("Tkinter introuvable. Installez python-tk / tkinter.", file=sys.stderr)
    raise

# ---- Thème (couleurs "color 0a") ----
DEFAULT_BG = "#000000"
DEFAULT_FG = "#00ff00"

# ---- Police mono ----
def get_mono_font(root):
    """Retourne une police mono (TkFixedFont si dispo)."""
    try:
        return tkfont.nametofont("TkFixedFont")
    except tk.TclError:
        return tkfont.Font(root, family="Courier New", size=11)

# ---- Beep cross‑platform ----
def do_beep(frequency=750, duration_ms=120, root=None):
    """
    Sur Windows: winsound.Beep ; sinon: fallback root.bell() ou clignote en console.
    (Standard lib uniquement.)
    """
    try:
        import winsound  # type: ignore
        winsound.Beep(int(frequency), int(duration_ms))
    except Exception:
        if root is not None:
            try:
                root.bell()
            except Exception:
                pass

# ---- Outils : ouverture système ----
def open_system_path(path: Path):
    """Ouvre un fichier/dossier avec l’appli système par défaut (cross‑platform)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        raise RuntimeError(f"Impossible d’ouvrir {path} : {e}")

# ---- Génération intégrée d’un gros pool de mots (≥500) ----
# Pour garder le code compact, on génère des mots pseudo‑aléatoires reproductibles + un petit lot de vrais mots.
# Cela respecte la contrainte "intégrée au code", sans dépendances.
def _build_word_pool(min_count=650):
    seed = 1337
    rng = _random.Random(seed)
    syll = ["ba","be","bi","bo","bu","ca","ce","ci","co","cu","da","de","di","do","du",
            "fa","fe","fi","fo","fu","ga","ge","gi","go","gu","ha","he","hi","ho","hu",
            "ja","je","ji","jo","ju","ka","ke","ki","ko","ku","la","le","li","lo","lu",
            "ma","me","mi","mo","mu","na","ne","ni","no","nu","pa","pe","pi","po","pu",
            "ra","re","ri","ro","ru","sa","se","si","so","su","ta","te","ti","to","tu",
            "va","ve","vi","vo","vu","wa","we","wi","wo","wu","ya","ye","yi","yo","yu",
            "za","ze","zi","zo","zu"]
    base = [
        "ananas","biscotte","cumulus","dahu","échalote","fusee","guitare","hibiscus","iguane",
        "jonquille","koala","loutre","mangouste","narval","opale","pamplemousse","quinquina",
        "radar","salicorne","trombone","ukulele","valise","wampee","xylophone","yaourt","zéphyr",
        "abricot","banquise","capybara","domino","étoile","fakir","gondole","hamac","isthme",
        "javelot","kakapo","lacustre","magret","nectarine","onyx","palissade","quenelle","roche",
        "stalactite","toucan","uranium","vortex","wapiti","xylème","yeuse","zinnia"
    ]
    # générer des pseudo‑mots tri‑syllabiques
    words = set(base)
    while len(words) < min_count:
        wlen = rng.choice([2,3,3,4])
        w = "".join(rng.choice(syll) for _ in range(wlen))
        # quelques ajustements
        if rng.random() < 0.15:
            w = w.capitalize()
        words.add(w)
    return sorted(words)

RANDOM_WORDS = _build_word_pool()

# ---- Génération intégrée de 200 dictons/proverbes ----
def _build_dictons(count=200):
    fixed = [
        "À cœur vaillant rien d’impossible.",
        "Petit à petit, l’oiseau fait son nid.",
        "Qui sème le vent récolte la tempête.",
        "Il n’y a pas de fumée sans feu.",
        "Mieux vaut tard que jamais.",
        "L’habit ne fait pas le moine.",
        "Après la pluie, le beau temps.",
        "Les bons comptes font les bons amis.",
        "On ne fait pas d’omelette sans casser des œufs.",
        "Chacun voit midi à sa porte.",
        "La nuit porte conseil.",
        "À cheval donné on ne regarde pas les dents.",
        "Il ne faut pas vendre la peau de l’ours avant de l’avoir tué.",
        "Qui va doucement va sûrement.",
        "Tel père, tel fils.",
        "Il faut battre le fer quand il est chaud.",
        "Qui ne risque rien n’a rien.",
        "La faim chasse le loup hors du bois.",
        "Toutes les routes mènent à Rome.",
        "Rien ne sert de courir, il faut partir à point.",
        "Il n’y a que les idiots qui ne changent pas d’avis.",
        "Les petites rivières font les grands fleuves.",
        "Quand on parle du loup, on en voit la queue.",
        "Pierre qui roule n’amasse pas mousse.",
        "À bon entendeur, salut.",
        "Charbonnier est maître chez soi.",
        "On n’est jamais mieux servi que par soi‑même.",
        "Un tiens vaut mieux que deux tu l’auras.",
        "Qui peut le plus peut le moins.",
        "Mieux vaut prévenir que guérir.",
        "Tant va la cruche à l’eau qu’à la fin elle se casse.",
        "Qui veut voyager loin ménage sa monture.",
        "À chaque jour suffit sa peine.",
        "Qui vivra verra.",
        "Il n’y a pas de petites économies.",
        "L’erreur est humaine.",
        "On apprend en chutant.",
        "La fortune sourit aux audacieux.",
        "Bon sang ne saurait mentir.",
        "La parole est d’argent, le silence est d’or.",
        "Mieux vaut être seul que mal accompagné.",
        "La curiosité est un vilain défaut.",
        "C’est en forgeant qu’on devient forgeron.",
        "Qui aime bien châtie bien.",
        "Loin des yeux, loin du cœur.",
        "La patience est mère de toutes les vertus.",
        "À malin, malin et demi.",
        "Qui vole un œuf vole un bœuf.",
        "À bon chat, bon rat.",
        "Faute avouée à demi pardonnée.",
    ]
    # générer des dictons synthétiques mais plausibles
    animaux = ["coq","merle","pie","âne","loup","renard","hibou","corbeau","grillon","cigale",
               "rossignol","moineau","chouette","cheval","chèvre","brebis","taureau","chien","chat","lièvre"]
    effets = ["soleil", "pluie", "gel", "vent", "orage", "beau temps", "bruine", "neige", "grésil", "brume"]
    actions = [
        "Quand le {animal} chante tôt,", "{animal_cap} à la porte,", "Si le {animal} se tait,", 
        "Quand {animal} se cache,", "On dit que {animal} crie,", "Quand {animal} danse,",
        "Si {animal} s’agite,", "Quand {animal} rit,", "Si {animal} bâille,", "Quand {animal} siffle,"
    ]
    suites = [
        "{effet} s’annonce.", "attends‑toi à {effet}.", "le {effet} n’est pas loin.", "c’est signe de {effet}.",
        "bonjour le {effet}.", "le {effet} pointe.", "place au {effet}.", "méfie‑toi du {effet}.",
        "souvent vient le {effet}.", "on aura du {effet}."
    ]
    rng = _random.Random(20240812)
    generated = []
    while len(fixed) + len(generated) < count:
        a = rng.choice(actions)
        an = rng.choice(animaux)
        e = rng.choice(effets)
        s = rng.choice(suites)
        phrase = f"{a.replace('{animal}', an).replace('{animal_cap}', an.capitalize())} {s.replace('{effet}', e)}"
        generated.append(phrase)
    out = fixed + generated[: max(0, count-len(fixed))]
    return out

DICTONS = _build_dictons(200)

# ---- Structures pour le registre de commandes ----
@dataclass
class CommandSpec:
    func: callable
    desc: str
    aliases: list = field(default_factory=list)

# ---- Fenêtres utilitaires ----
class ThemedToplevel(tk.Toplevel):
    def __init__(self, app, title="Fenêtre"):
        super().__init__(app.root)
        self.app = app
        self.title(title)
        self.configure(bg=self.app.bg)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.app.register_window(self)
        self.bind("<Escape>", lambda e: self.destroy())
    def on_close(self):
        self.app.unregister_window(self)
        self.destroy()
    def apply_theme(self):
        self.configure(bg=self.app.bg)
        for w in self.winfo_children():
            self.app.themify(w)

# ---- Application principale ----
class TerminalApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FreeOS 2.0")
        # Thème
        self.bg = DEFAULT_BG
        self.fg = DEFAULT_FG
        self.font = get_mono_font(self.root)

        # UI principale
        self._build_ui()

        # État
        self.cwd = Path.cwd()
        self.dir_history = [self.cwd]
        self.last_target_file: Path | None = None
        self.child_windows = set()  # Toplevel gérés
        self.active_countdowns = []  # minuteurs actifs (objets avec .stop_event)
        self.active_timers = []      # chronomètres actifs
        self.pending_selector = None # ex: play (sélection)

        # Registre des commandes
        self.commands: dict[str, CommandSpec] = {}
        self._register_commands()

        # Affichage d’accueil
        self._banner()

    # ---------- UI construction ----------
    def _build_ui(self):
        self.root.configure(bg=self.bg)
        # Zone console (Text + Scrollbar)
        self.text = tk.Text(self.root, wrap="word", bg=self.bg, fg=self.fg,
                            insertbackground=self.fg, font=self.font,
                            undo=False, autoseparators=False, maxundo=-1, height=24)
        self.text.pack(side="top", fill="both", expand=True)
        self.text.config(state="disabled")
        # Scrollbar
        sb = tk.Scrollbar(self.root, command=self.text.yview)
        sb.pack(side="right", fill="y")
        self.text["yscrollcommand"] = sb.set
        # Menu contextuel simple (copier tout/copie selection)
        self._build_context_menu()

        # Entrée de commande
        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(side="bottom", fill="x")
        self.prompt = tk.Label(frame, text="> ", bg=self.bg, fg=self.fg, font=self.font)
        self.prompt.pack(side="left")
        self.entry = tk.Entry(frame, bg=self.bg, fg=self.fg, insertbackground=self.fg, font=self.font)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Up>", self.on_history_up)
        self.entry.bind("<Down>", self.on_history_down)
        self.entry.bind("<Control-l>", lambda e: (self.clear(), "break"))
        self.entry.focus_set()

        self.cmd_history = []
        self.history_index = None

        # Applique thème
        self.themify(self.root)

    def _build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0, bg=self.bg, fg=self.fg, activebackground="#003300", activeforeground=self.fg)
        self.menu.add_command(label="Copier", command=self.copy_selection)
        self.menu.add_command(label="Tout sélectionner", command=self.select_all)
        self.text.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def copy_selection(self):
        try:
            sel = self.text.selection_get()
        except Exception:
            sel = ""
        if sel:
            self.root.clipboard_clear()
            self.root.clipboard_append(sel)

    def select_all(self):
        self.text.tag_add("sel", "1.0", "end-1c")

    # ---------- Thème ----------
    def themify(self, widget):
        """Appliquer le thème vert/noir à un widget et ses enfants."""
        try:
            widget.configure(bg=self.bg, fg=self.fg)
        except Exception:
            try:
                widget.configure(bg=self.bg)
            except Exception:
                pass
        # Curseur insertion (Entry/Text)
        if isinstance(widget, (tk.Entry, tk.Text)):
            widget.configure(insertbackground=self.fg)
        for child in widget.winfo_children():
            self.themify(child)

    def set_colors(self, fg=None, bg=None):
        if fg: self.fg = fg
        if bg: self.bg = bg
        # Re‑applique thème
        self.themify(self.root)

    # ---------- IO console ----------
    def write(self, text=""):
        self.text.config(state="normal")
        self.text.insert("end", text + "\n")
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")

    # ---------- Bannière ----------
    def _banner(self):
        self.write("Welcome to FreeOS'  |  tapez 'help' pour l’aide")
        self.write(f"Dossier courant: {self.cwd}")
        self.write("")

    # ---------- Historique ----------
    def on_history_up(self, event):
        if not self.cmd_history:
            return "break"
        if self.history_index is None:
            self.history_index = len(self.cmd_history) - 1
        else:
            self.history_index = max(0, self.history_index - 1)
        self.entry.delete(0, "end")
        self.entry.insert(0, self.cmd_history[self.history_index])
        return "break"

    def on_history_down(self, event):
        if self.history_index is None:
            return "break"
        self.history_index = min(len(self.cmd_history)-1, self.history_index + 1)
        self.entry.delete(0, "end")
        self.entry.insert(0, self.cmd_history[self.history_index])
        if self.history_index == len(self.cmd_history)-1:
            self.history_index = None
        return "break"

    # ---------- Saisie/Parsing ----------
    def on_enter(self, event):
        line = self.entry.get().strip()
        self.entry.delete(0, "end")
        if not line:
            return
        self.write("> " + line)
        self.cmd_history.append(line)
        self.history_index = None

        # Gestion d’un éventuel "pending selector" (ex: play multi-match)
        if self.pending_selector is not None:
            handler = self.pending_selector
            self.pending_selector = None
            handler(line)
            return

        try:
            self.execute_command(line)
        except Exception as e:
            self.write(f"[erreur] {e!s}")

    def _split_cmd(self, line: str):
        try:
            parts = shlex.split(line)
        except Exception:
            # fallback très tolérant
            parts = line.strip().split()
        return parts

    def execute_command(self, line: str):
        parts = self._split_cmd(line)
        if not parts:
            return
        cmd_raw = parts[0]
        args = parts[1:]

        cmd = cmd_raw.lower()
        # aliases → canon
        for name, spec in self.commands.items():
            if cmd == name or cmd in spec.aliases:
                return spec.func(args)

        self.write(f"[commande inconnue] '{cmd_raw}'. Essayez 'help'.")

    # ---------- Gestion fenêtres ----------
    def register_window(self, win: tk.Toplevel):
        self.child_windows.add(win)

    def unregister_window(self, win: tk.Toplevel):
        if win in self.child_windows:
            self.child_windows.remove(win)

    def close_all_windows(self):
        for w in list(self.child_windows):
            try:
                w.destroy()
            except Exception:
                pass
        self.child_windows.clear()

    # ---------- Commandes ----------
    def _register_commands(self):
        self._add_cmd("help", self.cmd_help, desc="Afficher l’aide (colonne alignée, adapte la largeur).")
        self._add_cmd("cln", self.cmd_clear, desc="Nettoyer l’affichage du terminal.", aliases=["cls"])

        # fichiers & navigation
        self._add_cmd("dir", self.cmd_dir, desc="Lister les fichiers/dossiers du dossier courant.", aliases=["ls"])
        self._add_cmd("cd", self.cmd_cd, desc="Changer/afficher le dossier courant. cd - / -- / --- pour revenir en arrière.")
        self._add_cmd("cds", self.cmd_cds, desc="Créer un dossier (parents si besoin).")
        self._add_cmd("cfile", self.cmd_cfile, desc="Créer/éditer un fichier. Ex: cfile test.txt - \"du texte\"")
        self._add_cmd("play", self.cmd_play, desc="Ouvrir un fichier/dossier avec l’appli système (sélection si multiples).")

        # texte & site
        self._add_cmd("msg", self.cmd_msg, desc="Afficher un message tel quel.")
        self._add_cmd("i", self.cmd_i, desc="Ouvrir https://ffm.bio/myrce/ dans le navigateur.")

        # random & password
        self._add_cmd("random", self.cmd_random, desc="Menu aléatoire (mot / nombre / dicton).")
        self._add_cmd("password", self.cmd_password, desc="Générateur de mot de passe / passphrase (fenêtre).")

        # outils graphiques
        self._add_cmd("count", self.cmd_count, desc="Compteur cliquable (+/−).")
        self._add_cmd("calc", self.cmd_calc, desc="Calculatrice (0–9, + − × ÷, ., =, C).")
        self._add_cmd("color", self.cmd_color, desc="Changer la couleur texte/fond (fenêtre).")
        self._add_cmd("audio", self.cmd_audio, desc="Infos audio (fallback sans dépendances).")

        # jeux
        self._add_cmd("game", self.cmd_game, desc="Menu jeux (devine nombre, memory, pendu, morpion, échecs).")

        # temps / date / calendriers
        self._add_cmd("time", self.cmd_time, desc="Affiche HH:MM:SS ou 'time x' pour horloge (fenêtre).")
        self._add_cmd("timer", self.cmd_timer, desc="Chronomètre (fenêtre).")
        self._add_cmd("minuteur", self.cmd_minuteur, desc="Compte à rebours (bips à 0, répétés jusqu’à 'Stop m').")
        self._add_cmd("Stop", self.cmd_stop, desc="Stop m : arrête le minuteur. Syntaxe: 'Stop m'.")
        self._add_cmd("stop", self.cmd_stop, desc="Alias de 'Stop m'.")
        self._add_cmd("stop all", self.cmd_stop_all, desc="Arrêter/fermer toutes les sous‑fenêtres & timers.")

        self._add_cmd("cal", self.cmd_cal, desc="Calendrier du mois courant.")
        self._add_cmd("date", self.cmd_date, desc="Date du jour (jj.mm.aaaa).")

        # audio rec
        self._add_cmd("rec", self.cmd_rec, desc="Dictaphone (désactivé sans lib externe ; explication en fenêtre).")

        # sorties / arrêt
        self._add_cmd("exitapp", self.cmd_exitapp, desc="Fermer toutes les sous‑fenêtres/outils (terminal reste ouvert).")
        self._add_cmd("exit", self.cmd_exit, desc="Fermer l’application terminal.")
        self._add_cmd("shutup", self.cmd_shutup, desc="Affiche 'ok', attend 1s, stop all + ferme.")

    def _add_cmd(self, name, func, desc="", aliases=None):
        if aliases is None: aliases = []
        self.commands[name] = CommandSpec(func=func, desc=desc, aliases=aliases)

    # ---------- Implémentations ----------
    # help
    def cmd_help(self, args):
        # Mise en forme selon largeur de la Text
        # Estimation largeur en caractères
        # On mesure 80 colonnes par défaut, sinon via font measure
        try:
            px_width = self.text.winfo_width()
            char_w = self.font.measure("M") or 8
            cols = max(60, int(px_width / max(1, char_w)))
        except Exception:
            cols = 80

        left_col_w = max(len(name) for name in self.commands) + 8  # place pour alias
        left_col_w = min(left_col_w, 42)
        wrapper = textwrap.TextWrapper(width=cols-left_col_w, subsequent_indent="")

        lines = []
        lines.append("Commandes disponibles :")
        # Regrouper nom + alias
        items = []
        for name, spec in sorted(self.commands.items()):
            alias_str = ""
            if spec.aliases:
                alias_str = " (alias: " + ", ".join(spec.aliases) + ")"
            items.append((name + alias_str, spec.desc))
        for left, desc in items:
            left_txt = (left + " " * left_col_w)[:left_col_w]
            wrapped = textwrap.wrap(desc, width=cols-left_col_w) or [""]
            lines.append(left_txt + wrapped[0])
            for wline in wrapped[1:]:
                lines.append(" " * left_col_w + wline)
        self.write("\n".join(lines))

    def cmd_clear(self, args):
        self.clear()

    # dir / ls
    def cmd_dir(self, args):
        p = self.cwd
        try:
            names = sorted(os.listdir(p))
        except Exception as e:
            self.write(f"[erreur] {e}")
            return
        if not names:
            self.write("(vide)")
            return
        # afficher types
        out = []
        for n in names:
            path = p / n
            tag = "<DIR>" if path.is_dir() else "     "
            out.append(f"{tag}  {n}")
        self.write("\n".join(out))

    # cd
    def cmd_cd(self, args):
        if not args:
            self.write(str(self.cwd))
            return
        target = args[0]
        if target in ("-", "--", "---"):
            steps = target.count("-")
            if len(self.dir_history) <= 1:
                self.write("[info] historique vide.")
                return
            # Revenir N fois si possible
            for _ in range(steps):
                if len(self.dir_history) > 1:
                    self.dir_history.pop()  # supprime le courant
                else:
                    break
            new_dir = self.dir_history[-1]
            try:
                os.chdir(new_dir)
                self.cwd = Path.cwd()
                self.write(f"{self.cwd}")
            except Exception as e:
                self.write(f"[erreur] {e}")
            return

        # chemin relatif/absolu
        path = (self.cwd / target).resolve() if not os.path.isabs(target) else Path(target).resolve()
        if not path.exists() or not path.is_dir():
            self.write(f"[erreur] dossier introuvable : {path}")
            return
        try:
            os.chdir(path)
            self.cwd = Path.cwd()
            self.dir_history.append(self.cwd)
            self.write(str(self.cwd))
        except Exception as e:
            self.write(f"[erreur] {e}")

    def cmd_cds(self, args):
        if not args:
            self.write("[usage] cds <nom_dossier>")
            return
        path = (self.cwd / args[0]).resolve()
        try:
            path.mkdir(parents=True, exist_ok=True)
            self.write(f"Dossier créé : {path}")
        except Exception as e:
            self.write(f"[erreur] {e}")

    def _append_text_to_file(self, path: Path, text: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
            if not text.endswith("\n"):
                f.write("\n")

    def cmd_cfile(self, args):
        # Cas : cfile - <texte> (append au dernier ciblé)
        if args and args[0] == "-":
            if self.last_target_file is None:
                self.write("[erreur] aucun fichier ciblé (utilisez d’abord: cfile <nom> ...)")
                return
            texte = " ".join(args[1:]) if len(args) > 1 else ""
            self._append_text_to_file(self.last_target_file, texte)
            self.write(f"Ajouté à {self.last_target_file.name}.")
            return

        if not args:
            self.write("[usage] cfile <nom> [- <texte>]")
            return

        # cfile <nom> [- <texte>]
        nom = args[0]
        texte = ""
        if len(args) >= 3 and args[1] == "-":
            texte = " ".join(args[2:])
        path = (self.cwd / nom).resolve()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.touch()
            if texte:
                self._append_text_to_file(path, texte)
            self.last_target_file = path
            action = "Créé" if texte == "" else "Créé/édité"
            self.write(f"{action} : {path}")
        except Exception as e:
            self.write(f"[erreur] {e}")

    # play
    def cmd_play(self, args):
        if not args:
            self.write("[usage] play <nom_partiel_ou_exact>")
            return
        needle = args[0].lower()
        entries = list((self.cwd).iterdir())
        matches = [p for p in entries if needle in p.name.lower()]
        if not matches:
            self.write("[info] aucune correspondance.")
            return
        if len(matches) == 1:
            try:
                open_system_path(matches[0])
                self.write(f"[ouvert] {matches[0].name}")
            except Exception as e:
                self.write(f"[erreur] {e}")
            return
        # multiples → proposer sélection dans la console
        self.write("Plusieurs correspondances :")
        for i, p in enumerate(matches, 1):
            self.write(f"  {i:>2}: {p.name}")
        self.write("Choisissez un numéro puis appuyez Entrée.")
        def selection_handler(line):
            try:
                k = int(line.strip())
                if 1 <= k <= len(matches):
                    open_system_path(matches[k-1])
                    self.write(f"[ouvert] {matches[k-1].name}")
                else:
                    self.write("[info] sélection annulée.")
            except Exception:
                self.write("[info] sélection annulée.")
        self.pending_selector = selection_handler

    # msg
    def cmd_msg(self, args):
        self.write(" ".join(args))

    # i
    def cmd_i(self, args):
        url = "https://ffm.bio/myrce/"
        self.write(f"[ouvrir] {url}")
        try:
            webbrowser.open(url)
        except Exception:
            pass

    # random
    def cmd_random(self, args):
        if not args:
            # Ouvre une petite fenêtre avec 3 options
            win = ThemedToplevel(self, title="Random")
            lab = tk.Label(win, text="Choisissez :", bg=self.bg, fg=self.fg, font=self.font)
            lab.pack(padx=8, pady=8)
            btns = tk.Frame(win, bg=self.bg); btns.pack(padx=8, pady=8)
            tk.Button(btns, text="Mot", command=lambda: self._rand_wrd(win)).pack(side="left", padx=6)
            tk.Button(btns, text="Nombre", command=lambda: self._rand_nmbr(win)).pack(side="left", padx=6)
            tk.Button(btns, text="Dicton", command=lambda: self._rand_dicton(win)).pack(side="left", padx=6)
            self.themify(win)
            return
        # Sous-commandes
        sub = (args[0] or "").lower()
        if sub in ("wrd", "word", "mot"):
            self._rand_wrd(None)
        elif sub in ("nmbr", "nombre", "num", "number"):
            mn, mx = 0, 100
            if len(args) >= 3:
                try:
                    mn, mx = int(args[1]), int(args[2])
                except Exception:
                    pass
            self.write(str(_random.randint(mn, mx)))
        elif sub in ("dicton", "prov", "proverbe"):
            self._rand_dicton(None)
        else:
            self.write("[usage] random [wrd|nmbr [min max]|dicton]")

    def _rand_wrd(self, win):
        word = _random.choice(RANDOM_WORDS)
        self.write(word)
        if win: win.destroy()

    def _rand_nmbr(self, win):
        n = _random.randint(0, 100)
        self.write(str(n))
        if win: win.destroy()

    def _rand_dicton(self, win):
        d = _random.choice(DICTONS)
        self.write(d)
        if win: win.destroy()

    # password
    def cmd_password(self, args):
        win = ThemedToplevel(self, title="Générateur de mots de passe")
        fr = tk.Frame(win, bg=self.bg); fr.pack(padx=10, pady=10)

        var_len = tk.IntVar(value=16)
        var_uc = tk.BooleanVar(value=True)
        var_lc = tk.BooleanVar(value=True)
        var_dg = tk.BooleanVar(value=True)
        var_sy = tk.BooleanVar(value=False)
        var_passphrase = tk.BooleanVar(value=False)
        var_words = tk.IntVar(value=4)

        tk.Checkbutton(fr, text="Majuscules (A‑Z)", variable=var_uc, bg=self.bg, fg=self.fg, selectcolor=self.bg).grid(row=0, column=0, sticky="w")
        tk.Checkbutton(fr, text="Minuscules (a‑z)", variable=var_lc, bg=self.bg, fg=self.fg, selectcolor=self.bg).grid(row=1, column=0, sticky="w")
        tk.Checkbutton(fr, text="Chiffres (0‑9)", variable=var_dg, bg=self.bg, fg=self.fg, selectcolor=self.bg).grid(row=2, column=0, sticky="w")
        tk.Checkbutton(fr, text="Symboles (!@#…)", variable=var_sy, bg=self.bg, fg=self.fg, selectcolor=self.bg).grid(row=3, column=0, sticky="w")

        tk.Label(fr, text="Longueur :", bg=self.bg, fg=self.fg).grid(row=4, column=0, sticky="w")
        tk.Entry(fr, textvariable=var_len, bg=self.bg, fg=self.fg, insertbackground=self.fg).grid(row=4, column=1, sticky="we")

        tk.Checkbutton(fr, text="Mode passphrase (mots aléatoires)", variable=var_passphrase, bg=self.bg, fg=self.fg, selectcolor=self.bg).grid(row=5, column=0, sticky="w", columnspan=2)
        tk.Label(fr, text="Nb mots (2–6) :", bg=self.bg, fg=self.fg).grid(row=6, column=0, sticky="w")
        tk.Entry(fr, textvariable=var_words, bg=self.bg, fg=self.fg, insertbackground=self.fg).grid(row=6, column=1, sticky="we")

        out = tk.Entry(fr, bg=self.bg, fg=self.fg, insertbackground=self.fg, width=50)
        out.grid(row=7, column=0, columnspan=2, pady=8, sticky="we")

        def gen():
            if var_passphrase.get():
                k = max(2, min(6, int(var_words.get() or 4)))
                words = [_random.choice(RANDOM_WORDS) for _ in range(k)]
                pwd = "-".join(words)
            else:
                import string
                pools = ""
                if var_uc.get(): pools += string.ascii_uppercase
                if var_lc.get(): pools += string.ascii_lowercase
                if var_dg.get(): pools += string.digits
                if var_sy.get(): pools += "!@#$%^&*()-_=+[]{};:,.?/"
                if not pools:
                    pools = "abcdefghijklmnopqrstuvwxyz0123456789"
                L = max(4, min(256, int(var_len.get() or 16)))
                rnd = _random.SystemRandom()
                pwd = "".join(rnd.choice(pools) for _ in range(L))
            out.delete(0, "end"); out.insert(0, pwd)

        def copy():
            val = out.get()
            if not val: return
            self.root.clipboard_clear(); self.root.clipboard_append(val)
            messagebox.showinfo("Copié", "Mot de passe copié dans le presse‑papiers.", parent=win)

        btns = tk.Frame(fr, bg=self.bg); btns.grid(row=8, column=0, columnspan=2, pady=4)
        tk.Button(btns, text="Générer", command=gen).pack(side="left", padx=6)
        tk.Button(btns, text="Copier", command=copy).pack(side="left", padx=6)

        for i in range(2):
            fr.grid_columnconfigure(i, weight=1)

        self.themify(win)

    # count
    def cmd_count(self, args):
        win = ThemedToplevel(self, title="Compteur")
        val = tk.IntVar(value=0)
        lab = tk.Label(win, textvariable=val, bg=self.bg, fg=self.fg, font=tkfont.Font(win, size=36, family=self.font.actual("family")))
        lab.pack(padx=10, pady=10)
        fr = tk.Frame(win, bg=self.bg); fr.pack(pady=6)
        tk.Button(fr, text=" + ", command=lambda: val.set(val.get()+1)).pack(side="left", padx=6)
        tk.Button(fr, text=" − ", command=lambda: val.set(val.get()-1)).pack(side="left", padx=6)
        self.themify(win)

    # calc
    def cmd_calc(self, args):
        win = ThemedToplevel(self, title="Calculatrice")
        expr = tk.StringVar(value="")
        disp = tk.Entry(win, textvariable=expr, bg=self.bg, fg=self.fg, insertbackground=self.fg, font=self.font)
        disp.pack(fill="x", padx=10, pady=10)

        buttons = [
            "7","8","9","/",
            "4","5","6","*",
            "1","2","3","-",
            "0",".","=","+",
            "C"
        ]
        grid = tk.Frame(win, bg=self.bg); grid.pack(padx=10, pady=10)
        def on_btn(b):
            if b == "C":
                expr.set("")
            elif b == "=":
                try:
                    # Évaluation basique sécurisée
                    import ast, operator as op
                    allowed_ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
                                   ast.USub: op.neg}
                    def eval_(node):
                        if isinstance(node, ast.Num): return node.n
                        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
                            return -eval_(node.operand)
                        if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
                            return allowed_ops[type(node.op)](eval_(node.left), eval_(node.right))
                        raise ValueError("Expression non supportée")
                    tree = ast.parse(expr.get(), mode='eval')
                    res = eval_(tree.body)
                    expr.set(str(res))
                except Exception:
                    expr.set("Erreur")
            else:
                expr.set(expr.get()+b)
        r=c=0
        for b in buttons:
            tk.Button(grid, text=b, width=4, command=lambda x=b:on_btn(x)).grid(row=r, column=c, padx=4, pady=4)
            c+=1
            if c==4:
                r+=1; c=0
        self.themify(win)

    # color
    def cmd_color(self, args):
        win = ThemedToplevel(self, title="Couleurs")
        tk.Label(win, text="Texte (hex) :", bg=self.bg, fg=self.fg).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        efg = tk.Entry(win, bg=self.bg, fg=self.fg, insertbackground=self.fg); efg.insert(0, self.fg)
        efg.grid(row=0, column=1, sticky="we", padx=8, pady=6)
        tk.Label(win, text="Fond (hex) :", bg=self.bg, fg=self.fg).grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ebg = tk.Entry(win, bg=self.bg, fg=self.fg, insertbackground=self.fg); ebg.insert(0, self.bg)
        ebg.grid(row=1, column=1, sticky="we", padx=8, pady=6)

        fr = tk.Frame(win, bg=self.bg); fr.grid(row=2, column=0, columnspan=2, pady=8)
        presets = [
            ("Vert/Noir", DEFAULT_FG, DEFAULT_BG),
            ("Ambre/Noir", "#ffbf00", "#000000"),
            ("Vert doux/Noir", "#66ff66", "#000000"),
            ("Vert/Gris", "#00ff00", "#111111"),
        ]
        tk.Label(win, text="Presets :", bg=self.bg, fg=self.fg).grid(row=3, column=0, sticky="w", padx=8)
        pfr = tk.Frame(win, bg=self.bg); pfr.grid(row=3, column=1, sticky="we", padx=8)
        for name, fg, bg in presets:
            tk.Button(pfr, text=name, command=lambda f=fg,b=bg:(efg.delete(0,"end"),efg.insert(0,f),ebg.delete(0,"end"),ebg.insert(0,b))).pack(side="left", padx=4)

        def apply():
            fg = efg.get().strip() or self.fg
            bg = ebg.get().strip() or self.bg
            self.set_colors(fg, bg)
            # Appliquer aux fenêtres ouvertes
            for w in list(self.child_windows):
                try:
                    if hasattr(w, "apply_theme"):
                        w.apply_theme()
                    else:
                        self.themify(w)
                except Exception:
                    pass

        tk.Button(win, text="Appliquer", command=apply).grid(row=4, column=0, columnspan=2, pady=8)
        win.grid_columnconfigure(1, weight=1)
        self.themify(win)

    # audio
    def cmd_audio(self, args):
        # Sans dépendances externes, on ne peut pas interroger proprement les périphériques.
        # Fallback : tenter des commandes système si disponibles, sinon message clair.
        sub = (args[0].lower() if args else "")
        if sub in ("list","liste"):
            self._audio_list()
            return
        count_in, count_out = self._audio_counts_attempt()
        if count_in is None and count_out is None:
            self.write("Audio : non disponible sans dépendance externe.")
        else:
            self.write(f"Entrées audio détectées (approx) : {count_in}")
            self.write(f"Sorties audio détectées (approx) : {count_out}")
            self.write("(Détection via commandes système si présentes ; résultats non garantis.)")

    def _audio_counts_attempt(self):
        # Tentatives approximatives :
        try:
            if sys.platform == "darwin":
                # macOS : system_profiler
                out = subprocess.check_output(["system_profiler", "SPAudioDataType"], text=True, timeout=3)
                ei = out.count("Input:")
                eo = out.count("Output:")
                return ei or 0, eo or 0
            elif sys.platform.startswith("linux"):
                # Linux : pactl (si présent)
                try:
                    src = subprocess.check_output(["pactl", "list", "short", "sources"], text=True, timeout=2)
                    snk = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True, timeout=2)
                    ci = len([l for l in src.splitlines() if l.strip()])
                    co = len([l for l in snk.splitlines() if l.strip()])
                    return ci, co
                except Exception:
                    return None, None
            elif sys.platform.startswith("win"):
                # Windows : sans lib externe, pas d’API simple ; abandon propre
                return None, None
        except Exception:
            pass
        return None, None

    def _audio_list(self):
        if sys.platform == "darwin":
            try:
                out = subprocess.check_output(["system_profiler", "SPAudioDataType"], text=True, timeout=3)
                self.write(out.strip() or "(vide)")
                return
            except Exception:
                pass
        if sys.platform.startswith("linux"):
            try:
                out1 = subprocess.check_output(["pactl", "list", "short", "sources"], text=True, timeout=3)
                out2 = subprocess.check_output(["pactl", "list", "short", "sinks"], text=True, timeout=3)
                self.write("=== Sources ==="); self.write(out1.strip() or "(vide)")
                self.write("=== Sinks ==="); self.write(out2.strip() or "(vide)")
                return
            except Exception:
                pass
        self.write("audio list : non disponible sans dépendance externe.")

    # game
    def cmd_game(self, args):
        win = ThemedToplevel(self, title="Jeux")
        tk.Label(win, text="Choisissez un jeu :", bg=self.bg, fg=self.fg, font=self.font).pack(padx=10, pady=10)
        fr = tk.Frame(win, bg=self.bg); fr.pack(padx=10, pady=10)
        tk.Button(fr, text="Devine un nombre", command=lambda: self._game_guess()).pack(fill="x", pady=3)
        tk.Button(fr, text="Memory (16 cases)", command=lambda: self._game_memory()).pack(fill="x", pady=3)
        tk.Button(fr, text="Pendu", command=lambda: self._game_pendu()).pack(fill="x", pady=3)
        tk.Button(fr, text="Morpion ASCII (2 joueurs)", command=lambda: self._game_morpion()).pack(fill="x", pady=3)
        tk.Button(fr, text="Échecs (texte)", command=lambda: self._game_chess_text()).pack(fill="x", pady=3)
        tk.Button(fr, text="Échecs (fenêtre)", command=lambda: self._game_chess_gui()).pack(fill="x", pady=3)
        self.themify(win)

    # -- Devine un nombre
    def _game_guess(self):
        win = ThemedToplevel(self, title="Devine un nombre (1..100)")
        secret = _random.randint(1, 100)
        info = tk.StringVar(value="Je pense à un nombre entre 1 et 100.")
        tk.Label(win, textvariable=info, bg=self.bg, fg=self.fg).pack(padx=10, pady=10)
        e = tk.Entry(win, bg=self.bg, fg=self.fg, insertbackground=self.fg); e.pack(padx=10, pady=10)
        e.focus_set()
        def check(_=None):
            try:
                g = int(e.get().strip())
            except Exception:
                info.set("Entre un entier valide.")
                return
            if g < secret: info.set("Plus grand.")
            elif g > secret: info.set("Plus petit.")
            else:
                info.set("Bravo !")
                do_beep(root=self.root); do_beep(root=self.root); do_beep(root=self.root)
        e.bind("<Return>", check)
        tk.Button(win, text="Tester", command=check).pack(pady=6)
        self.themify(win)

    # -- Memory (16)
    def _game_memory(self):
        win = ThemedToplevel(self, title="Memory 4x4")
        symbols = list("🍎🍐🍊🍋🍉🍇🍓🍒")  # 8 paires
        cards = symbols * 2
        rng = _random.Random()
        rng.shuffle(cards)
        state = {"first": None, "second": None, "found": set(), "moves": 0}
        grid = tk.Frame(win, bg=self.bg); grid.pack(padx=10, pady=10)
        btns = []
        def show(i):
            if i in state["found"]:
                return
            b = btns[i]
            b.config(text=cards[i])
            if state["first"] is None:
                state["first"] = i
            elif state["second"] is None and i != state["first"]:
                state["second"] = i
                self.root.after(600, check)
        def check():
            a, b = state["first"], state["second"]
            if a is None or b is None: return
            if cards[a] == cards[b]:
                state["found"].update((a,b))
                btns[a].config(state="disabled"); btns[b].config(state="disabled")
            else:
                btns[a].config(text="■"); btns[b].config(text="■")
            state["first"]=state["second"]=None
            state["moves"] += 1
            if len(state["found"]) == 16:
                messagebox.showinfo("Terminé", f"Bravo ! Coups: {state['moves']}", parent=win)
        for r in range(4):
            for c in range(4):
                i = r*4+c
                b = tk.Button(grid, text="■", width=4, height=2, command=lambda k=i: show(k))
                b.grid(row=r, column=c, padx=4, pady=4)
                btns.append(b)
        self.themify(win)

    # -- Pendu
    def _game_pendu(self):
        win = ThemedToplevel(self, title="Pendu")
        word = _random.choice(RANDOM_WORDS).lower()
        hidden = ["_" if ch.isalpha() else ch for ch in word]
        tries = 8
        tried = set()

        info = tk.StringVar(value=f"Mot : {' '.join(hidden)}    Restant: {tries}")
        tk.Label(win, textvariable=info, bg=self.bg, fg=self.fg, font=self.font).pack(padx=10, pady=10)
        e = tk.Entry(win, bg=self.bg, fg=self.fg, insertbackground=self.fg); e.pack(padx=10, pady=6)
        e.focus_set()

        def update_info():
            info.set(f"Mot : {' '.join(hidden)}    Lettres: {', '.join(sorted(tried))}    Restant: {tries}")

        def guess(_=None):
            nonlocal tries
            g = e.get().strip().lower()
            e.delete(0, "end")
            if not g: return
            if len(g) == 1:
                if g in tried: return
                tried.add(g)
                if g in word:
                    for i,ch in enumerate(word):
                        if ch == g: hidden[i] = g
                else:
                    tries -= 1
            else:
                if g == word:
                    for i, ch in enumerate(word):
                        hidden[i] = ch
                else:
                    tries -= 1
            update_info()
            if "_" not in hidden:
                messagebox.showinfo("Gagné", f"Bravo ! Le mot était '{word}'.", parent=win)
            elif tries <= 0:
                messagebox.showinfo("Perdu", f"Dommage. Le mot était '{word}'.", parent=win)

        e.bind("<Return>", guess)
        tk.Button(win, text="Proposer", command=guess).pack(pady=6)
        self.themify(win)

    # -- Morpion ASCII (2 joueurs) dans une fenêtre (affichage texte)
    def _game_morpion(self):
        win = ThemedToplevel(self, title="Morpion ASCII (2 joueurs)")
        board = [" "]*9
        player = ["X"]
        info = tk.StringVar()

        def render():
            s = (f" {board[0]} | {board[1]} | {board[2]}\n"
                 f"---+---+---\n"
                 f" {board[3]} | {board[4]} | {board[5]}\n"
                 f"---+---+---\n"
                 f" {board[6]} | {board[7]} | {board[8]}\n")
            lab_board.config(text=s)
            info.set(f"Au tour de {player[0]}. Entrez 1..9.")

        def winner(bd):
            lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
            for a,b,c in lines:
                if bd[a] != " " and bd[a]==bd[b]==bd[c]:
                    return bd[a]
            if all(x != " " for x in bd):
                return "egal"
            return None

        lab_board = tk.Label(win, text="", bg=self.bg, fg=self.fg, font=self.font, justify="left")
        lab_board.pack(padx=10, pady=10)
        tk.Label(win, textvariable=info, bg=self.bg, fg=self.fg).pack()
        e = tk.Entry(win, bg=self.bg, fg=self.fg, insertbackground=self.fg); e.pack(padx=10, pady=8)
        e.focus_set()

        def play(_=None):
            v = e.get().strip(); e.delete(0, "end")
            if v not in [str(i) for i in range(1,10)]:
                info.set("Entrez 1..9.")
                return
            k = int(v)-1
            if board[k] != " ":
                info.set("Case déjà prise.")
                return
            board[k] = player[0]
            w = winner(board)
            render()
            if w == "egal":
                messagebox.showinfo("Morpion", "Égalité.", parent=win)
            elif w in ("X","O"):
                messagebox.showinfo("Morpion", f"Victoire de {w}.", parent=win)
            else:
                player[0] = "O" if player[0]=="X" else "X"

        e.bind("<Return>", play)
        tk.Button(win, text="Jouer", command=play).pack(pady=6)
        render()
        self.themify(win)

    # -- Échecs (texte) : validation basique + affichage ASCII
    def _game_chess_text(self):
        win = ThemedToplevel(self, title="Échecs (texte)")
        # Représentation simple
        board = self._chess_start_board()
        turn = ["w"]
        info = tk.StringVar(value="Entrez les coups (ex: e2 e4). Pas de roque/en passant/promo.")
        lab = tk.Label(win, text=self._chess_board_ascii(board), bg=self.bg, fg=self.fg, font=self.font, justify="left")
        lab.pack(padx=10, pady=10)
        tk.Label(win, textvariable=info, bg=self.bg, fg=self.fg).pack()
        e = tk.Entry(win, bg=self.bg, fg=self.fg, insertbackground=self.fg); e.pack(padx=10, pady=6)
        e.focus_set()

        def play(_=None):
            mv = e.get().strip().lower(); e.delete(0,"end")
            parts = mv.split()
            if len(parts)!=2 or not all(len(p)==2 for p in parts):
                info.set("Format: e2 e4")
                return
            src, dst = parts
            ok, msg = self._chess_try_move(board, turn[0], src, dst)
            if not ok:
                info.set(msg)
                return
            lab.config(text=self._chess_board_ascii(board))
            turn[0] = "b" if turn[0]=="w" else "w"
            info.set(f"Au tour de {'blancs' if turn[0]=='w' else 'noirs'}.")

        e.bind("<Return>", play)
        tk.Button(win, text="Jouer", command=play).pack(pady=6)
        self.themify(win)

    # -- Échecs (fenêtre) : graphique minimal
    def _game_chess_gui(self):
        win = ThemedToplevel(self, title="Échecs (fenêtre)")
        size = 56
        canvas = tk.Canvas(win, width=size*8, height=size*8, highlightthickness=0, bg=self.bg)
        canvas.pack(padx=10, pady=10)
        board = self._chess_start_board()
        turn = ["w"]
        selected = [None]

        def draw():
            canvas.delete("all")
            for r in range(8):
                for c in range(8):
                    x0, y0 = c*size, r*size
                    color = "#111111" if (r+c)%2==0 else "#222222"
                    canvas.create_rectangle(x0, y0, x0+size, y0+size, fill=color, outline="#333333")
                    piece = board[r][c]
                    if piece != ".":
                        canvas.create_text(x0+size/2, y0+size/2, text=self._chess_piece_symbol(piece),
                                           fill=self.fg, font=tkfont.Font(win, size=28, family=self.font.actual("family")))
            if selected[0]:
                r,c = selected[0]
                canvas.create_rectangle(c*size+2, r*size+2, c*size+size-2, r*size+size-2, outline="#00aa00", width=2)

        def on_click(event):
            c = event.x // size; r = event.y // size
            if r<0 or r>7 or c<0 or c>7: return
            if selected[0] is None:
                # Sélectionner une pièce du bon camp
                pc = board[r][c]
                if pc != "." and ((pc.isupper() and turn[0]=="w") or (pc.islower() and turn[0]=="b")):
                    selected[0] = (r,c)
            else:
                r0,c0 = selected[0]
                src = self._chess_idx_to_sq(r0,c0); dst = self._chess_idx_to_sq(r,c)
                ok, msg = self._chess_try_move(board, turn[0], src, dst)
                if ok:
                    turn[0] = "b" if turn[0]=="w" else "w"
                selected[0] = None
            draw()

        canvas.bind("<Button-1>", on_click)
        draw()
        self.themify(win)

    # --- Helpers Échecs ---
    def _chess_start_board(self):
        # Représentation: lettres blanches MAJ, noires min ; p=pion, r=tour, n=cavalier, b=fou, q=dame, k=roi
        # Rang 8 → index 0
        rows = [
            list("rnbqkbnr"),
            list("pppppppp"),
            list("........"),
            list("........"),
            list("........"),
            list("........"),
            list("PPPPPPPP"),
            list("RNBQKBNR"),
        ]
        return [row[:] for row in rows]

    def _chess_board_ascii(self, board):
        lines = []
        for i, row in enumerate(board):
            rank = 8 - i
            line = f"{rank} "
            for ch in row:
                line += (ch if ch != "." else "·") + " "
            lines.append(line)
        lines.append("  a b c d e f g h")
        return "\n".join(lines)

    def _chess_piece_symbol(self, p):
        symbols = {
            "K":"♔","Q":"♕","R":"♖","B":"♗","N":"♘","P":"♙",
            "k":"♚","q":"♛","r":"♜","b":"♝","n":"♞","p":"♟",
        }
        return symbols.get(p, "?")

    def _chess_sq_to_idx(self, sq):
        file = "abcdefgh".find(sq[0])
        rank = int(sq[1])
        r = 8 - rank
        c = file
        return r,c

    def _chess_idx_to_sq(self, r,c):
        return "abcdefgh"[c] + str(8-r)

    def _chess_try_move(self, board, turn, src, dst):
        # Validation basique: respect des mouvements, pas de roque/en passant/promo.
        try:
            r0,c0 = self._chess_sq_to_idx(src)
            r1,c1 = self._chess_sq_to_idx(dst)
        except Exception:
            return False, "Coordonnées invalides."
        pc = board[r0][c0]
        if pc == ".":
            return False, "Case source vide."
        if turn=="w" and not pc.isupper(): return False, "C’est aux blancs."
        if turn=="b" and not pc.islower(): return False, "C’est aux noirs."
        target = board[r1][c1]
        if target != "." and (target.isupper()==pc.isupper()):
            return False, "Case occupée par une pièce alliée."

        dr = r1 - r0; dc = c1 - c0
        absdr, absdc = abs(dr), abs(dc)
        name = pc.upper()

        def path_clear():
            # pour les pièces glissantes
            if dr==0 and dc==0: return False
            stepr = (0 if dr==0 else (1 if dr>0 else -1))
            stepc = (0 if dc==0 else (1 if dc>0 else -1))
            r, c = r0+stepr, c0+stepc
            while (r,c) != (r1,c1):
                if board[r][c] != ".":
                    return False
                r += stepr; c += stepc
            return True

        ok=False
        if name == "P":
            dir = -1 if pc.isupper() else 1  # blanc vers r-1, noir vers r+1
            start_row = 6 if pc.isupper() else 1
            if dc==0 and target==".":
                if dr == dir:
                    ok=True
                elif dr == 2*dir and r0==start_row and board[r0+dir][c0]=="." and board[r1][c1]==".":
                    ok=True
            elif absdc==1 and dr==dir and target!="." and (target.isupper()!=pc.isupper()):
                ok=True
        elif name == "N":
            ok = (absdr,absdc) in [(1,2),(2,1)]
        elif name == "B":
            ok = absdr==absdc and path_clear()
        elif name == "R":
            ok = (dr==0 or dc==0) and path_clear()
        elif name == "Q":
            ok = ((dr==0 or dc==0) or (absdr==absdc)) and path_clear()
        elif name == "K":
            ok = max(absdr,absdc)==1

        if not ok:
            return False, "Coup illégal."
        # effectuer le coup
        board[r1][c1] = pc
        board[r0][c0] = "."
        return True, "ok"

    # time
    def cmd_time(self, args):
        if args and args[0].lower() in ("x","X"):
            win = ThemedToplevel(self, title="Horloge")
            lab = tk.Label(win, text="", bg=self.bg, fg=self.fg, font=tkfont.Font(win, size=24, family=self.font.actual("family")))
            lab.pack(padx=10, pady=10)
            def tick():
                try:
                    now = time.strftime("%H:%M:%S")
                    lab.config(text=now)
                    if win.winfo_exists():
                        self.root.after(500, tick)
                except Exception:
                    pass
            tick()
            self.themify(win)
        else:
            now = time.strftime("%H:%M:%S")
            self.write(now)

    # timer (chronomètre)
    def cmd_timer(self, args):
        win = ThemedToplevel(self, title="Chronomètre (cliquer = start/stop)")
        lab = tk.Label(win, text="00:00:00.0", bg=self.bg, fg=self.fg, font=tkfont.Font(win, size=24, family=self.font.actual("family")))
        lab.pack(padx=10, pady=10)
        running = {"on": False, "start": 0.0, "elapsed": 0.0}
        def update():
            if running["on"]:
                elapsed = running["elapsed"] + (time.perf_counter() - running["start"])
                lab.config(text=self._fmt_hms(elapsed))
            if win.winfo_exists():
                self.root.after(100, update)
        def toggle(_=None):
            if not running["on"]:
                running["on"] = True; running["start"] = time.perf_counter()
            else:
                running["elapsed"] += (time.perf_counter() - running["start"])
                running["on"] = False
        lab.bind("<Button-1>", toggle)
        update()
        self.themify(win)
        self.active_timers.append(win)

    def _fmt_hms(self, seconds):
        h = int(seconds//3600); m = int((seconds%3600)//60); s = seconds%60
        return f"{h:02d}:{m:02d}:{s:04.1f}"

    # minuteur
    def cmd_minuteur(self, args):
        if not args:
            self.write("[usage] minuteur <hh:mm[:ss]>")
            return
        total = self._parse_hms(args[0])
        if total is None:
            self.write("[erreur] format invalide (hh:mm[:ss])")
            return
        # Fenêtre
        win = ThemedToplevel(self, title="Minuteur")
        var = tk.StringVar(value=self._fmt_hhmmss(total))
        lab = tk.Label(win, textvariable=var, bg=self.bg, fg=self.fg, font=tkfont.Font(win, size=28, family=self.font.actual("family")))
        lab.pack(padx=10, pady=10)
        stop_event = threading.Event()

        class Minuteur:
            pass
        tracker = Minuteur()
        tracker.stop_event = stop_event
        tracker.win = win
        self.active_countdowns.append(tracker)

        def countdown():
            nonlocal total
            if stop_event.is_set():
                return
            if total > 0:
                total -= 1
                var.set(self._fmt_hhmmss(total))
                self.root.after(1000, countdown)
            else:
                # À 0 : trois bips courts, pause, et répéter jusqu'à Stop m
                self._minuteur_alarm_loop(stop_event, lab)

        lab.bind("<Button-1>", lambda e: stop_event.set())
        countdown()
        self.themify(win)

    def _minuteur_alarm_loop(self, stop_event, label_widget):
        def loop():
            if stop_event.is_set() or not label_widget.winfo_exists():
                return
            for _ in range(3):
                if stop_event.is_set(): return
                do_beep(root=self.root)
                time.sleep(0.12)
            # clignoter
            for _ in range(3):
                if stop_event.is_set(): return
                try:
                    label_widget.config(fg="#ffffff"); time.sleep(0.15)
                    label_widget.config(fg=self.fg); time.sleep(0.15)
                except Exception:
                    break
            # pause et recommencer
            if not stop_event.is_set():
                self.root.after(1500, loop)
        threading.Thread(target=loop, daemon=True).start()

    def _parse_hms(self, s):
        parts = s.split(":")
        try:
            if len(parts)==2:
                h,m = int(parts[0]), int(parts[1]); sec=0
            elif len(parts)==3:
                h,m,sec = int(parts[0]), int(parts[1]), int(parts[2])
            else:
                return None
            return h*3600 + m*60 + sec
        except Exception:
            return None

    def _fmt_hhmmss(self, t):
        h = t//3600; m = (t%3600)//60; s = t%60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def cmd_stop(self, args):
        # Syntaxe attendue : "Stop m" ; tolérons aussi "stop m"
        if args and args[0].lower().startswith("m"):
            stopped = 0
            for tr in self.active_countdowns:
                try:
                    tr.stop_event.set(); stopped += 1
                    if tr.win and tr.win.winfo_exists():
                        tr.win.destroy()
                except Exception:
                    pass
            self.active_countdowns.clear()
            self.write(f"[minuteur] arrêté(s) : {stopped}")
        else:
            self.write("Usage: Stop m  (arrête le minuteur)")

    def cmd_stop_all(self, args):
        # Fermer toutes les sous‑fenêtres et arrêter minuteurs
        self.cmd_stop(["m"])
        self.close_all_windows()
        self.write("[stop all] toutes les sous‑fenêtres/timers arrêtés.")

    # cal / date
    def cmd_cal(self, args):
        now = datetime.date.today()
        cal = _calendar.month(now.year, now.month)
        self.write(cal.rstrip())

    def cmd_date(self, args):
        d = datetime.date.today()
        self.write(d.strftime("%d.%m.%Y"))

    # rec (dictaphone)
    def cmd_rec(self, args):
        # Sans lib externe (pyaudio/sounddevice/winsdk), on ne peut pas enregistrer le micro.
        # On crée une fenêtre expliquant le fallback/limitation.
        win = ThemedToplevel(self, title="Dictaphone (désactivé)")
        msg = (
            "Enregistrement audio : non disponible sans dépendance externe.\n\n"
            "- MP3 : impossible sans bibliothèque tierce.\n"
            "- WAV : l’enregistrement micro n’est pas accessible via la seule bibliothèque standard.\n\n"
            "Fallback : cette fonction est désactivée proprement pour éviter tout plantage.\n"
            "Astuce : installez par ex. 'sounddevice' + 'scipy' pour un vrai dictaphone (hors périmètre demandé)."
        )
        tk.Label(win, text=msg, bg=self.bg, fg=self.fg, justify="left", font=self.font).pack(padx=12, pady=12)
        self.themify(win)

    # exitapp / exit / shutup
    def cmd_exitapp(self, args):
        self.close_all_windows()
        self.write("[exitapp] fenêtres/outils fermés.")

    def cmd_exit(self, args):
        self.root.after(10, self.root.destroy)

    def cmd_shutup(self, args):
        self.write("ok")
        def later():
            self.cmd_stop_all([])
            self.cmd_exit([])
        self.root.after(1000, later)

    # ---------- Boucle ----------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = TerminalApp()
    app.run()