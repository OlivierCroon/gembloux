from flask import Flask, render_template, redirect, url_for, session


def create_app():
    app = Flask(__name__)

    # Configuration (Clé secrète, Database URI, etc.)
    app.config['SECRET_KEY'] = 'gembloux_secret_key_1234'
    # Permet d'afficher correctement les accents (é, è, etc.) dans les réponses JSON
    app.json.ensure_ascii = False

    # Importation et enregistrement des Blueprints (Modules)
    from app.routes.interventions import bp as interventions_bp
    from app.routes.patrimoine import bp as patrimoine_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.magasin import bp as magasin_bp

    app.register_blueprint(interventions_bp, url_prefix='/interventions')
    app.register_blueprint(patrimoine_bp, url_prefix='/patrimoine')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(magasin_bp, url_prefix='/magasin')

    # Route par défaut : on vérifie la session avant de rendre l'accueil
    @app.route('/')
    def index():
        # Si l'utilisateur n'est pas connecté (pas de rôle en session), on le redirige vers le login
        if not session.get('role'):
            return redirect(url_for('auth.login'))
        return render_template('index.html')

    return app