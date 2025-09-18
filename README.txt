FreeOS est un mini-terminal graphique écrit en Python/Tkinter, avec le style rétro de color 0a (fond noir, texte vert pixelisé).
Il propose des commandes simples, des outils pratiques et même des mini-jeux, sans aucune dépendance externe.
Installation
Option 1 : Avec Python installé
Téléchargez freeos.py.
Vérifiez que Python 3.10+ est installé avec Tkinter (déjà présent sur Windows/macOS, à installer séparément sur certaines distributions Linux).
Lancez FreeOS avec :
python freeos.py
Option 2 : Version prête à l’emploi (Windows)
Téléchargez freeos.exe (si fourni).
Double-cliquez pour lancer FreeOS, sans installation.
Utilisation
Au démarrage, FreeOS affiche un écran d’accueil et attend vos commandes (> prompt).
Tapez une commande et validez avec Entrée.
Exemple :
> help
Commandes principales
Fichiers & navigation
dir ou ls — liste les fichiers/dossiers.
cd <chemin> — change de dossier (cd - pour revenir en arrière).
cds <nom> — crée un dossier.
cfile <nom> — crée un fichier vide.
cfile <nom> - <texte> — crée/édite un fichier avec du texte.
cfile - <texte> — ajoute du texte au dernier fichier utilisé.
play <nom> — ouvre un fichier/dossier via l’application système.
Outils pratiques
calc — calculatrice.
count — compteur cliquable.
color — changer couleurs texte/fond.
time — heure actuelle.
timer — chronomètre.
minuteur hh:mm:ss — compte à rebours avec bips.
cal — calendrier du mois.
date — date du jour.
Aléatoire & sécurité
random wrd — mot aléatoire (650+ disponibles).
random nmbr [min max] — nombre aléatoire.
random dicton — dicton/proverbe aléatoire (200+).
password — générateur de mots de passe et passphrases.
Jeux inclus
game — menu de jeux :
Devine un nombre
Memory 4x4
Pendu
Morpion ASCII (2 joueurs)
Échecs (texte ou graphique)
Divers
msg <texte> — affiche un message.
i — ouvre ma page dans le navigateur.
exitapp — ferme toutes les fenêtres/outils mais garde FreeOS ouvert.
exit — quitte FreeOS.
shutup — dit “ok”, ferme tout et quitte.
Limitations connues
Audio : pas d’enregistrement micro sans bibliothèques externes (fonction désactivée proprement).
Échecs : règles simplifiées (pas de roque, en passant, promotions complexes).
Compatibilité : testé sur Windows et Linux ; sur macOS, certaines fonctions peuvent varier.
Avertissement
FreeOS est un projet expérimental pensé pour le fun et la créativité.
Il n’a pas vocation à remplacer un terminal système complet.