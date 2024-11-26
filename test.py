import os
import smtplib
from flask import Flask, render_template, request
from flask_mailman import Mail, EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from flask_sqlalchemy import SQLAlchemy

# Scopes nécessaires pour envoyer des emails via Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Configuration Flask
app = Flask(__name__)

# Configuration de la base de données SQLite avec SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'  # Fichier de la base de données SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Désactiver les modifications inutiles
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'votre_email@gmail.com'  # Remplacez par votre email
app.config['MAIL_PASSWORD'] = None  # Pas besoin de mot de passe avec OAuth2
app.config['DEFAULT_FROM_EMAIL'] = 'votre_email@gmail.com'

mail = Mail(app)
db = SQLAlchemy(app)

# Modèle pour enregistrer les emails envoyés dans la base de données
class SentEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<SentEmail {self.subject}>'

# Fonction pour obtenir le jeton d'accès OAuth2
def get_access_token():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        # Si aucun jeton existe, démarrer l'authentification OAuth2
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Enregistrer le jeton pour les futurs appels
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds.token

# Classe pour l'authentification OAuth2 dans SMTP
class OAuth2SMTP(smtplib.SMTP):
    def __init__(self, *args, **kwargs):
        self.access_token = kwargs.pop('access_token', None)
        super().__init__(*args, **kwargs)

    def login(self, user, password=None):
        if self.access_token:
            self.ehlo()
            self.starttls()
            self.ehlo()
            auth_string = f"user={user}\1auth=Bearer {self.access_token}\1\1"
            self.docmd('AUTH', 'XOAUTH2 ' + auth_string.encode('ascii').decode())
        else:
            super().login(user, password)

# Route pour envoyer un email et l'enregistrer dans la base de données
@app.route('/send-email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        recipient = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']

        access_token = get_access_token()  # Obtenez le jeton d'accès
        try:
            # Utilisation de OAuth2 pour l'authentification SMTP
            with OAuth2SMTP(
                app.config['MAIL_SERVER'],
                app.config['MAIL_PORT'],
                access_token=access_token
            ) as smtp:
                email = EmailMessage(
                    subject=subject,
                    body=body,
                    to=[recipient],
                )
                smtp.sendmail(
                    app.config['MAIL_USERNAME'],
                    email.to,
                    email.message().as_string()
                )

            # Enregistrer l'email dans la base de données
            sent_email = SentEmail(
                recipient=recipient,
                subject=subject,
                body=body
            )
            db.session.add(sent_email)
            db.session.commit()

            return "Email envoyé avec succès et enregistré dans la base de données !"
        except Exception as e:
            return f"Erreur lors de l'envoi de l'email : {e}"

    return render_template('send_email.html')

# Route pour afficher tous les emails envoyés
@app.route('/sent-emails')
def sent_emails():
    emails = SentEmail.query.all()  # Récupère tous les emails envoyés
    return render_template('sent_emails.html', emails=emails)

if __name__ == '__main__':
    db.create_all()  # Crée la base de données si elle n'existe pas encore
    app.run(debug=True)
