from app import db

class Personnel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(50), nullable=False)
    poste = db.Column(db.String(100), nullable=False)
    sexe = db.Column(db.String(10), nullable=False)
    cout_repas = db.Column(db.Numeric, nullable=False)
    cout_logement = db.Column(db.Numeric, nullable=False)
    division_regionale = db.Column(db.String(50), nullable=False)


class Decompte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_ordre = db.Column(db.String(50), unique=True, nullable=False)
    numero_om = db.Column(db.String(50), nullable=False)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnel.id'), nullable=False)
    personnel = db.relationship("Personnel", backref="decomptes")  
    date_ordre = db.Column(db.Date, nullable=False)
    date_depart = db.Column(db.Date, nullable=False)
    date_retour = db.Column(db.Date, nullable=False)
    nombre_jours = db.Column(db.Integer, nullable=False)
    nombre_repas = db.Column(db.Integer, nullable=False)
    nombre_nuitees = db.Column(db.Integer, nullable=False)
    frais_restauration = db.Column(db.Numeric, nullable=False)
    frais_logement = db.Column(db.Numeric, nullable=False)
    total_paye = db.Column(db.Numeric, nullable=False)

    # Ajout des frais supplémentaires
    frais_transport_aller = db.Column(db.Numeric, nullable=True, default=0)
    frais_transport_retour = db.Column(db.Numeric, nullable=True, default=0)
    frais_peage_aller = db.Column(db.Numeric, nullable=True, default=0)  
    frais_peage_retour = db.Column(db.Numeric, nullable=True, default=0) 

class Responsable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    fonction = db.Column(db.String(50), nullable=False)
    division = db.Column(db.String(50), nullable=False)
    actif = db.Column(db.Boolean, default=True)
    interim = db.Column(db.Boolean, default=False)

    interimaire_id = db.Column(db.Integer, db.ForeignKey('responsable.id'), nullable=True)  
    interimaire = db.relationship('Responsable', remote_side=[id], backref="interim_responsables")

