Je te propose de remplacer les boutons ttk (rectangles plats) par des boutons dessinés sur le canvas, dans le même style que ceux de la page des règles. Ils auront une ombre, un effet de survol (fond plus clair, contour jaune, curseur main) et APODY sera grisé quand il n’y a rien à annuler. Je n’ai pas pu lancer le code, donc teste-le chez toi.

1. Remplacer dessiner_bouton

Cette version sert aussi pour la page des règles, qui profite du survol sans rien changer.

Avant :

python
def dessiner_bouton(tag, texte, x, y, commande):
    id_texte = canvas.create_text(
        x, y, text=texte, font=("Georgia", 16, "bold"), fill="#f3e2b8", tags=tag
    )
    ...
    canvas.tag_bind(tag, "<Button-1>", lambda event: commande())

Après :

python
def dessiner_bouton(tag, texte, x, y, commande, taille=16, actif=True):
    # couleurs selon l'état (grisé si inactif)
    c_texte = "#f3e2b8" if actif else "#8a7a66"
    c_fond = "#3b2415" if actif else "#4a3a2e"
    c_bord = "#c9a24a" if actif else "#7a6a55"
    tags = (tag, "bouton")  # "bouton" sert à ignorer ces clics dans clic_case

    id_texte = canvas.create_text(
        x, y, text=texte, font=("Georgia", taille, "bold"), fill=c_texte, tags=tags
    )
    x1, y1, x2, y2 = canvas.bbox(id_texte)  # taille réelle du texte
    marge_x, marge_y = 25, 10

    # ombre décalée de 3 px vers le bas-droite
    id_ombre = rectangle_arrondi(
        x1 - marge_x + 3, y1 - marge_y + 4, x2 + marge_x + 3, y2 + marge_y + 4,
        14, fill="#1a0d05", outline="", tags=tags,
    )
    id_fond = rectangle_arrondi(
        x1 - marge_x, y1 - marge_y, x2 + marge_x, y2 + marge_y,
        14, fill=c_fond, outline=c_bord, width=2, tags=tags,
    )
    canvas.tag_lower(id_fond, id_texte)   # fond derrière le texte
    canvas.tag_lower(id_ombre, id_fond)   # ombre derrière le fond

    if not actif:
        return  # bouton grisé : ni survol ni clic

    def survol(event):
        canvas.itemconfig(id_fond, fill="#5a3a22", outline="#ffd400")  # plus clair + contour jaune
        canvas.config(cursor="hand2")  # curseur main

    def sortie(event):
        canvas.itemconfig(id_fond, fill="#3b2415", outline="#c9a24a")  # retour à la normale
        canvas.config(cursor="")

    canvas.tag_bind(tag, "<Enter>", survol)
    canvas.tag_bind(tag, "<Leave>", sortie)
    canvas.tag_bind(tag, "<Button-1>", lambda event: commande())
2. Les trois boutons dans dessin_plateau

Avant :

python
    if btn_miverina is not None:
        canvas.create_window(
            marge_x,
            hauteur - 55,
            window=btn_miverina,
            anchor="center",
        )
    if btn_vaovao is not None:
        ...
    if btn_apody is not None:
        ...

Après :

python
    y_boutons = hauteur - 55
    dessiner_bouton("btn_hivoka", "HIVOKA", marge_x, y_boutons, retour_menu, taille=18)
    dessiner_bouton("btn_vaovao", "VAOVAO", largeur / 2, y_boutons, lalao_vaovao, taille=18)
    dessiner_bouton(
        "btn_apody", "APODY", marge_x + plateau_largeur, y_boutons,
        annuler_dernier, taille=18,
        actif=bool(historique),  # grisé tant qu'il n'y a aucun coup à annuler
    )
3. Simplifier lancer

Supprime les boutons ttk et le style, devenus inutiles.

Avant :

python
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Apody.TButton", ...)
    style.map("Apody.TButton", ...)

    btn_apody = ttk.Button(...)
    btn_miverina = ttk.Button(...)
    btn_vaovao = ttk.Button(...)

Après : supprime tout ce bloc. Tu peux aussi enlever btn_apody, btn_miverina, btn_vaovao du global dans lancer.

4. Éviter qu’un clic sur un bouton joue un coup

Sans cela, cliquer sur APODY déclenche aussi clic_case et peut sélectionner un pion.

Avant :

python
def clic_case(event):
    global pion_selectionne
    # intersection

Après :

python
def clic_case(event):
    global pion_selectionne
    if "bouton" in canvas.gettags("current"):  # clic sur un bouton : on ignore
        return
    # intersection

Si tu veux, je peux aussi ajouter un petit symbole (↶ pour APODY, par exemple) ou changer les couleurs pour qu’elles collent à ton plateau.




Claude is AI and can make mistakes. Please double-check responses.