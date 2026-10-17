 1. Variables globales (en haut du fichier)

Avant :

python
image_case = None #rafa mandeh game 
image_case_jeu = None

Après (ajoute 3 lignes en dessous) :

python
image_case = None #rafa mandeh game 
image_case_jeu = None
image_plateau_originale = None  # image PIL chargée UNE seule fois (évite de relire le fichier à chaque redessin)
image_plateau = None            # PhotoImage tkinter : doit rester en global, sinon Python la supprime et l'image disparaît
taille_plateau_cache = None     # dernière taille utilisée : on ne redimensionne que si la fenêtre a changé
2. Dans lancer() : charger l’image

Avant :

python
    global canvas, btn_apody, btn_miverina, btn_vaovao
    canvas = tk.Canvas(root, bg="#8b522f", highlightthickness=0)

Après :

python
    global canvas, btn_apody, btn_miverina, btn_vaovao
    global image_plateau_originale, taille_plateau_cache  # on va les modifier ici
    image_plateau_originale = Image.open("plateau.png")   # charge l'image de fond (mets ton fichier dans le même dossier que le .py)
    taille_plateau_cache = None                           # force un premier redimensionnement
    canvas = tk.Canvas(root, bg="#8b522f", highlightthickness=0)
3. Dans dessin_plateau() : dessiner l’image en premier

Avant :

python
def dessin_plateau(event=None):
    global positions, rayon_pions
    canvas.delete("all")

    largeur = canvas.winfo_width()
    hauteur = canvas.winfo_height()

Après :

python
def dessin_plateau(event=None):
    global positions, rayon_pions, image_plateau, taille_plateau_cache
    canvas.delete("all")                      # efface tout le canvas (image comprise, on la redessine juste après)

    largeur = canvas.winfo_width()            # largeur actuelle de la fenêtre
    hauteur = canvas.winfo_height()           # hauteur actuelle de la fenêtre

    if largeur > 1 and hauteur > 1:           # évite une division/redimension invalide au tout début (fenêtre pas encore affichée)
        # ratio "cover" : l'image remplit tout l'écran sans déformation (comme dans ton menu)
        ratio = max(
            largeur / image_plateau_originale.width,
            hauteur / image_plateau_originale.height,
        )
        nouvelle_taille = (
            int(image_plateau_originale.width * ratio),   # nouvelle largeur de l'image
            int(image_plateau_originale.height * ratio),  # nouvelle hauteur de l'image
        )
        if nouvelle_taille != taille_plateau_cache:       # on redimensionne seulement si la taille a changé (LANCZOS est lent)
            image = image_plateau_originale.resize(nouvelle_taille, Image.Resampling.LANCZOS)  # redimensionne avec bonne qualité
            image_plateau = ImageTk.PhotoImage(image)     # convertit en image utilisable par tkinter
            taille_plateau_cache = nouvelle_taille        # mémorise la taille pour la prochaine fois
        # place l'image au centre du canvas ; dessinée EN PREMIER donc tout le reste passe au-dessus
        canvas.create_image(largeur / 2, hauteur / 2, image=image_plateau, tags="fond_plateau")
4. Le rectangle marron qui cache l’image

Ton rectangle 
#b87542 est plein : il recouvrirait l’image au milieu. Enlève le remplissage.

Avant :

python
        fill="#b87542",
        outline="#482817",
        width=4,

Après :

python
        fill="",            # "" = transparent : on voit l'image à travers le rectangle
        outline="#482817",  # on garde seulement le contour du plateau
        width=4,

(Si tu veux supprimer aussi le contour, enlève simplement tout le canvas.create_rectangle(...).)

Pourquoi ça marche
Dans un Canvas tkinter, l’ordre de création = l’ordre d’empilement : le premier objet créé est en bas, le dernier en haut.
L’image est créée en premier, puis viennent le rectangle, les lignes, les points jaunes, les pions et enfin les boutons : tout est donc au-dessus de l’image.
image_plateau en global est indispensable : si c’était une variable locale, tkinter perdrait la référence et l’image deviendrait blanche.
À vérifier
Le fichier plateau.png doit être dans le même dossier que ton script (comme menu.png).
Si l’image est trop claire, les lignes 
#3a2a1a seront peu visibles : tu peux alors passer leur width de 1 à 2.





Ton écran noir vient d’une erreur Python dans dessin_plateau(). Elle plante avant que le plateau soit dessiné, donc le canvas reste vide. Regarde ta console : tu devrais y voir UnboundLocalError. Il y a 4 erreurs dans le bloc de l’image.

Les 4 erreurs
global incomplet : image_plateau et taille_plateau ne sont pas déclarées globales, donc Python les prend pour des variables locales et plante.
nouvelle_partie != taille_plateau : tu compares une fonction à une taille. Il faut comparer taille_vaovao.
int(image_plateau_originale.width*ratio) est écrit deux fois : la 2ᵉ doit utiliser .height, sinon l’image est déformée.
Mauvaise indentation : le if du redimensionnement et le create_image sont en dehors du if largeur>1. Si la fenêtre n’est pas encore affichée, taille_vaovao n’existe pas.
Correction

Avant :

python
def dessin_plateau(event=None):
    global positions, rayon_pions
    canvas.delete("all")

    largeur = canvas.winfo_width()
    hauteur = canvas.winfo_height()

    if largeur>1 and hauteur >1:
        ratio = max(largeur/image_plateau_originale.width,hauteur/image_plateau_originale.height)
        taille_vaovao = (
            int(image_plateau_originale.width*ratio),
            int(image_plateau_originale.width*ratio),
        )

    if nouvelle_partie != taille_plateau:
        image = image_plateau_originale.resize(taille_vaovao,Image.Resampling.LANCZOS)
        image_plateau = ImageTk.PhotoImage(image)
        taille_plateau = taille_vaovao 
    canvas.create_image(largeur/2,hauteur/2,image=image_plateau,tags ="fond_plateau " )

Après :

python
def dessin_plateau(event=None):
    global positions, rayon_pions, image_plateau, taille_plateau  # erreur 1 : on ajoute les 2 variables globales
    canvas.delete("all")  # efface tout le canvas avant de redessiner

    largeur = canvas.winfo_width()   # largeur actuelle du canvas
    hauteur = canvas.winfo_height()  # hauteur actuelle du canvas

    if largeur > 1 and hauteur > 1:  # évite de dessiner quand la fenêtre n'est pas encore affichée
        # ratio "cover" : l'image remplit tout l'écran sans se déformer
        ratio = max(
            largeur / image_plateau_originale.width,
            hauteur / image_plateau_originale.height,
        )
        taille_vaovao = (
            int(image_plateau_originale.width * ratio),   # nouvelle largeur
            int(image_plateau_originale.height * ratio),  # erreur 3 : .height ici, pas .width
        )

        if taille_vaovao != taille_plateau:  # erreur 2 : on compare deux tailles, pas une fonction
            # on redimensionne seulement si la taille a changé (LANCZOS est lent)
            image = image_plateau_originale.resize(taille_vaovao, Image.Resampling.LANCZOS)
            image_plateau = ImageTk.PhotoImage(image)  # doit rester global sinon l'image disparaît
            taille_plateau = taille_vaovao             # mémorise la taille utilisée

        # erreur 4 : indenté dans le if, l'image est dessinée EN PREMIER donc tout le reste passe au-dessus
        canvas.create_image(
            largeur / 2, hauteur / 2,   # centre du canvas
            image=image_plateau,
            tags="fond_plateau",        # j'ai retiré l'espace parasite à la fin du tag
        )

Le reste de ta fonction (marge_x = largeur * 0.17, etc.) ne change pas.

Si l’écran est encore noir après ça
Vérifie que grille.png est bien dans le même dossier que ton script. Sinon tu auras FileNotFoundError dans la console.
Ouvre grille.png : si l’image elle-même est noire ou a un fond noir/transparent, c’est elle qui s’affiche.
Si une autre erreur apparaît dans la console, copie-la ici et je regarde.