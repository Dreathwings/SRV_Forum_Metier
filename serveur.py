from flask import Flask, abort, redirect, render_template, request, session, url_for,jsonify
import mariadb
app = Flask('forum-metier',static_url_path='/forum-metier/static/')
app.secret_key='CECIESTLACLEFSECRETDEGEII'
app.config.update(TEMPLATES_AUTO_RELOAD=True)

def connect_to_DB_forum_metier():
    try:
        DB = mariadb.connect(host="localhost",
                            port=3306,
                            user="warren",
                            password="EPKdVcgcaBYh2l*b",
                            database="forum-metier",
                            autocommit=True)
        DB.autocommit = True
        return DB
    except mariadb.Error as e:
        raise Exception(f"Error connecting to the database: {e}")
    
def connect_to_DB_cas():
    try:
        DB = mariadb.connect(host="localhost",
                            port=3306,
                            user="warren",
                            password="EPKdVcgcaBYh2l*b",
                            database="db_cas",
                            autocommit=True)
        DB.autocommit = True
        return DB
    except mariadb.Error as e:
        raise Exception(f"Error connecting to the database: {e}")
    

@app.errorhandler(403)
def access_denied(e):
    # note that we set the 403 status explicitly
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 403 status explicitly
    return render_template('404.html'), 404

@app.route("/forum-metier",methods=['GET'])
def form():
    return render_template('form.html')

@app.route("/forum-metier/validate", methods=['POST'])
def validate():
    print(request.form)
    data = request.form
    DB = connect_to_DB_forum_metier()
    cur = DB.cursor()
    cur.execute("INSERT INTO `forum-metier`.DATA(ent_nom,ent_adresse,ent_cp,ent_ville,ent_desc,parcours,nb_p,p1_nom,p1_prenom,p1_email,p1_poste,p1_dej,p2_nom,p2_prenom,p2_email,p2_poste,p2_dej,p3_nom,p3_prenom,p3_email,p3_poste,p3_dej) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                ,(data.get("entreprise_nom",None),
                  data.get("entreprise_adresse",None),
                  data.get("code_postal",None),
                  data.get("ville",None),
                  data.get("entreprise_description",None),
                  ",".join(request.form.getlist("parcours_but")),
                  data.get("nb_personnes",None),
                  data.get("participants[1][nom]",None),
                  data.get("participants[1][prenom]",None),
                  data.get("participants[1][email]",None),
                  data.get("participants[1][poste]",None),
                  data.get("participants[1][dej_vendredi]",None),
                  data.get("participants[2][nom]",None),
                  data.get("participants[2][prenom]",None),
                  data.get("participants[2][email]",None),
                  data.get("participants[2][poste]",None),
                  data.get("participants[2][dej_vendredi]",None),
                  data.get("participants[3][nom]",None),
                  data.get("participants[3][prenom]",None),
                  data.get("participants[3][email]",None),
                  data.get("participants[3][poste]",None),
                  data.get("participants[3][dej_vendredi]",None),))
    
    return render_template('validation.html')

# Running the API
if __name__ == "__main__":
    with app.app_context():
        app.run(port=6970,debug=True)

