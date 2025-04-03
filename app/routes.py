from flask import Blueprint, render_template, redirect, url_for, request, make_response, send_file, flash
from app import db
from app.models import Personnel, Decompte, Responsable
from app.forms import DecompteForm, PersonnelForm, ResponsableForm
from datetime import datetime
from sqlalchemy import extract
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.pdfgen import canvas
import io, os, re
from reportlab.lib.utils import simpleSplit
from num2words import num2words
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.colors import yellow, black

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")


# Route pour afficher la liste du personnel
@bp.route("/personnel")
def afficher_personnel():
    # Récupérer la page courante (par défaut 1)
    page = request.args.get('page', 1, type=int)

    # Nombre d'éléments par page
    per_page = 8

    # Récupération paginée des employés
    pagination = Personnel.query.paginate(page=page, per_page=per_page, error_out=False)

    #  DEBUG : Voir si on récupère bien des données
    print("Employés récupérés :", pagination.items)

    return render_template(
        "personnel.html",
        employes=pagination,  # Passer l'objet pagination
        pagination=pagination
    )

#  Route pour ajouter un personnel
@bp.route("/ajouter_personnel", methods=["GET", "POST"])
def ajouter_personnel():
    form = PersonnelForm()
    if form.validate_on_submit():
        employe = Personnel(
            nom=form.nom.data,
            prenom=form.prenom.data,
            classe=form.classe.data,
            poste=form.poste.data,
            sexe=form.sexe.data,
            cout_repas=form.cout_repas.data,
            cout_logement=form.cout_logement.data,
            division_regionale=form.division_regionale.data
        )
        db.session.add(employe)
        db.session.commit()
        return redirect(url_for("main.afficher_personnel"))

    flash("Ajout de personnel effectué avec succès !", "success")
    return render_template("ajouter_personnel.html", form=form)

# Route pour modifier un personnel
@bp.route("/modifier_personnel/<int:personnel_id>", methods=["GET", "POST"])
def modifier_personnel(personnel_id):
    employe = Personnel.query.get_or_404(personnel_id)
    form = PersonnelForm(obj=employe)

    if form.validate_on_submit():
        employe.nom = form.nom.data
        employe.prenom = form.prenom.data
        employe.classe = form.classe.data
        employe.poste = form.poste.data
        employe.sexe = form.sexe.data
        employe.cout_repas = form.cout_repas.data
        employe.cout_logement = form.cout_logement.data
        employe.division_regionale = form.division_regionale.data

        db.session.commit()
        return redirect(url_for("main.afficher_personnel"))

    flash("Modification de personnel effectuée avec succès !", "success")
    return render_template("modifier_personnel.html", form=form, employe=employe)


#  Route pour supprimer un personnel
@bp.route("/supprimer_personnel/<int:personnel_id>", methods=["POST", "GET"])
def supprimer_personnel(personnel_id):
    employe = Personnel.query.get_or_404(personnel_id)
    db.session.delete(employe)
    db.session.commit()

    flash("Personnel supprimé avec succès !", "success")
    return redirect(url_for("main.afficher_personnel"))


# Route pour ajouter un nouveau décompte
@bp.route("/nouveau_decompte", methods=["GET", "POST"])
def nouveau_decompte():
    form = DecompteForm()
    form.personnel.choices = [(p.id, f"{p.nom} {p.prenom}") for p in Personnel.query.all()]

    if form.validate_on_submit():
        personnel = Personnel.query.get(form.personnel.data)

        #  Numéro de l'OM (saisi par l'utilisateur)
        numero_om = form.numero_om.data

        #  Génération automatique du numéro d'ordre
        annee = datetime.now().year % 100  # Ex: 2025 devient 25
        nombre_decomptes = Decompte.query.filter(
            Decompte.date_ordre >= datetime(datetime.now().year, 1, 1)
        ).count()
        numero_ordre = nombre_decomptes + 1  # Ex: 1, 2, 3...

        division = "DK"  # TODO: Récupérer la division dynamiquement
        numero_complet = f"{numero_ordre}/{annee}/CNSS/DCDR/RD-{division}"

        #  Calcul des valeurs
        nombre_jours = (form.date_retour.data - form.date_depart.data).days + 1
        nombre_repas = 2 * nombre_jours - 1
        nombre_nuitees = nombre_jours - 1
        frais_restauration = personnel.cout_repas * nombre_repas
        frais_logement = personnel.cout_logement * nombre_nuitees
        total_paye = frais_restauration + frais_logement

        #  Récupérer les frais supplémentaires
        frais_transport_aller = form.frais_transport_aller.data or 0
        frais_transport_retour = form.frais_transport_retour.data or 0
        frais_peage_aller = form.frais_peage_aller.data or 0
        frais_peage_retour = form.frais_peage_retour.data or 0

        #  Calcul du total final
        total_final = total_paye + frais_transport_aller + frais_transport_retour + frais_peage_aller + frais_peage_retour


        #  Création du décompte
        decompte = Decompte(
            numero_ordre=numero_complet,  # Numéro d'ordre généré automatiquement
            numero_om=numero_om,  # Numéro OM saisi par l'utilisateur
            personnel_id=personnel.id,
            date_ordre=form.date_ordre.data,
            date_depart=form.date_depart.data,
            date_retour=form.date_retour.data,
            nombre_jours=nombre_jours,
            nombre_repas=nombre_repas,
            nombre_nuitees=nombre_nuitees,
            frais_restauration=frais_restauration,
            frais_logement=frais_logement,
            total_paye=total_final,
            frais_transport_aller=frais_transport_aller,
            frais_transport_retour=frais_transport_retour,
            frais_peage_aller=frais_peage_aller,
            frais_peage_retour=frais_peage_retour
        )
        db.session.add(decompte)
        db.session.commit()

        flash("Nouveau décompte créé avec succès !", "success")

        return redirect(url_for("main.afficher_decomptes"))

    return render_template("nouveau_decompte.html", form=form)

@bp.route("/decomptes")
def afficher_decomptes():
    page = request.args.get("page", 1, type=int)  #  Récupérer le numéro de la page (1 par défaut)
    per_page = 5  #  Nombre de décomptes par page

    decomptes = Decompte.query.order_by(Decompte.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("decomptes.html", decomptes=decomptes)

@bp.route("/modifier_decompte/<int:decompte_id>", methods=["GET", "POST"])
def modifier_decompte(decompte_id):
    decompte = Decompte.query.get_or_404(decompte_id)
    form = DecompteForm(obj=decompte)  #  Préremplit le formulaire

    form.personnel.choices = [(p.id, f"{p.nom} {p.prenom}") for p in Personnel.query.all()]

    if form.validate_on_submit():
        decompte.numero_om = form.numero_om.data
        decompte.date_ordre = form.date_ordre.data
        decompte.date_depart = form.date_depart.data
        decompte.date_retour = form.date_retour.data
        decompte.personnel_id = form.personnel.data

        # Recalculer les valeurs
        nombre_jours = (form.date_retour.data - form.date_depart.data).days + 1
        nombre_repas = 2 * nombre_jours - 1
        nombre_nuitees = nombre_jours - 1
        frais_restauration = decompte.personnel.cout_repas * nombre_repas
        frais_logement = decompte.personnel.cout_logement * nombre_nuitees
        total_paye = frais_restauration + frais_logement


        #  Récupérer les frais supplémentaires
        frais_transport_aller = int(form.frais_transport_aller.data or 0)
        frais_transport_retour = int(form.frais_transport_retour.data or 0)
        frais_peage_aller = int(form.frais_peage_aller.data or 0)
        frais_peage_retour = int(form.frais_peage_retour.data or 0)

        #  Calcul du total final
        total_final = total_paye + frais_transport_aller + frais_transport_retour + frais_peage_aller + frais_peage_retour

        decompte.nombre_jours = nombre_jours
        decompte.nombre_repas = nombre_repas
        decompte.nombre_nuitees = nombre_nuitees
        decompte.frais_restauration = frais_restauration
        decompte.frais_logement = frais_logement
        decompte.total_paye = total_final
        decompte.frais_transport_aller=frais_transport_aller
        decompte.frais_transport_retour=frais_transport_retour
        decompte.frais_peage_aller=frais_peage_aller
        decompte.frais_peage_retour=frais_peage_retour

        db.session.commit()
        return redirect(url_for("main.afficher_decomptes"))

    flash("Modificcation de décompte effectuée avec succès !", "success")
    return render_template("modifier_decompte.html", form=form, decompte=decompte)

@bp.route("/supprimer_decompte/<int:decompte_id>", methods=["POST", "GET"])
def supprimer_decompte(decompte_id):
    decompte = Decompte.query.get_or_404(decompte_id)

    db.session.delete(decompte)
    db.session.commit()

    flash("Supression de décompte effectué !", "success")
    return redirect(url_for("main.afficher_decomptes"))

def format_nombre_pdf(value):
    """Formate un nombre avec des espaces pour les milliers"""
    if isinstance(value, (int, float)):
        return f"{int(value):,}".replace(",", " ")  # Convertit en entier et ajoute des espaces
    return value


@bp.route("/decompte/<int:decompte_id>/pdf")
def generer_pdf(decompte_id):
    """ Génère un PDF du décompte de déplacement """
    # Récupération du décompte correspondant à l'identifiant
    decompte = Decompte.query.get_or_404(decompte_id)

    # Chemin du répertoire de génération de PDF
    base_dir = os.path.abspath(os.path.dirname(__file__))
    directory = os.path.join(base_dir, "static", "pdf")
    
    # Nettoyage du nom de fichier
    numero_ordre_sanitized = re.sub(r'[\\/:"*?<>|]+', '_', decompte.numero_ordre)
    filename = f"decompte_{numero_ordre_sanitized}.pdf"
    filepath = os.path.join(directory, filename)

    # Création du répertoire si nécessaire
    if not os.path.exists(directory):
        os.makedirs(directory)

    c = canvas.Canvas(filepath, pagesize=landscape(A4))
    width, height = landscape(A4)

    # **1. Entête**
    # Texte de l'entête
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 50, "CAISSE NATIONALE")
    c.drawString(100, height - 65, "DE")
    c.drawString(50, height - 80, "SECURITE SOCIALE")

    # Dimensions du logo
    logo_width = 90
    logo_height = 90
    logo_x = width - logo_width - 50

    # Calcul de la position Y pour centrer le logo avec les trois lignes
    logo_center_y = (height - 50 + height - 80) / 2 - (logo_height / 2)


    logo_path = os.path.join(base_dir, "static", "logo-CNSS-new.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, logo_x, logo_center_y, width=logo_width, height=logo_height)

    # **2. Titre et sous-titre**
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 120, f"Décompte de déplacement n° {decompte.numero_ordre}")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 135, "Compte n° 63021007")

    # **3. Infos du personnel**
    lieu_dict = {
        "DK": "Kara", 
        "DC": "Tchamba", 
        "DP": "Atakpamé", 
        "DMG": "Lomé", 
        "DML": "Aného", 
        "DS": "Dapaong"
    }
    y_position = height - 165

    division_nom = lieu_dict.get(decompte.personnel.division_regionale, "Lomé")
    civilite = "Monsieur" if decompte.personnel.sexe == "Homme" else "Madame"
    info_personnel = f"Indemnité de déplacement de {civilite} {decompte.personnel.nom} {decompte.personnel.prenom} (classe {decompte.personnel.classe}), {decompte.personnel.poste} à la CNSS {division_nom}."
    info_ordre = f"Déplacement suivant l'ordre de mission {decompte.numero_om} du {decompte.date_ordre.strftime('%d/%m/%Y')}."
    c.drawString(50, y_position, info_personnel)
    c.drawString(50, y_position - 20, info_ordre)

    # **4. Tableau des frais**
    x_start, y_start = 50, height - 205
    colonnes = [
        "Ordre de \nmission n°", "Date de \ndépart", "Date de \nretour", "Nombre de \njours",
        "Nombre de \nrepas", "Coût du \nrepas", "Frais de \nrestauration",
        "Nombre de \nnuitées", "Coût du \nlogement", "Frais de \nlogement", "Total"
    ]
    valeurs = [
        decompte.numero_om,
        decompte.date_depart.strftime('%d/%m/%Y'),
        decompte.date_retour.strftime('%d/%m/%Y'),
        str(decompte.nombre_jours),
        str(decompte.nombre_repas),
        str(format_nombre_pdf(decompte.personnel.cout_repas)),
        str(format_nombre_pdf(decompte.frais_restauration)),
        str(decompte.nombre_nuitees),
        str(format_nombre_pdf(decompte.personnel.cout_logement)),
        str(format_nombre_pdf(decompte.frais_logement)),
        str(format_nombre_pdf(decompte.total_paye))
    ]
    left_margin = 50
    right_margin = 50
    usable_width = width - left_margin - right_margin
    col_width = usable_width / len(colonnes)  # Largeur uniforme pour chaque colonne

    table_data = [colonnes, valeurs]
    table = Table(table_data, colWidths=[col_width] * len(colonnes))


    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
    ]))
    table.wrapOn(c, x_start, y_start)
    table.drawOn(c, x_start, y_start - len(table_data) * 20)

    # **5. Frais supplémentaires**
    frais_supp = [
        ("Frais de transport (Aller)", format_nombre_pdf(decompte.frais_transport_aller)),
        ("Frais de transport (Retour)", format_nombre_pdf(decompte.frais_transport_retour)),
        ("Frais de péage (Aller)", format_nombre_pdf(decompte.frais_peage_aller)),
        ("Frais de péage (Retour)", format_nombre_pdf(decompte.frais_peage_retour))
    ]
    frais_supp = [(libelle, montant) for libelle, montant in frais_supp if montant > 0]
    y = y_start - 60
    for libelle, montant in frais_supp:
        c.drawString(50, y, libelle)
        c.drawRightString(750, y, f"{montant} FCFA")
        y -= 20

    # **6. Total final**
    total_final = decompte.total_paye + sum(montant for _, montant in frais_supp)
    y -= 10
    c.setFont("Helvetica-Bold", 12)
    
    # Coloration du fond en jaune (position x, y, largeur, hauteur)
    c.setFillColor(yellow)  
    c.rect(530, y - 5, 260, 20, fill=True, stroke=False)

    # Remettre le texte en noir et l'écrire sur le fond
    c.setFillColor(black)
    c.drawString(550, y, "TOTAL A PAYER:")
    c.drawRightString(770, y, f"{format_nombre_pdf(total_final)} FCFA")


    # **7. Montant en lettres**
    montant_lettre = num2words(total_final, lang="fr")
    y -= 25
    texte_total = f"Arrêté le présent décompte à la somme de : {montant_lettre} ({format_nombre_pdf(total_final)}) francs CFA."
    c.drawString(50, y, texte_total)

    # **8. Lieu, date, signatures**
    y -= 20
    
    lieu = lieu_dict.get(decompte.personnel.division_regionale, "Lomé")
    date_auj = datetime.today().strftime("%d/%m/%Y")
    c.drawString(600, y, f"Fait à {lieu}, le {date_auj}")

    # **Signatures**
    # Récupérer le CSAF et le RD actifs
    #csaf = Responsable.query.filter_by(fonction="CSAF", division=decompte.personnel.division_regionale, actif=True).first()
    csaf = Responsable.query.filter_by(
        fonction="CSAF", 
        division=decompte.personnel.division_regionale
    ).filter(
        (Responsable.actif == True) | (Responsable.interim == True)  # Récupérer soit l'actif, soit l'intérimaire
    ).first()

    rd = Responsable.query.filter_by(
        fonction="RD", 
        division=decompte.personnel.division_regionale
    ).filter(
        (Responsable.actif == True) | (Responsable.interim == True)  # Récupérer soit l'actif, soit l'intérimaire
    ).first()


    #rd = Responsable.query.filter_by(fonction="RD", division=decompte.personnel.division_regionale, actif=True).first()

    # Gérer l'affichage de l'intérim
    def get_nom_responsable(responsable):
        if responsable and responsable.interim and responsable.interimaire:
            return f"{responsable.interimaire.nom.upper()} {responsable.interimaire.prenom.capitalize()}"
        elif responsable:
            return f"{responsable.nom.upper()} {responsable.prenom.capitalize()}"
        return "_________"

    # Gérer le titre avec "pi" si intérim
    #titre_csaf = "Chef Service Administratif et Financier pi" if csaf and csaf.interim else "Chef Service Administratif et Financier"
    #titre_rd = "Responsable de Division pi" if rd and rd.interim else "Responsable de Division"

    #nom_csaf = get_nom_responsable(csaf)
    #nom_rd = get_nom_responsable(rd)
    if csaf and csaf.interim and csaf.interimaire:
        titre_csaf = "Chef Service Administratif et Financier pi"
        nom_csaf = get_nom_responsable(csaf)
    else:
        titre_csaf = "Chef Service Administratif et Financier"
        nom_csaf = get_nom_responsable(csaf)
    
    if rd and rd.interim and rd.interimaire:
        titre_rd = "Responsable de Division pi"
        nom_rd = get_nom_responsable(rd)
    else:
        titre_rd = "Responsable de Division"
        nom_rd = get_nom_responsable(rd)


    # **Affichage des titres**
    y -= 16
    c.drawString(50, y, titre_csaf)  
    c.drawString(600, y, titre_rd)

    # **Affichage des noms**
    y -= 50
    c.drawString(50, y, nom_csaf)
    c.drawString(600, y, nom_rd)

    # **9. Bénéficiaire**
    y -= 50
    c.drawString(50, y, "Bénéficiaire")
    y -= 20
    c.drawString(50, y, "Pour acquis:")
    y -= 20
    c.drawString(50, y, f"{lieu}, le ________________")

    # Sauvegarde du fichier
    c.save()

    flash("PDF généré avec succès !", "success")
    return send_file(filepath, as_attachment=True)


@bp.route("/responsables")
def afficher_responsables():
    page = request.args.get("page", 1, type=int)  # Récupérer le numéro de page (par défaut: 1)
    responsables_pagination = Responsable.query.order_by(Responsable.nom, Responsable.prenom).paginate(page=page, per_page=10)

    return render_template(
        "responsables.html", 
        responsables = responsables_pagination,
        #pagination = responsables_pagination
    )


from app.models import Responsable

@bp.route("/ajouter_responsable", methods=["GET", "POST"])
def ajouter_responsable():
    form = ResponsableForm()

    # Charger les responsables disponibles pour être intérimaires
    form.interimaire_id.choices = [(0, "Aucun")] + [
        (r.id, f"{r.nom} {r.prenom}") for r in Responsable.query.all()]

    if form.validate_on_submit():
        nouveau_responsable = Responsable(
            nom=form.nom.data.upper(),
            prenom=form.prenom.data.capitalize(),
            fonction=form.fonction.data,
            division=form.division.data,
            actif=form.actif.data,
            interim=form.interim.data,
            interimaire_id=form.interimaire_id.data if form.interim.data else None
        )
        db.session.add(nouveau_responsable)
        db.session.commit()
        flash("Responsable ajouté avec succès", "success")
        return redirect(url_for("main.afficher_responsables"))

    return render_template("ajouter_responsable.html", form=form)


@bp.route('/modifier_responsable/<int:responsable_id>', methods=['GET', 'POST'])
def modifier_responsable(responsable_id):
    responsable = Responsable.query.get_or_404(responsable_id)
    form = ResponsableForm(obj=responsable)


    form.interimaire_id.choices = [("", "Aucun")] + [
        (r.id, f"{r.nom} {r.prenom}") for r in Responsable.query.filter(Responsable.id != responsable.id).all()
    ]

    if form.validate_on_submit():
        responsable.nom = form.nom.data.upper()
        responsable.prenom = form.prenom.data.capitalize()
        responsable.fonction = form.fonction.data
        responsable.division = form.division.data
        responsable.actif = form.actif.data
        responsable.interim = form.interim.data

        #  CHANGEMENT IMPORTANT
        if form.interim.data and form.interimaire_id.data:
            responsable.interimaire_id = form.interimaire_id.data
        else:
            responsable.interimaire_id = None

        db.session.commit()
        flash("Modification effectuée avec succès !", "success")
        return redirect(url_for("main.afficher_responsables"))

    return render_template("modifier_responsable.html", form=form, responsable=responsable)

@bp.route("/supprimer_responsable/<int:responsable_id>", methods=["POST", "GET"])
def supprimer_responsable(responsable_id):
    responsable = Responsable.query.get_or_404(responsable_id)
    db.session.delete(responsable)
    db.session.commit()
    flash("Suppression du responsable effectuée !", "success")
    return redirect(url_for("main.afficher_responsables"))

@bp.route('/responsable/interim/<int:responsable_id>', methods=['POST'])
def activer_interim(responsable_id):
    responsable = Responsable.query.get_or_404(responsable_id)
    responsable.interim = not responsable.interim  # Inversion de l’état

    if responsable.interim:
        interimaire_id = request.form.get("interimaire")  # On récupère l'ID
        if interimaire_id:
            interimaire_obj = Responsable.query.get(int(interimaire_id))  # On cherche l'objet
            if interimaire_obj:
                responsable.interimaire = interimaire_obj  # On assigne l’objet SQLAlchemy
            else:
                flash("L'intérimaire sélectionné n'existe pas.", "danger")
                return redirect(url_for("main.afficher_responsables"))
    else:
        responsable.interimaire = None  # Désactivation de l’intérim

    db.session.commit()
    flash("Mise à jour de l'intérim effectuée !", "success")
    return redirect(url_for("main.afficher_responsables"))
