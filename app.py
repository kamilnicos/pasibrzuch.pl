from flask import Flask, render_template
from routes.auth import auth_bp
from routes.klient import klient_bp
from routes.restauracja import restauracja_bp
from routes.dostawca import dostawca_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Klucz do sesji (wymagane dla Flask)

# Rejestracja blueprintów
app.register_blueprint(auth_bp)
app.register_blueprint(klient_bp, url_prefix='/klient')
app.register_blueprint(restauracja_bp, url_prefix='/restauracja')
app.register_blueprint(dostawca_bp, url_prefix='/dostawca')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
