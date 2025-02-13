from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Optional
from app.models import Responsable

class DecompteForm(FlaskForm):
    numero_om = StringField("Numéro de l'ordre de mission", validators=[DataRequired()])
    date_ordre = DateField("Date de l'ordre de mission", validators=[DataRequired()])
    date_depart = DateField("Date de départ", validators=[DataRequired()])
    date_retour = DateField("Date de retour", validators=[DataRequired()])
    personnel = SelectField("Personnel", coerce=int)

    #  Champs pour les frais supplémentaires
    frais_transport_aller = DecimalField("Frais de transport (Aller)", validators=[Optional()], default=0)
    frais_transport_retour = DecimalField("Frais de transport (Retour)", validators=[Optional()], default=0)
    frais_peage_aller = DecimalField("Frais de péage (Aller)", validators=[Optional()], default=0)  
    frais_peage_retour = DecimalField("Frais de péage (Retour)", validators=[Optional()], default=0)  

    submit = SubmitField("Enregistrer")

class PersonnelForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired()])
    prenom = StringField("Prénom", validators=[DataRequired()])
    classe = StringField("Classe", validators=[DataRequired()])
    poste = StringField("Poste", validators=[DataRequired()])
    sexe = SelectField("Sexe", choices=[("Homme", "Homme"), ("Femme", "Femme")], validators=[DataRequired()])
    cout_repas = DecimalField("Coût Repas", validators=[DataRequired()])
    cout_logement = DecimalField("Coût Logement", validators=[DataRequired()])
    division_regionale = SelectField("Division Régionale", choices=[
        ("DK", "Kara"),
        ("DC", "Tchamba"),
        ("DP", "Atakpamé"),
        ("DMG", "Lomé"),
        ("DML", "Aného"),
        ("DS", "Dapaong")
    ], validators=[DataRequired()])
    submit = SubmitField("Enregistrer")

class ResponsableForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired()])
    prenom = StringField("Prénom", validators=[DataRequired()])
    fonction = SelectField("Fonction", choices=[
        ("CSAF", "CSAF"), ("RD", "RD")
    ], validators=[DataRequired()])
    division = SelectField("Division", choices=[
        ("DK", "Kara"), ("DC", "Tchamba"), ("DP", "Atakpamé"),
        ("DMG", "Lomé"), ("DML", "Aného"), ("DS", "Dapaong")
    ], validators=[DataRequired()])
    actif = BooleanField("Actif ?")
    interim = BooleanField("En intérim ?")

    def coerce_interimaire(value):
        if isinstance(value, int):  # Si c'est déjà un entier, on le garde
            return value
        return int(value) if value and str(value).isdigit() else None


    interimaire_id = SelectField(
        "Choisir l'intérimaire",
        coerce=coerce_interimaire,  #  On gère `None` proprement
        choices=[]  # Rempli dynamiquement
    )

    submit = SubmitField("Enregistrer")
