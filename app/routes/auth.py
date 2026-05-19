from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

bp = Blueprint('auth', __name__)

# Simulation d'une base de données d'utilisateurs
# Rôles : 'admin', 'contre-maitre', 'ouvrier'
USERS = {
    "admin@hotmail.com": {"password": "1", "role": "admin", "nom": "Administrateur"},
    "cm@hotmail.com": {"password": "2", "role": "contre-maitre", "nom": "Contre-maître"},
    "ouvrier@hotmail.com": {"password": "3", "role": "ouvrier", "nom": "Ouvrier"}
}


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        identifiant = request.form.get('identifiant')
        mot_de_passe = request.form.get('mot_de_passe')

        user = USERS.get(identifiant)
        # Vérification du mot de passe
        if user and user['password'] == mot_de_passe:
            # Enregistrement dans la session Flask
            session['user'] = identifiant
            session['role'] = user['role']
            session['nom'] = user['nom']

            # Redirection en fonction du rôle
            if user['role'] == 'admin':
                return redirect(url_for('auth.admin_dashboard'))
            elif user['role'] == 'contre-maitre':
                # Redirection vers le tableau de bord du contre-maître
                return redirect(url_for('interventions.cm_dashboard'))
            else:
                # Les ouvriers vont directement sur la liste des interventions
                return redirect(url_for('patrimoine.page_index'))
        else:
            error = "Identifiant ou mot de passe incorrect."

    return render_template('auth/login.html', error=error)


@bp.route('/logout')
def logout():
    """Déconnecte l'utilisateur et vide la session"""
    session.clear()
    return redirect(url_for('auth.login'))


@bp.route('/admin')
def admin_dashboard():
    """Page réservée à l'administrateur"""
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('auth/admin.html', users=USERS)


@bp.route('/admin/add', methods=['POST'])
def admin_add_user():
    """Route pour ajouter un utilisateur depuis le panel admin"""
    if session.get('role') != 'admin':
        return jsonify({"error": "Accès refusé"}), 403

    identifiant = request.form.get('identifiant')
    password = request.form.get('password')
    role = request.form.get('role')
    nom = request.form.get('nom')

    if identifiant and password and role and nom:
        if identifiant not in USERS:
            USERS[identifiant] = {"password": password, "role": role, "nom": nom}

    return redirect(url_for('auth.admin_dashboard'))


@bp.route('/admin/delete/<identifiant>', methods=['POST'])
def admin_delete_user(identifiant):
    """Route pour supprimer un utilisateur"""
    if session.get('role') != 'admin':
        return jsonify({"error": "Accès refusé"}), 403

    # On empêche l'admin de se supprimer lui-même
    if identifiant in USERS and identifiant != session.get('user'):
        del USERS[identifiant]

    return redirect(url_for('auth.admin_dashboard'))


@bp.route('/api/ouvriers')
def api_ouvriers():
    """Renvoie la liste des ouvriers pour l'assignation par le contre-maître"""
    ouvriers = [{"identifiant": k, "nom": v["nom"]} for k, v in USERS.items() if v["role"] == "ouvrier"]
    return jsonify(ouvriers)