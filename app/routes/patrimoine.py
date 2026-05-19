from flask import Blueprint, render_template, jsonify

bp = Blueprint('patrimoine', __name__)

@bp.route('/')
def index():
    """Affiche l'interface de scan"""
    return render_template('patrimoine/scanner.html')

@bp.route('/scan/<string:qr_code>')
def obtenir_item(qr_code):
    """Affiche la fiche technique d'un objet scanné"""
    # Simulation d'une recherche dans la base de données
    item_info = {
        "code": qr_code,
        "type": "Mobilier urbain",
        "dernier_entretien": "2025-10-12",
        "etat": "Bon",
        "localisation": "Place de l'Hôtel de Ville"
    }
    return render_template('patrimoine/fiche.html', item=item_info)