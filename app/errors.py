from flask import render_template, request
from app import app, db

# Eigenentwicklung
# Implementiert eine Fehlermeldung für den Error Code 403 und gibt die URL zurück, welche die Seite aufgerufen hat
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html', ref=request.referrer), 403 # Quelle: https://stackoverflow.com/questions/28593235/get-referring-url-for-flask-request

# Übernommen
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Übernommen
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
