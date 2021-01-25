import mysql.connector
from flask_dance.contrib.google import make_google_blueprint, google
from flask import Flask, redirect, url_for, render_template
# from flask import logout_user
from dotenv import load_dotenv
import os

load_dotenv('.env')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')
blueprint = make_google_blueprint(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
)
app.register_blueprint(blueprint, url_prefix="/login")


def get_data():
    mydb = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
    )
    c = mydb.cursor()
    c.execute("select vasarlo_neve from vasarlok where vasarlo_id=3")
    my_result = c.fetchall()
    mydb.commit()
    mydb.close()
    print(type(my_result[0]))
    return my_result[0][0]


@app.route('/')
def index():
    # get_data()
    # a flask alapértelmezetten a templates mappában keresi a html
    # template-eket
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    email = resp.json()["email"]
    return render_template('index.html', name=get_data(), email=email)


@app.route('/logout')
def logout():
    token = blueprint.token["access_token"]
    resp = google.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.ok, resp.text
    # logout_user()        # Delete Flask-Login's session #TODO
    del blueprint.token  # Delete OAuth token from storage
    return render_template('logout.html')


# ha a futtatott file, az éppen ez a file
if __name__ == '__main__':
    app.debug = True
    # akkor elindul a flask
    app.run(host='0.0.0.0', port=5000)
