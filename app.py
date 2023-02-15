from flask import Flask, render_template, session, request, url_for, redirect
from flask.helpers import make_response
from flask.json import jsonify
import pymongo
import json
from bson import ObjectId


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myDB = myclient["sampleDB"]


users = myDB["users"]

app = Flask(__name__)
app.secret_key = "jcnuTad478"


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


@app. route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user_email = request.form["email"]
        user_name = request.form["usrname"]
        user_password = request.form["passwd"]

        if users.count_documents({'email': user_email}) == 0:
            new_user = {
                'email': user_email,
                'username': user_name,
                'password': user_password
            }
            users.insert_one(new_user)
            session["email"] = user_email
            return redirect(url_for("home"))
        else:
            render_template(
                "login.html", message="User account already exists")
    else:
        return render_template("signup.html")


@app. route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["passwd"]
        # check credentials
        x = users.find_one({'email': user_email})
        if x is not None:
            if x['password'] == user_password:
                session["email"] = user_email
                return redirect(url_for("home"))
            else:
                return render_template("login.html", message="Wrong password")
        else:
            return render_template("login.html", message="Invalid email id")

    else:
        return render_template("login.html", message="")


@app. route("/logout", methods=["GET"])
def logout():
    session.pop('email', None)
    return redirect(url_for("home"))

@app.route("/updatePassword", methods=["POST"])
def updatePassword():
    msg = ""
    x = users.find_one({'email': session['email']})
    user_password = request.form["oldpasswd"]
    if x['password'] == user_password:
        new_password = request.form["newpasswd"]
        users.update_one({'email': session['email']}, {
                         '$set': {'password': new_password}})
        msg = "Updated password successfully"
    else:
        msg = "Wrong password"

    return render_template("profile.html", title="User profile", message=msg)


@app.route("/deleteAccount", methods=["POST"])
def deleteUser():
    user_password = request.form["passwd"]
    x = users.find_one({'email': session['email']})
    if x['password'] == user_password:
        users.delete_one({'email': session['email']})
        return redirect(url_for("logout"))
    else:
        msg = "Wrong password. Account deletion failed."
        return render_template("profile.html", title="User profile", message=msg)  



@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route('/')
def home():
    if "email" in session:
        usrname = users.find_one({'email': session['email']})['username']
        usr_active_tasks = []
        # for x in usr_tasks:
        #     if x['status'] == 1:
        #         usr_active_tasks.append(x)
        return render_template("index.html", title="My home", user=usrname, tasks=usr_active_tasks)
    else:
        return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
