from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

bp = Blueprint('interventions', __name__)

# Simulation de la base de données ATAL avec ajout du champ 'assigne_a'
INTERVENTIONS = [
    {
        "id": 101,
        "note_atal": "AT-2026-089",
        "lieu": "Grand-Manil",
        "adresse": "Rue de la Station 12",
        "contact": "Jean Dupont",
        "telephone": "081/61.12.34",
        "tache": "Réparation Avaloir",
        "statut": "Ouvert",
        "assigne_a": None
    },
    {
        "id": 102,
        "note_atal": "AT-2026-090",
        "lieu": "Centre-Ville",
        "adresse": "Place de la Mairie",
        "contact": "Commune",
        "telephone": "-",
        "tache": "Remplacement panneau signalisation",
        "statut": "Ouvert",
        "assigne_a": "Ouvrier"
    }
]


@bp.route('/')
def page_liste():
    """Vue pour l'ouvrier (liste de ses interventions)"""
    if session.get('role') not in ['ouvrier', 'contre-maitre', 'admin']:
        return redirect(url_for('auth.login'))
    return render_template('interventions/liste.html')


@bp.route('/cm_dashboard')
def cm_dashboard():
    """Tableau de bord exclusif du contre-maître"""
    if session.get('role') not in ['contre-maitre', 'admin']:
        return redirect(url_for('auth.login'))
    return render_template('interventions/cm_dashboard.html')


@bp.route('/nouvelle')
def page_nouvelle():
    """Page pour signaler un nouveau problème depuis le terrain"""
    if session.get('role') not in ['ouvrier', 'contre-maitre', 'admin']:
        return redirect(url_for('auth.login'))
    return render_template('interventions/nouvelle.html')


@bp.route('/signalements')
def page_signalements():
    """Page pour le contre-maître listant les signalements remontés du terrain"""
    if session.get('role') not in ['contre-maitre', 'admin']:
        return redirect(url_for('auth.login'))
    return render_template('interventions/signalements.html')


@bp.route('/api/donnees')
def api_donnees():
    """Renvoie la liste des interventions (filtrée selon le rôle)"""
    role = session.get('role')
    nom_utilisateur = session.get('nom')

    # Si c'est un ouvrier, on ne renvoie que les interventions qui lui sont assignées
    if role == 'ouvrier':
        interventions_filtrees = [inter for inter in INTERVENTIONS if inter.get('assigne_a') == nom_utilisateur]
        return jsonify(interventions_filtrees)

    # Si c'est un admin ou un contre-maître, on renvoie tout
    return jsonify(INTERVENTIONS)


@bp.route('/api/nouvelle', methods=['POST'])
def api_nouvelle():
    """Enregistre un nouveau signalement remonté par un agent"""
    if session.get('role') not in ['ouvrier', 'contre-maitre', 'admin']:
        return jsonify({"status": "error", "message": "Accès refusé"}), 403

    data = request.get_json()

    type_lieu = data.get('type_lieu', 'Autre')
    description = data.get('description', 'Aucune description')

    # Formatage du lieu en fonction du type choisi
    if type_lieu == 'Voirie':
        lat = data.get('lat', '')
        lng = data.get('lng', '')
        lieu_texte = f"Voirie (GPS: {lat}, {lng})" if lat else "Voirie (GPS non fourni)"
    elif type_lieu == 'Bâtiment':
        lieu_texte = f"Bâtiment: {data.get('batiment')} - Étage: {data.get('etage')} - Local: {data.get('local')}"
    else:
        lieu_texte = type_lieu  # Plaine de jeux ou Autre

    nouveau_id = len(INTERVENTIONS) + 101

    nouvelle_inter = {
        "id": nouveau_id,
        "note_atal": f"PROVISOIRE-{nouveau_id}",
        "lieu": lieu_texte,
        "adresse": "À déterminer",
        "contact": session.get('nom'),  # L'agent qui a créé le signalement
        "telephone": "-",
        "tache": description,
        "statut": "Signalement",
        "assigne_a": None
    }

    INTERVENTIONS.append(nouvelle_inter)

    return jsonify({"status": "success", "message": "Signalement envoyé avec succès !"})


@bp.route('/api/assigner/<int:id>', methods=['POST'])
def assigner(id):
    """Permet au contre-maître d'assigner une intervention à un ouvrier"""
    if session.get('role') != 'contre-maitre' and session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Accès refusé"}), 403

    data = request.get_json()
    ouvrier_nom = data.get('ouvrier')

    for inter in INTERVENTIONS:
        if inter['id'] == id:
            inter['assigne_a'] = ouvrier_nom
            return jsonify({"status": "success", "message": f"L'intervention a été assignée à {ouvrier_nom}."})

    return jsonify({"status": "error", "message": "Intervention non trouvée"}), 404


@bp.route('/cloturer/<int:id>', methods=['POST'])
def cloturer(id):
    """Reçoit les données de la Phase 2 et met à jour le statut"""
    donnees = request.get_json()
    for inter in INTERVENTIONS:
        if inter['id'] == id:
            inter['statut'] = 'Clôturé - Transmis ATAL'

    return jsonify({
        "status": "success",
        "message": "Données synchronisées avec ATAL"
    })