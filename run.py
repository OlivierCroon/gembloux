from app import create_app

# Point d'entrée de l'application
app = create_app()

if __name__ == '__main__':
    # Configuration pour l'accès réseau (tablettes/GSM)
    # host='0.0.0.0' permet l'accès depuis n'importe quel appareil du réseau local
    app.run(host='0.0.0.0', port=5030, debug=True)