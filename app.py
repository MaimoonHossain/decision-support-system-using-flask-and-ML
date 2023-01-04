from flask import Flask, render_template, session, request, url_for, redirect
from flask.helpers import make_response
from flask.json import jsonify
import pymongo
import json
from bson import ObjectId


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myDB = myclient["sampleDB"]


users = myDB["users"]
tasks = myDB["tasks"]

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


@app.route("/markCompleted", methods=['POST'])
def markCompleted():
    t = request.get_json()
    print(t)
    tasks.update_one({'_id': ObjectId(t['id'])}, {'$set': {'status': 0}})
    return '200'


@app.route("/markAllCompleted", methods=['POST'])
def markAllCompleted():
    tasks.update_many({'user': session['email']}, {'$set': {'status': 0}})
    return '200'



@app.route("/addTask", methods=['POST'])
def addTask():
    t = request.get_json()
    new_task = {
        'content': t['task'],
        'status': 1,
        'user': session['email']
    }
    x = tasks.insert_one(new_task)
    res = make_response(jsonify({'id': str(x.inserted_id)}), 200)  
    return res


@app.route("/deleteCompleted")
def deleteCompletedTasks():
    tasks.delete_many({'user': session['email'], 'status': 0})
    return '200'


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route('/')
def home():
    if "email" in session:
        usrname = users.find_one({'email': session['email']})['username']
        usr_tasks = tasks.find({'user': session['email']})
        usr_active_tasks = []
        for x in usr_tasks:
            if x['status'] == 1:
                usr_active_tasks.append(x)
        return render_template("index.html", title="My home", user=usrname, tasks=usr_active_tasks)
    else:
        return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
