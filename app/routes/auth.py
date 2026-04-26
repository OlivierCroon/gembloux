from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

bp = Blueprint('auth', __name__)

# Simulation d'une base de données d'utilisateurs
# Rôles : 'admin', 'contre-maitre', 'ouvrier'
USERS = {
    "admin": {"password": "admin", "role": "admin", "nom": "Administrateur Système"},
    "cm1": {"password": "cm1", "role": "contre-maitre", "nom": "Chef de chantier 1"},
    "ouvrier1": {"password": "ouv1", "role": "ouvrier", "nom": "Jean Dupont"},
    "ouvrier2": {"password": "ouv2", "role": "ouvrier", "nom": "Marc Vandame"}
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
                # En attendant de créer le tableau de bord du contre-maître, on renvoie vers l'accueil
                return redirect('/')
            else:
                # Les ouvriers vont directement sur la liste des interventions
                return redirect(url_for('interventions.page_liste'))
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