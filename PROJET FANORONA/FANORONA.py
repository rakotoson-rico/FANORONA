import random
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

lignes_plateau = 5
colonnes_plateu = 9
# droie gauche bas haut
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
btn_apody = None  # nampiana : ny objet button APODY, tsy azo avadika isaky ny redessin
btn_miverina = None
btn_vaovao = None


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
        contour = "#ffcc00"  # mak acontour jaune
        epaisseur_contour = 3
    else:
        contour = "#1e1e1e"
        epaisseur_contour = 2

    # cercle plincipale des pions
    canvas.create_oval(
        x - rayon,  # gauche pions
        y - rayon,  # superieur
        x + rayon,  # droite
        y + rayon,  # inferieur
        fill=couleur_pion,  # hakany ny tokony aklainy
        outline=contour,
        width=epaisseur_contour,  # epaisseur du contour
    )  # mamita anazy
    canvas.create_oval(
        x - rayon * 0.45,  # gauche
        y - rayon * 0.50,  # d
        x + rayon * 0.05,
        y + rayon * 0.10,  # inferieurtr
        fill=couleur_reflet,
        outline="",  # hazhoany sisiny a gauche ambony kely egny
    )


def position(case):
    return positions[case[1]][case[0]]


def clic_case(event):
    global pion_selectionne
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
    global positions, rayon_pions
    canvas.delete("all")

    largeur = canvas.winfo_width()
    hauteur = canvas.winfo_height()

    # nampiana : nampitomboina ny marge mba hampikelezana ny plateau (0.11->0.17 sy 0.13->0.19)
    marge_x = largeur * 0.17
    marge_y = hauteur * 0.19

    plateau_largeur = largeur - 2 * marge_x
    plateau_hauteur = hauteur - 2 * marge_y

    canvas.create_rectangle(
        marge_x - 55,  # br gauche fond
        marge_y - 55,  # br sup
        marge_x + plateau_largeur + 55,  # bord droite du fond
        marge_y + plateau_hauteur + 55,  # inferieur
        fill="#b87542",
        outline="#482817",
        width=4,
    )
    if tour == "noir":
        texte_tour = "An'ireo mainty izao ! "
        couleur_tour = (
            "black"  # nampiana : rehefa an'ny mainty ny tour, mainty ny soratra
        )
    else:
        texte_tour = "An'ireo fotsy izao ! "
        couleur_tour = (
            "white"  # nampiana : rehefa an'ny fotsy ny tour, fotsy ny soratra
        )

    canvas.create_text(
        largeur / 2,
        32,
        text=texte_tour,
        fill=couleur_tour,
        anchor="n",  #milieu e droite 
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

    # verticale (corrigé)
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

    if btn_miverina is not None:
        canvas.create_window(
            marge_x,  # eo ankavia indrindra hoan'ny MIVERINA
            hauteur - 55,  # 30 pixel eo ambony ny bord ambany
            window=btn_miverina,
            anchor="center",
        )
    if btn_vaovao is not None:
        canvas.create_window(
            largeur / 2,  # eo afo-vy (centre) hoan'ny VAOVAO
            hauteur - 55,
            window=btn_vaovao,
            anchor="center",
        )
    if btn_apody is not None:
        canvas.create_window(
            marge_y + plateau_largeur + 135,  # eo ankavanana indrindra hoan'ny APODY
            hauteur - 55,  # 30 pixel eo ambony ny bord ambany
            window=btn_apody,
            anchor="center",
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
        nouvelle_partie()  # mamerina ny plateau sy ny etat rehetra amin'ny fiandohana
        dessin_plateau()


def lancer():
    for widget in root.winfo_children():
        widget.destroy()
    global canvas, btn_apody, btn_miverina, btn_vaovao
    canvas = tk.Canvas(root, bg="#8b522f", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    style = ttk.Style()
    style.configure("Apody.TButton", font=("Times New Roman", 12, "bold"))
    btn_apody = ttk.Button(
        canvas, text="APODY", style="Apody.TButton", command=annuler_dernier
    )
    btn_miverina = ttk.Button(
        canvas, text="HIVOKA", style="Apody.TButton", command=retour_menu
    )

    btn_vaovao = ttk.Button(
        canvas, text="VAOVAO", style="Apody.TButton", command=lalao_vaovao
    )
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Apody.TButton",
        font=("Arial", 16, "bold"),background="#8b522f",foreground="#3b1f0a",borderwidth=2,
        relief="solid",
        bordercolor ="#3b2415",
        focusthickness =0,
        focuscolor ="#8b522f",
        padding =6,
    )
    style.map(
        "Apody.TButton",
        background=[("active", "#8b522f"), ("pressed", "#8b522f")],
        foreground=[("active", "#2a1506"), ("pressed", "#2a1506")],
    )

    canvas.bind("<Configure>", dessin_plateau)
    canvas.bind("<Button-1>", clic_case)

    nouvelle_partie()
    dessin_plateau()


def splash():
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="black")  # corrigé "bllack" → "black"
    label = tk.Label(
        root,
        text="KILALAO MALAGASY :)",
        font=("Arial", 40, "bold"),
        fg="white",
        bg="black",
    )  # corrigé "blod"
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
        # nampiana : ny boutton_quitter (HIALA) dia mena, ny hafa dia mijanona amin'ny couleur_texte mahazatra
        couleur_bouton = "#c0392b" if tag == "boutton_quitter" else couleur_texte
        canvas.create_text(
            0, 0, text=texte, font=("Arial", 20, "bold"), fill=couleur_bouton, tags=tag
        )
    canvas.create_text(
        0, 0, text="◆", font=("Arial", 12), fill="#9b5d3d", tags="separateur1"
    )
    canvas.create_text(
        0, 0, text="◆", font=("Arial", 12), fill="#9b5d3d", tags="separateur2"
    )
    canvas.create_text(
        0, 0, text="◆", font=("Arial", 12), fill="#9b5d3d", tags="separateur2"
    )
    canvas.create_text(
        0, 0, text="◆", font=("Arial", 12), fill="#9b5d3d", tags="separateur3"
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


def comment_jouer():
    for widget in root.winfo_children():
        widget.destroy()
    global canvas, image_fond_originale
    image_fond_originale = Image.open("menu2.png")
    canvas = tk.Canvas(root, bg="#ecdfc8", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    couleur_texte = "#3b2415"  # brun fonce, comme le titre FANORONA
    couleur_accent = "#a5502b"  # terracotta, comme le "18"

    regle_jeu = (
        "FOMBA FILALAOVANA\n\n"
        "Ny fanorona dia mitana toerana miavaka sy lehibe amin'ny maha malagasy ,izy io mantsy ny fialamboly ny Ntaolo fahiny ary mbola tohizana ankehitriny fa mety hoe hiova ny endriny"
        "Ho jerena manokana eto moa izany dia ny fanorona 18, ny mampiavaka azy dia ny fomba filalaovana azy sy ny endriny (ahitana 5x9 tsipika)\n "
        "Ahoana ara ny fomba filalaovana azy ? \n"
        "Samby manana vato mihisa 18 ny mpilalao ary mifandimbidimby ny handefasa azy\n"
        "Afaka mihetsika amin'ny ze malalaka ny vato rehetra \n"
        "Raha misy tokony vonoina dia tsimaintsy vonoina \n"
        "Ny fomba famonona dia tsotra, izay vato mifanitsy amin'ny ahetsikanao dia maty raha mihemotra ianao n amandroso\n"
        "Mirary fazotona hoanao hilalao ny fialambolin drazantsika  :)"
    )

    canvas.create_text(
        0,
        0,
        text=regle_jeu,
        font=("Georgia", 14),
        fill=couleur_texte,
        width=650,
        justify="left",
        tags="regle_jeu",
    )

    # boutton retour
    canvas.create_rectangle(
        0, 0, 0, 0, fill=couleur_texte, outline="", tags="fond_retour"
    )
    canvas.create_text(
        0,
        0,
        text=" MIVERINA ",
        font=("Georgia", 14, "bold"),
        fill=couleur_accent,
        anchor="w",
        tags="bouton_retour",
    )

    def redimension(event=None):
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

        # texte descendu, sous le titre / la ligne decorative de l'image
        canvas.coords("regle_jeu", largeur / 2, hauteur * 0.68)

        # boutton retour, en bas a gauche maintenant
        canvas.coords("bouton_retour", 30, hauteur - 30)
        canvas.coords("fond_retour", 10, hauteur - 48, 160, hauteur - 12)
        canvas.tag_raise("bouton_retour")

    canvas.bind("<Configure>", redimension)
    canvas.tag_bind("bouton_retour", "<Button-1>", lambda event: menu())
    canvas.tag_bind("fond_retour", "<Button-1>", lambda event: menu())


def sauvegarder_etat():
    global \
        historique, \
        plateau, \
        tour, \
        pion_selectionne, \
        positions_visitees, \
        derniere_direction, \
        choix_capture
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
    global \
        historique, \
        plateau, \
        tour, \
        pion_selectionne, \
        positions_visitees, \
        derniere_direction, \
        choix_capture
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
    # vide
    plateau.append([None] * colonnes_plateu)
    plateau.append(["blanc"] * colonnes_plateu)
    plateau.append(["blanc"] * colonnes_plateu)

    tour = "blanc"
    pion_selectionne = None
    positions_visitees = []
    derniere_direction = None
    choix_capture = None
    historique = []  # nampiana : mamafa ny historique isaky ny manomboka lalao vaovao


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


# ahoan rehfa tena tsmaintsy laina
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
            if piece == "noir":  # corrigé : enlevé l'espace
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
        eliminer_pions(depart, arriver, direction, capture_list or capture_list[0])
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


# jour solo
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


if True:
    root = tk.Tk()
    root.title("FANORONA 18 ")
    root.state("zoomed")
    root.configure(bg="#8b522f")
    splash()
    root.mainloop()
