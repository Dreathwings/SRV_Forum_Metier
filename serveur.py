from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    session,
    send_file,
    send_from_directory,
    url_for,
    jsonify,
)
import flask
import mariadb
import zipfile
from io import BytesIO
from uuid import uuid4
from pathlib import Path
import xml.etree.ElementTree as ET
import requests as REQ
from generate_badges import badge_basename, extract_participants, render_badge_svg
app = Flask('geii/forum-metier')
app.secret_key='CECIESTLACLEFSECRETDEGEII'
app.config.update(TEMPLATES_AUTO_RELOAD=True)
oauth_user = dict()

admin_user = {"wprivat":"ADMIN",
              "ltheolie":"ADMIN",
              "deldescombe":"ADMIN",}
### Activate CAS oauth ###
@app.route("/forum-metier/static/<path:filename>")
@app.route("/geii/forum-metier/static/<path:filename>")
def forum_metier_static(filename):
    """Serve static assets for legacy deployment prefixes."""
    print("ressources ",app.static_folder)
    return send_from_directory(app.static_folder, filename)

CAS = True
@app.route("/forum-metier/oauth")
def oauth():
    if 'ticket' in request.values:
        PARAMS = {"ticket":request.values['ticket'],
                  'service':f"https://www.iut.u-bordeaux.fr/geii/forum-metier/oauth"}
        
        

        RESP = REQ.get(url = "https://cas.u-bordeaux.fr/cas/serviceValidate",params=PARAMS)
        if "authenticationSuccess" in str(RESP.content):
            id = str(RESP.content).split('cas:user')[1].removeprefix('>').removesuffix("</")

            DB = connect_to_DB_forum_metier()
            
            cur = DB.cursor()
            cur.execute(f"SELECT CAS_ID FROM ADMIN WHERE CAS_ID = '{id}' ")
            try:
                login = str(cur.fetchone()[0])
            except:
                return abort(403)
            ##print(f" {DB.user} | Login {data}")

            if login != None: # Verif si user autorised sinon 403 list(cur.execute("SELECT ID FROM "))
                if id in oauth_user.items(): #Verif si user deja un SESSID
                    key = {i for i in oauth_user if oauth_user[i]==id}
                    oauth_user.pop(key)

                SESSID = uuid4().int.__str__()[:10]
                status = admin_user.get(id,"BASIC")
                oauth_user[SESSID] = [id,login,status]
                ##print(oauth_user[SESSID])
                resp = flask.make_response(redirect("/geii/forum-metier/admin"))  
                resp.set_cookie("SESSID", value = SESSID)
                #print(f"USER {id} authorized with {status} authority")
                return resp
            else:
                #print('Degage')
                return abort(403)
                
            
        else:
            return redirect(f"https://cas.u-bordeaux.fr/cas/login?service=https://www.iut.u-bordeaux.fr/geii/forum-metier/oauth")
    else:
        return redirect(f"https://cas.u-bordeaux.fr/cas/login?service=https://www.iut.u-bordeaux.fr/geii/forum-metier/oauth")

def connect_to_DB_forum_metier():
    try:
        DB = mariadb.connect(host="localhost",
                            port=3306,
                            user="warren",
                            password="cultiver-TAPEZ-mijote-68594-infirmes-tigre-aditya",
                            database="forummetier",
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
                            password="cultiver-TAPEZ-mijote-68594-infirmes-tigre-aditya",
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
    return render_template('formV3.html')

@app.route("/forum-metier/admin",methods=['GET'])
def admin():
    if CAS:
        if request.cookies.get("SESSID") != None:
            if request.cookies.get("SESSID") in oauth_user.keys() :
                data = request.form
                DB = connect_to_DB_forum_metier()
                cur = DB.cursor()
                cur.execute('SELECT * FROM `forummetier`.`DATA`;')
                data = list(item for item in cur.fetchall())
                return render_template('admin.html',data=data)
            else:
                return redirect("/geii/forum-metier/oauth")
        else:
            return redirect("/geii/forum-metier/oauth")
    else:
        data = request.form
        DB = connect_to_DB_forum_metier()
        cur = DB.cursor()
        cur.execute('SELECT * FROM `forummetier`.`DATA`;')
        data = list(item for item in cur.fetchall())
        return render_template('admin.html',data=data)


@app.route("/forum-metier/admin/badges",methods=['POST'])
def admin_generate_badges_zip():
    print("start badging")
    DB = connect_to_DB_forum_metier()
    cur = DB.cursor()
    try:
        cur.execute('SELECT * FROM `forummetier`.`DATA`;')
        rows = cur.fetchall()
        columns = [column[0] for column in cur.description]
    finally:
        cur.close()
        DB.close()

    records = [dict(zip(columns, row)) for row in rows]
    participants = extract_participants(records)
    if not participants:
        print("pas de participant")
        abort(404, description="Aucun participant n'a été trouvé pour générer les badges.")

    template_path = Path(__file__).resolve().parent / "static/ressources/badge_template.svg"
    if not template_path.exists():
        abort(500, description="Le template de badge est introuvable sur le serveur.")

    template_root = ET.parse(template_path).getroot()

    archive_io = BytesIO()
    with zipfile.ZipFile(archive_io, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for index, participant in enumerate(participants, start=1):
            svg_bytes = render_badge_svg(
                template_root,
                participant,
                # Les recherches de logos en ligne peuvent ralentir fortement
                # la génération côté serveur et entraîner un "proxy error".
                # On se limite donc aux logos locaux pour cette route.
                allow_online_logo_lookup=False,
            )
            archive.writestr(f"{badge_basename(participant, index)}.svg", svg_bytes)

    archive_io.seek(0)
    print('badge fini')
    return send_file(
        archive_io,
        mimetype="application/zip",
        as_attachment=True,
        download_name="badges_svg.zip",
    )
    

@app.route("/forum-metier/validate",methods=['POST'])
def validate():
    data = request.form
    DB = connect_to_DB_forum_metier()
    cur = DB.cursor()
    cur.execute("""INSERT INTO `forummetier`.DATA(ent_nom,ent_adresse,ent_cp,ent_ville,ent_desc,parcours,nb_p,p1_nom,p1_prenom,p1_email,p1_poste,p1_dej,p2_nom,p2_prenom,p2_email,p2_poste,p2_dej,p3_nom,p3_prenom,p3_email,p3_poste,p3_dej) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
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
        app.run(host="0.0.0.0",port=6970,debug=True)
