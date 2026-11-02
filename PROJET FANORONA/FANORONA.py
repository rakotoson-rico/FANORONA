import random
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

lignes_plateau = 5
colonnes_plateu = 9
# droite gauche bas haut
directions_droites = [(1, 0), (-1, 0), (0, 1), (0, -1)]
directions_diagonales = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

# hasina nu etat
# var global
plateau = []  # noir blanc vide
tour = "blanc"
pion_selectionne = None  # fidiny joueur
positions_visitees = []  # hankanany ny hipodianany

derniere_direction = None
choix_capture = None

historique = []

# mode solo
mode_jeu = "2players"
couleur_ia = "noir"
proofondeur_ia = 3  # niveau

# var interface
root = None
canvas = None
positions = []
rayon_pions = 25  # hicalculena anz isikin miova dimension
image_fond = None
image_fond_originale = None
image_case = None  # rafa mandeh game
image_case_jeu = None
image_plateau_originale = None
image_plateau = None
taille_plateau = None
image_jeu_originale = None
image_jeu = None  # la PhotoImage doit rester en global, sinon Tkinter l'efface
taille_image_jeu = None


page_regle = 0


def dessin_pion(canvas, x, y, rayon, couleur, selectionne=False):
    canvas.create_oval(
        x - rayon + 4,  # gauche ombre
        y - rayon + 5,  # sup
        x + rayon + 4,  # droite
        y + rayon + 5,  # inf
        fill="#3b2518",
        outline="",  # maka ny comptours ombre
    )

    if couleur == "noir":  # verification
        couleur_pion = "#171717"
        couleur_reflet = "#555555"
    else:
        couleur_pion = "#f4efd9"
        couleur_reflet = "#ffffff"
    # mijery n position alany
    if selectionne:
        contour = "#ffcc00"  # contour jaune
        epaisseur_contour = 3
    else:
        contour = "#1e1e1e"
        epaisseur_contour = 2

    # cercle principal des pions
    canvas.create_oval(
        x - rayon,  # gauche pions
        y - rayon,  # superieur
        x + rayon,  # droite
        y + rayon,  # inferieur
        fill=couleur_pion,
        outline=contour,
        width=epaisseur_contour,
    )
    canvas.create_oval(
        x - rayon * 0.45,
        y - rayon * 0.50,
        x + rayon * 0.05,
        y + rayon * 0.10,
        fill=couleur_reflet,
        outline="",  # reflet en haut à gauche
    )


def position(case):
    return positions[case[1]][case[0]]


def clic_case(event):
    global pion_selectionne
    # si on clique sur un bouton, on ne joue pas de coup
    if "bouton" in canvas.gettags("current"):
        return
    # intersection
    meilleure_case = None
    meilleure_distance = float("inf")  # initialisation à l'infini
    for ligne in range(lignes_plateau):
        for colonne in range(colonnes_plateu):
            x, y = positions[ligne][colonne]
            distance = (event.x - x) ** 2 + (event.y - y) ** 2
            if distance < meilleure_distance:
                meilleure_case = (colonne, ligne)
                meilleure_distance = distance
    if pion_selectionne is None:
        if meilleure_case in pions_selectionnables():
            pion_selectionne = meilleure_case
    else:
        resultat = mpilalao(meilleure_case)
        if resultat == "choix":
            approche = messagebox.askyesno(
                "Safidy ny fanamborana",
                "Samborina aminèny fantonana ?\n\nOui : manantona\nNon : mihemotra",
            )
            resultat = mifidy_maty("approche" if approche else "retrait")
        if resultat in ("blanc", "noir"):
            messagebox.showinfo("Tapitra", f"Ny loko {resultat} no nandresy !")

    dessin_plateau()
    if mode_jeu == "1player" and tour == couleur_ia:
        root.after(450, jouer_ia_aleatoire)


def dessin_plateau(event=None):
    global positions, rayon_pions, image_plateau, taille_plateau
    canvas.delete("all")

    largeur = canvas.winfo_width()
    hauteur = canvas.winfo_height()

    # CORRIGÉ : si le canvas n'a pas encore de taille, on sort tout de suite
    if largeur <= 1 or hauteur <= 1:
        return

    ratio = max(
        largeur / image_plateau_originale.width,
        hauteur / image_plateau_originale.height,
    )
    taille_vaovao = (
        int(image_plateau_originale.width * ratio),
        int(image_plateau_originale.height * ratio),
    )

    if taille_vaovao != taille_plateau:
        image = image_plateau_originale.resize(taille_vaovao, Image.Resampling.LANCZOS)
        image_plateau = ImageTk.PhotoImage(image)
        taille_plateau = taille_vaovao
    canvas.create_image(
        largeur / 2,
        hauteur / 2,
        image=image_plateau,
        tags="fond_plateau",
    )

    marge_x = largeur * 0.17
    marge_y = hauteur * 0.19

    plateau_largeur = largeur - 2 * marge_x
    plateau_hauteur = hauteur - 2 * marge_y

    canvas.create_rectangle(
        marge_x - 55,
        marge_y - 55,
        marge_x + plateau_largeur + 55,
        marge_y + plateau_hauteur + 55,
        fill="",
        outline="#482817",
        width=4,
    )
    if tour == "noir":
        texte_tour = "An'ireo mainty izao ! "
        couleur_tour = "black"
    else:
        texte_tour = "An'ireo fotsy izao ! "
        couleur_tour = "white"

    canvas.create_text(
        largeur / 2,
        32,
        text=texte_tour,
        fill=couleur_tour,
        anchor="n",
        font=("Arial", 38, "bold"),
    )

    positions = []

    for ligne in range(lignes_plateau):
        ligne_positions = []
        for col in range(colonnes_plateu):
            x = marge_x + col * plateau_largeur / (colonnes_plateu - 1)
            y = marge_y + ligne * plateau_hauteur / (lignes_plateau - 1)
            ligne_positions.append((x, y))
        positions.append(ligne_positions)

    # horizontale
    for ligne in range(lignes_plateau):
        for col in range(colonnes_plateu - 1):
            x1, y1 = position((col, ligne))
            x2, y2 = position((col + 1, ligne))
            canvas.create_line(x1, y1, x2, y2, fill="#3a2a1a", width=1)

    # verticale
    for col in range(colonnes_plateu):
        for ligne in range(lignes_plateau - 1):
            x1, y1 = position((col, ligne))
            x2, y2 = position((col, ligne + 1))
            canvas.create_line(x1, y1, x2, y2, fill="#3a2a1a", width=1)

    # diagonale
    for ligne in range(lignes_plateau - 1):
        for col in range(colonnes_plateu - 1):
            if (col + ligne) % 2 == 0:
                x1, y1 = position((col, ligne))
                x2, y2 = position((col + 1, ligne + 1))
                canvas.create_line(x1, y1, x2, y2, fill="#3a2a1a", width=1)

                x1, y1 = position((col + 1, ligne))
                x2, y2 = position((col, ligne + 1))
                canvas.create_line(x1, y1, x2, y2, fill="#3A2A1A", width=1)

    rayon_pions = min(plateau_largeur / 36, plateau_hauteur / 15)

    # Indique les cases où le pion sélectionné peut se déplacer.
    if pion_selectionne is not None:
        for colonne, ligne in lalana_fidina():
            x, y = position((colonne, ligne))
            canvas.create_oval(
                x - 7, y - 7, x + 7, y + 7, fill="#ffd400", outline="#ffffff", width=1
            )

    # Dessine tous les pions présents dans la grille.
    for ligne in range(lignes_plateau):
        for colonne in range(colonnes_plateu):
            couleur = plateau[ligne][colonne]
            if couleur is not None:
                x, y = position((colonne, ligne))
                dessin_pion(
                    canvas,
                    x,
                    y,
                    rayon_pions,
                    couleur,
                    (colonne, ligne) == pion_selectionne,
                )

    y_boutons = hauteur - 55  # hauteur commune aux 3 boutons

    dessiner_bouton("btn_hivoka", "HIVOKA", marge_x, y_boutons, retour_menu, 18)
    dessiner_bouton("btn_vaovao", "VAOVAO", largeur / 2, y_boutons, lalao_vaovao, 18)

    # APODY : actif seulement s'il y a un coup à annuler
    if len(historique) > 0:
        dessiner_bouton(
            "btn_apody",
            "APODY",
            marge_x + plateau_largeur,
            y_boutons,
            annuler_dernier,
            18,
            True,
        )
    else:
        dessiner_bouton(
            "btn_apody",
            "APODY",
            marge_x + plateau_largeur,
            y_boutons,
            annuler_dernier,
            18,
            False,
        )


def retour_menu():
    confirmation = messagebox.askyesno(
        "Miverina any amin'ny menu",
        "Tena hialana ve ny lalao?\nHo very ny lalao eo am-pandehanana.",
    )
    if confirmation:
        menu()


def lalao_vaovao():
    confirmation = messagebox.askyesno(
        "Lalao vaovao",
        "Haverina avy amin'ny voaloany ?\nHo very ny lalao eo am-pandehanana.",
    )
    if confirmation:
        nouvelle_partie()
        dessin_plateau()


def lancer():
    for widget in root.winfo_children():
        widget.destroy()
    global canvas
    global image_plateau_originale, taille_plateau
    image_plateau_originale = Image.open("grille.jpg")
    taille_plateau = None

    canvas = tk.Canvas(root, bg="#8b522f", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    canvas.bind("<Configure>", dessin_plateau)
    canvas.bind("<Button-1>", clic_case)

    nouvelle_partie()
    dessin_plateau()


def splash():
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="black")
    label = tk.Label(
        root,
        text="KILALAO MALAGASY :)",
        font=("Arial", 40, "bold"),
        fg="white",
        bg="black",
    )
    label.place(relx=0.5, rely=0.5, anchor="center")
    root.after(2000, menu)


def menu():
    for widget in root.winfo_children():
        widget.destroy()
    global canvas, image_fond_originale
    image_fond_originale = Image.open("menu.png")
    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    couleur_texte = "#4a2d1b"
    boutons = (
        ("boutton1", " P I L A L A O   I R A Y", 0.36),
        ("boutton2", "P I L A L A O   R O A ", 0.46),
        ("boutton3", "F O M B A F I L A L A O V A N A", 0.54),
        ("boutton_quitter", "A K A T O N A ", 0.64),
    )
    for tag, texte, position_y in boutons:
        couleur_bouton = "#c0392b" if tag == "boutton_quitter" else couleur_texte
        canvas.create_text(
            0, 0, text=texte, font=("Arial", 25, "bold"), fill=couleur_bouton, tags=tag
        )
    canvas.create_text(
        0, 0, text="◆", font=("Arial", 18), fill="#9b5d3d", tags="separateur2"
    )
    canvas.create_text(
        0, 0, text="◆", font=("Arial", 18), fill="#9b5d3d", tags="separateur2"
    )
    canvas.create_text(
        0, 0, text="◆", font=("Arial", 18), fill="#9b5d3d", tags="separateur3"
    )

    def redimensionner_menu(event=None):
        largeur = max(canvas.winfo_width(), 1)
        hauteur = max(canvas.winfo_height(), 1)
        ratio = max(
            largeur / image_fond_originale.width, hauteur / image_fond_originale.height
        )
        image = image_fond_originale.resize(
            (
                int(image_fond_originale.width * ratio),
                int(image_fond_originale.height * ratio),
            ),
            Image.Resampling.LANCZOS,
        )
        global image_fond
        image_fond = ImageTk.PhotoImage(image)
        canvas.delete("fond")
        canvas.create_image(largeur / 2, hauteur / 2, image=image_fond, tags="fond")
        canvas.tag_lower("fond")

        for tag, _, position_y in boutons:
            canvas.coords(tag, largeur / 2, hauteur * position_y)
        canvas.coords("separateur1", largeur / 2, hauteur * 0.49)
        canvas.coords("separateur2", largeur / 2, hauteur * 0.59)
        canvas.coords("separateur3", largeur / 2, hauteur * 0.49)

    def demarrer_mode(mode):
        global mode_jeu
        mode_jeu = mode
        lancer()

    canvas.bind("<Configure>", redimensionner_menu)
    canvas.tag_bind("boutton1", "<Button-1>", lambda event: demarrer_mode("1player"))
    canvas.tag_bind("boutton2", "<Button-1>", lambda event: demarrer_mode("2players"))
    canvas.tag_bind("boutton3", "<Button-1>", lambda event: comment_jouer())
    canvas.tag_bind("boutton_quitter", "<Button-1>", lambda event: root.quit())


# LOGIQUE__________________________________________________


# fomba filalaova _____________
def schema():
    return min(
        canvas.winfo_width() * 0.05, canvas.winfo_height() * 0.075
    )  # 5% LARGEUR ET 7.5% HAUTEUR


def schema_ligne(cx, cy, cases, pas, rayon, marque=None):
    # ligne de points avec des pions
    n = len(cases)
    x0 = cx - (n - 1) * pas / 2
    canvas.create_line(x0, cy, x0 + (n - 1) * pas, cy, fill="#3a2a1a", width=2)
    for i in range(n):
        x = x0 + i * pas
        canvas.create_oval(x - 5, cy - 5, x + 5, cy + 5, fill="#3a2a1a", outline="")
        if cases[i] is not None:
            dessin_pion(canvas, x, cy, rayon, cases[i], i == marque)


def schema_depart(cx, cy):
    # mini plateau
    pas = schema()
    x0 = cx - 4 * pas
    y0 = cy - 2 * pas

    for ligne in range(5):
        canvas.create_line(
            x0,
            y0 + ligne * pas,
            x0 + 8 * pas,
            y0 + ligne * pas,
            fill="#3a2a1a",
            width=1,
        )
    for col in range(9):
        canvas.create_line(
            x0 + col * pas, y0, x0 + col * pas, y0 + 4 * pas, fill="#3a2a1a", width=1
        )
    for ligne in range(4):
        for col in range(8):
            if (col + ligne) % 2 == 0:
                canvas.create_line(
                    x0 + col * pas,
                    y0 + ligne * pas,
                    x0 + (col + 1) * pas,
                    y0 + (ligne + 1) * pas,
                    fill="#3a2a1a",
                    width=1,
                )
                canvas.create_line(
                    x0 + (col + 1) * pas,
                    y0 + ligne * pas,
                    x0 + col * pas,
                    y0 + (ligne + 1) * pas,
                    fill="#3a2a1a",
                    width=1,
                )
    couleurs = ["noir", "noir", None, "blanc", "blanc"]
    for ligne in range(5):
        for col in range(9):
            if couleurs[ligne] is not None:
                dessin_pion(
                    canvas,
                    x0 + col * pas,
                    y0 + ligne * pas,
                    pas * 0.32,
                    couleurs[ligne],
                )


def schema_mini_grille(cx, cy, pas, diagonales):
    for i in range(3):
        # horizontales
        canvas.create_line(
            cx - pas,
            cy + (i - 1) * pas,
            cx + pas,
            cy + (i - 1) * pas,
            fill="#3a2a1a",
            width=2,
        )
        # verticales (CORRIGÉ : cy au lieu de cx)
        canvas.create_line(
            cx + (i - 1) * pas,
            cy - pas,
            cx + (i - 1) * pas,
            cy + pas,
            fill="#3a2a1a",
            width=2,
        )
    if diagonales:
        canvas.create_line(cx - pas, cy - pas, cx + pas, cy + pas, fill="#3a2a1a")
        canvas.create_line(cx - pas, cy + pas, cx + pas, cy - pas, fill="#3a2a1a")

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            if dx != 0 and dy != 0 and not diagonales:
                continue
            x = cx + dx * pas
            y = cy + dy * pas  # CORRIGÉ : cy au lieu de cx
            canvas.create_oval(
                x - 9, y - 9, x + 9, y + 9, fill="#ffd400", outline="#ffffff"
            )
    dessin_pion(canvas, cx, cy, pas * 0.32, "blanc")


def schema_mouvement(cx, cy):
    pas = schema()
    schema_mini_grille(cx - 2.5 * pas, cy, pas, True)  # 8 directions
    schema_mini_grille(cx + 2.5 * pas, cy, pas, False)  # 4 directions
    canvas.create_text(
        cx - 2.5 * pas,
        cy + 1.8 * pas,
        text="Teboka misy tsikika miampy : lalana 8",
        font=("Georgia", 14, "bold"),  # CORRIGÉ : "Gerogia"
        fill="#7a3b1d",
    )
    canvas.create_text(
        cx + 2.5 * pas,
        cy + 1.8 * pas,
        text="Teboka hafa : lalana 4",
        font=("Georgia", 14, "bold"),  # CORRIGÉ : "Georgie"
        fill="#7a3b1d",
    )


def schema_capture(cx, cy):
    pas = schema()
    rayon = pas * 0.32
    gauche = cx - 3 * pas
    droite = cx + 3 * pas

    canvas.create_text(
        gauche,
        cy - 2 * pas,
        text="FANATONA",
        font=("Georgia", 16, "bold"),
        fill="#7a3b1d",
    )
    canvas.create_text(
        droite,
        cy - 2 * pas,
        text="FIHEMORANA",
        font=("Georgia", 16, "bold"),
        fill="#7a3b1d",
    )

    # approche
    schema_ligne(
        gauche, cy - pas, ["blanc", None, "noir", "noir", None], pas, rayon, marque=0
    )
    canvas.create_text(gauche, cy, text="▼", font=("Arial", 16), fill="#a5502b")
    schema_ligne(
        gauche, cy + pas, [None, "blanc", None, None, None], pas, rayon, marque=1
    )

    # retrait
    schema_ligne(
        droite, cy - pas, ["noir", "noir", "blanc", None, None], pas, rayon, marque=2
    )
    canvas.create_text(droite, cy, text="▼", font=("Arial", 16), fill="#a5502b")
    schema_ligne(
        droite, cy + pas, [None, None, None, "blanc", None], pas, rayon, marque=3
    )


# ___contenu

regle = [
    (
        "1 . NY TANJONA",
        "Samy manana vato 18 ny mpilalo roa , ary mifandimby mihetsika. \n\n"
        "Tanjona : mamono ny vato rehetran'ny mpifaninana aminao."
        "Izay lany vato no resy. ",
        schema_depart,
    ),
    (
        "2 . NY",
        "Isaky ny handefa dia mandehana any amin'ny toerana malalaka , izany hoe mbola tsy misy vato."
        "Fa kosa mifanila aminy , maraka ny tsipika.\n"
        "Ny sasany amin 'ny teboka dia manana tsipika miampita ka afaka mihetsika amin'ny lalana 8.",
        schema_mouvement,
    ),
    (
        "3 . FOMBA FAMONOANA",  # CORRIGÉ : virgule ajoutée
        "Raha mitovy ny tsipika misy anao sy ny mpifanianan aminao , ka mihetsika ianao dia mamono ianao zay \n"
        "FANANTONANA : mandroso amin'ny vato, mamono ny mifanitsy rehetra eo aloha. \n"
        "FIHEMORANA : mihemotra miala ny vato , mamono ny vato mifanesy afaranao. \n"
        "Raha samby izy roa dia mifidy ianao .",
        schema_capture,
    ),
    (
        "4. FISTIPIKA",
        "• Raha misy azo vonoina dia tsy maintsy vonoina .\n\n"
        "• Raha misy vato iaray avy mamono ka mbola misy hafa afaka vonoin'io vato io dia mbola mandeha io vato io ary mamono izay eo izay.\n\n"
        "• Tsy mahazo miverina ny toerana efa nodiaviny tamin'io fihetsehana io ilay vato. \n\n"
        "• Tsy mahazo manao lalana mitovy misesy. \n\n"
        "MIARARY ANTSIKA HANKAFY NY FIALAMBOLY NAPETRAKAN' IREO RAZANTSIKA ;)",
        None,
    ),
]


def rectangle_arrondi(x1, y1, x2, y2, rayon, **options):
    # Polygone dont les coins sont lissés par smooth=True
    points = [
        x1 + rayon, y1,
        x2 - rayon, y1,
        x2, y1,
        x2, y1 + rayon,
        x2, y2 - rayon,
        x2, y2,
        x2 - rayon, y2,
        x1 + rayon, y2,
        x1, y2,
        x1, y2 - rayon,
        x1, y1 + rayon,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **options)


def bouton_survol(tag):
    # appelée quand la souris entre dans le bouton
    canvas.itemconfig(tag + "_fond", fill="#5a3a22", outline="#ffd400")  # fond plus clair, contour jaune
    canvas.config(cursor="hand2")  # curseur en forme de main


def bouton_sortie(tag):
    # appelée quand la souris quitte le bouton
    canvas.itemconfig(tag + "_fond", fill="#3b2415", outline="#c9a24a")  # couleurs normales
    canvas.config(cursor="")  # curseur normal


def dessiner_bouton(tag, texte, x, y, commande, taille=16, actif=True):
    # couleurs : normales si actif, grisées sinon
    if actif:
        c_texte = "#f3e2b8"
        c_fond = "#3b2415"
        c_bord = "#c9a24a"
    else:
        c_texte = "#8a7a66"
        c_fond = "#4a3a2e"
        c_bord = "#7a6a55"

    # le texte du bouton
    id_texte = canvas.create_text(
        x,
        y,
        text=texte,
        font=("Georgia", taille, "bold"),
        fill=c_texte,
        tags=(tag, "bouton"),  # "bouton" sert à ignorer ces clics dans clic_case
    )
    x1, y1, x2, y2 = canvas.bbox(id_texte)  # rectangle qui entoure le texte

    # l'ombre : même rectangle décalé de 3 px à droite et 4 px en bas
    id_ombre = rectangle_arrondi(
        x1 - 22,
        y1 - 6,
        x2 + 28,
        y2 + 14,
        14,
        fill="#1a0d05",
        outline="",
        tags=(tag, "bouton"),
    )
    # le fond du bouton (son tag sert au survol)
    id_fond = rectangle_arrondi(
        x1 - 25,
        y1 - 10,
        x2 + 25,
        y2 + 10,
        14,
        fill=c_fond,
        outline=c_bord,
        width=2,
        tags=(tag, tag + "_fond", "bouton"),
    )

    canvas.tag_lower(id_fond, id_texte)  # le fond passe derrière le texte
    canvas.tag_lower(id_ombre, id_fond)  # l'ombre passe derrière le fond

    # survol et clic seulement si le bouton est actif
    if actif:
        canvas.tag_bind(tag, "<Enter>", lambda event: bouton_survol(tag))
        canvas.tag_bind(tag, "<Leave>", lambda event: bouton_sortie(tag))
        canvas.tag_bind(tag, "<Button-1>", lambda event: commande())


def dessiner_regle(event=None):
    global image_jeu, taille_image_jeu
    canvas.delete("all")
    largeur = max(canvas.winfo_width(), 1)
    hauteur = max(canvas.winfo_height(), 1)

    # Image de fond, agrandie pour couvrir toute la fenêtre
    ratio = max(
        largeur / image_jeu_originale.width,
        hauteur / image_jeu_originale.height,
    )
    nouvelle_taille = (
        int(image_jeu_originale.width * ratio),
        int(image_jeu_originale.height * ratio),
    )
    if nouvelle_taille != taille_image_jeu:  # redimensionne seulement si la taille change
        image = image_jeu_originale.resize(nouvelle_taille, Image.Resampling.LANCZOS)
        image_jeu = ImageTk.PhotoImage(image)
        taille_image_jeu = nouvelle_taille
    canvas.create_image(largeur / 2, hauteur / 2, image=image_jeu)

    titre, texte, schema1 = regle[page_regle]
    id_titre = canvas.create_text(
        largeur / 2,
        hauteur * 0.09,
        text="FOMBA FILALAOVANA",
        font=("Georgia", 34, "bold"),
        fill="#f3e2b8",
    )
    x1, y1, x2, y2 = canvas.bbox(id_titre)
    id_plaque = rectangle_arrondi(
        x1 - 40,
        y1 - 10,
        x2 + 40,
        y2 + 10,
        18,
        fill="#3b2415",
        outline="#c9a24a",
        width=3,
    )
    canvas.tag_lower(id_plaque, id_titre)

    largeur_texte = min(largeur * 0.7, 820)  # jamais plus de 820px

    canvas.create_text(
        largeur / 2,
        hauteur * 0.20,
        text=titre,
        font=("Georgia", 28, "bold"),
        fill="#7a3b1d",
    )

    if schema1 is None:
        canvas.create_text(
            largeur / 2,
            hauteur * 0.52,
            text=texte,
            anchor="center",
            font=("Georgia", 18),
            fill="#3b2415",
            width=largeur_texte,
            justify="left",
        )
    else:
        canvas.create_text(
            largeur / 2,
            hauteur * 0.27,
            text=texte,
            anchor="n",
            font=("Georgia", 17),
            fill="#3b2415",
            width=largeur_texte,
            justify="center",
        )
        schema1(largeur / 2, hauteur * 0.65)

    for i in range(len(regle)):
        x = largeur / 2 + (i - (len(regle) - 1) / 2) * 28  # CORRIGÉ : parenthèses
        y = hauteur * 0.845
        if i == page_regle:
            canvas.create_oval(
                x - 7, y - 7, x + 7, y + 7, fill="#7a3b1d", outline="#c9a24a", width=2
            )
        else:
            canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="#b08d57", outline="")

    if page_regle == 0:
        texte_gauche = "HIVOKA"
    else:
        texte_gauche = "MIVERINA"
    # CORRIGÉ : texte_droite est défini dans tous les cas
    if page_regle == len(regle) - 1:
        texte_droite = "TAPITRA"
    else:
        texte_droite = "MANARAKA"
    y_boutons = hauteur * 0.91

    dessiner_bouton(
        "regle_gauche", texte_gauche, largeur / 2 - 220, y_boutons, page_precedente
    )
    dessiner_bouton(
        "regle_droite", texte_droite, largeur / 2 + 220, y_boutons, page_suivante
    )


def page_suivante():
    global page_regle
    if page_regle < len(regle) - 1:
        page_regle += 1
        dessiner_regle()
    else:
        menu()


def page_precedente():
    global page_regle
    if page_regle > 0:
        page_regle -= 1
        dessiner_regle()
    else:
        menu()


def comment_jouer():
    # CORRIGÉ : indentation, le canvas n'est créé qu'une seule fois
    global canvas, image_jeu_originale, taille_image_jeu, page_regle
    for widget in root.winfo_children():
        widget.destroy()
    canvas = tk.Canvas(root, bg="#2b1a0e", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    image_jeu_originale = Image.open("fomba_filalaovana.png")
    taille_image_jeu = None
    page_regle = 0
    canvas.bind("<Configure>", dessiner_regle)


def sauvegarder_etat():
    copie_plateau = [ligne[:] for ligne in plateau]
    etat = {
        "plateau": copie_plateau,
        "tour": tour,
        "pion_selectionne": pion_selectionne,
        "positions_visitees": positions_visitees[:],
        "derniere_direction": derniere_direction,
        "choix_capture": choix_capture,
    }
    historique.append(etat)


def annuler_dernier():
    global plateau, tour, pion_selectionne, positions_visitees
    global derniere_direction, choix_capture
    if not historique:
        messagebox.showinfo("AZAFADY", "TSY MISY AVERINA INTSONY.")
        return
    dernier_etat = historique.pop()
    plateau = dernier_etat["plateau"]
    tour = dernier_etat["tour"]
    pion_selectionne = dernier_etat["pion_selectionne"]
    positions_visitees = dernier_etat["positions_visitees"]
    derniere_direction = dernier_etat["derniere_direction"]
    choix_capture = dernier_etat["choix_capture"]
    dessin_plateau()


def nouvelle_partie():
    global plateau, tour, pion_selectionne, positions_visitees
    global derniere_direction, choix_capture, historique
    plateau = []
    plateau.append(["noir"] * colonnes_plateu)
    plateau.append(["noir"] * colonnes_plateu)
    plateau.append([None] * colonnes_plateu)
    plateau.append(["blanc"] * colonnes_plateu)
    plateau.append(["blanc"] * colonnes_plateu)

    tour = "blanc"
    pion_selectionne = None
    positions_visitees = []
    derniere_direction = None
    choix_capture = None
    historique = []


def adversaire(couleur):
    if couleur == "noir":
        return "blanc"
    else:
        return "noir"


def dans_plateau(case):
    colonne, ligne = case
    return 0 <= colonne < colonnes_plateu and 0 <= ligne < lignes_plateau


def pions(case):
    colonne, ligne = case
    return plateau[ligne][colonne]


def ajouter(case, direction):
    return (case[0] + direction[0], case[1] + direction[1])


def directions(case):
    colonne, ligne = case
    if (colonne + ligne) % 2 == 0:
        return directions_droites + directions_diagonales
    else:
        return directions_droites


def captures_possibles(depart, direction):
    arrivee = ajouter(depart, direction)
    captures = []
    if not dans_plateau(arrivee) or pions(arrivee) is not None:
        return captures

    devant = ajouter(arrivee, direction)
    if dans_plateau(devant) and pions(devant) == adversaire(tour):
        captures.append("approche")

    direction_inverse = (-direction[0], -direction[1])
    derriere = ajouter(depart, direction_inverse)
    if dans_plateau(derriere) and pions(derriere) == adversaire(tour):
        captures.append("retrait")

    return captures


def destination(depart):
    coups = {}
    if pions(depart) != tour:
        return coups

    for direction in directions(depart):
        arrivee = ajouter(depart, direction)
        if not dans_plateau(arrivee) or pions(arrivee) is not None:
            continue
        if arrivee in positions_visitees:
            continue
        if direction == derniere_direction:
            continue
        coups[arrivee] = captures_possibles(depart, direction)
    return coups


# raha tena tsy maintsy laina
def capture_obligatoire():
    for ligne in range(lignes_plateau):
        for colonne in range(colonnes_plateu):
            for capture in destination((colonne, ligne)).values():
                if capture:
                    return True
    return False


def pions_selectionnables():
    if pion_selectionne is not None:
        return {pion_selectionne}
    selectionnables = set()
    doit_capturer = capture_obligatoire()

    for ligne in range(lignes_plateau):
        for colonne in range(colonnes_plateu):
            coups = destination((colonne, ligne))
            if not coups:
                continue
            if not doit_capturer or any(coups.values()):
                selectionnables.add((colonne, ligne))
    return selectionnables


# choix
def lalana_fidina():
    if pion_selectionne is None:
        return {}
    coups = destination(pion_selectionne)
    if positions_visitees:
        return {case: caps for case, caps in coups.items() if caps}
    if capture_obligatoire():
        return {case: caps for case, caps in coups.items() if caps}
    else:
        return coups


def deplacement_pions(depart, arriver):
    colonne_depart, ligne_depart = depart
    colonne_arriver, ligne_arriver = arriver
    plateau[ligne_arriver][colonne_arriver] = plateau[ligne_depart][colonne_depart]
    plateau[ligne_depart][colonne_depart] = None


def eliminer_pions(depart, arriver, direction, capture):
    deplacement_pions(depart, arriver)
    if capture == "approche":
        case = ajouter(arriver, direction)
        pas = direction
    else:
        pas = (-direction[0], -direction[1])
        case = ajouter(depart, pas)
    while dans_plateau(case) and pions(case) == adversaire(tour):
        colonne, ligne = case
        plateau[ligne][colonne] = None
        case = ajouter(case, pas)


def mandresy():
    noirs = 0
    blancs = 0
    for ligne in plateau:
        for piece in ligne:
            if piece == "noir":
                noirs += 1
            elif piece == "blanc":
                blancs += 1
    if noirs == 0:
        return "blanc"
    elif blancs == 0:
        return "noir"
    return None


def fin_tour():
    global tour, pion_selectionne, positions_visitees, derniere_direction
    resultat = mandresy()
    pion_selectionne = None
    positions_visitees = []
    derniere_direction = None
    tour = adversaire(tour)
    return resultat or "tour"


def mpilalao(arriver, capture=None):
    global pion_selectionne, positions_visitees, derniere_direction, choix_capture
    if pion_selectionne is None:
        return "igniore"
    coups = lalana_fidina()
    if arriver not in coups:
        return "igniore"
    depart = pion_selectionne
    direction = (arriver[0] - depart[0], arriver[1] - depart[1])
    capture_list = coups[arriver]
    if len(capture_list) == 2 and capture is None:
        choix_capture = (arriver, direction)
        return "choix"

    sauvegarder_etat()

    if capture_list:
        # CORRIGÉ : on utilise le choix du joueur (capture), sinon la seule option
        eliminer_pions(depart, arriver, direction, capture or capture_list[0])
        positions_visitees.append(arriver)
        derniere_direction = direction
        pion_selectionne = arriver
        if lalana_fidina():
            return "continuer"
    else:
        deplacement_pions(depart, arriver)
    return fin_tour()


def mifidy_maty(capture):
    global choix_capture
    if choix_capture is None:
        return "igniore"
    arriver, direction = choix_capture
    choix_capture = None
    return mpilalao(arriver, capture)


# jeu solo
def jouer_ia_aleatoire():
    global pion_selectionne
    if mode_jeu != "1player" or tour != couleur_ia:
        return

    while tour == couleur_ia:
        pions_jouables = list(pions_selectionnables())
        if not pions_jouables:
            break

        pion_selectionne = random.choice(pions_jouables)
        coups = lalana_fidina()
        if not coups:
            pion_selectionne = None
            break

        arriver = random.choice(list(coups))
        captures = coups[arriver]
        if len(captures) == 2:
            resultat = mpilalao(arriver, random.choice(captures))
        else:
            resultat = mpilalao(arriver)

        if resultat != "continuer":
            break

    dessin_plateau()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("FANORONA 18 ")
    root.state("zoomed")
    root.configure(bg="#8b522f")
    splash()
    root.mainloop()
