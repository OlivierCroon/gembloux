from flask import Blueprint, render_template, jsonify, request
from datetime import datetime

bp = Blueprint('magasin', __name__)

# Utilisation d'une variable globale pour simuler une base de données persistante
STOCKS = [
    {"code": "MAT-001", "nom": "Ciment", "quantite": 42},
    {"code": "SIG-012", "nom": "Panneau", "quantite": 5},
    {"code": "OUT-045", "nom": "Pelle", "quantite": 12}
]

# Simulation des sorties (historique par code article) avec ajout des quantités
SORTIES = {
    "MAT-001": [
        {"atal": "AT-2026-001", "date": "2026-04-10", "ouvrier": "Jean Dupont", "quantite": 2},
        {"atal": "AT-2026-015", "date": "2026-04-12", "ouvrier": "Marc Vandame", "quantite": 5}
    ],
    "SIG-012": [
        {"atal": "AT-2026-005", "date": "2026-04-11", "ouvrier": "Pierre Martin", "quantite": 1}
    ],
    "OUT-045": []
}


@bp.route('/stocks')
def page_stocks():
    """Affiche la page principale du magasin"""
    return render_template('magasin/stocks.html')


@bp.route('/api/stocks')
def api_stocks():
    """API pour lister les stocks"""
    return jsonify(STOCKS)


@bp.route('/api/sorties/<string:code>')
def api_sorties(code):
    """API pour lister les sorties d'un article spécifique"""
    liste_sorties = SORTIES.get(code, [])
    return jsonify(liste_sorties)


@bp.route('/api/sortie', methods=['POST'])
def api_sortie():
    """Décompte les articles du stock et enregistre la quantité dans l'historique"""
    data = request.get_json()

    if not data or 'materiaux' not in data:
        return jsonify({"status": "error", "message": "Données invalides"}), 400

    atal_note = data.get('atal', 'AT-NON-SPECIFIE')
    ouvrier = data.get('ouvrier', 'Ouvrier inconnu')
    date_jour = datetime.now().strftime("%Y-%m-%d")

    for item_utilise in data['materiaux']:
        nom_art = item_utilise.get('nom', '').lower().strip()
        qty_a_sortir = int(item_utilise.get('quantite', 0))

        for article in STOCKS:
            if nom_art in article['nom'].lower():
                # Diminution du stock en mémoire
                article['quantite'] -= qty_a_sortir

                # Ajout dans l'historique avec la quantité
                code_art = article['code']
                if code_art not in SORTIES:
                    SORTIES[code_art] = []

                SORTIES[code_art].append({
                    "atal": atal_note,
                    "date": date_jour,
                    "ouvrier": ouvrier,
                    "quantite": qty_a_sortir
                })
                break

    return jsonify({"status": "success", "message": "Stock mis à jour et historique enregistré"})


@bp.route('/api/entree', methods=['POST'])
def api_entree():
    """Ajoute une quantité à un article existant ou crée un nouvel article"""
    data = request.get_json()

    if not data or 'code' not in data or 'nom' not in data or 'quantite' not in data:
        return jsonify({"status": "error", "message": "Données incomplètes"}), 400

    code_art = data['code'].strip()
    nom_art = data['nom'].strip()
    qty_a_ajouter = int(data['quantite'])

    # Chercher si l'article existe déjà
    article_trouve = False
    for article in STOCKS:
        if article['code'] == code_art:
            article['quantite'] += qty_a_ajouter
            # On met à jour le nom si jamais il a été corrigé par l'agent
            article['nom'] = nom_art
            article_trouve = True
            break

    # Si c'est un nouvel article, on le crée
    if not article_trouve:
        STOCKS.append({
            "code": code_art,
            "nom": nom_art,
            "quantite": qty_a_ajouter
        })
        # On initialise aussi son historique de sorties (vide pour le moment)
        SORTIES[code_art] = []

    return jsonify({"status": "success", "message": "Entrée en stock enregistrée avec succès"})