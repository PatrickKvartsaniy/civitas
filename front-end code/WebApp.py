from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("base.html",title="Civiats Home")

@app.route("/mapexplorer")
def MapExplorer():
    return render_template("MapExplorer.html",title="Map Explorer")

@app.route("/dashboard")
def dashboard():
    context = {"title": "Dashboard",}
    return render_template("Dashboard.html", **context)

@app.route("/threedviewer")
def threedviewer():
    return render_template("ThreeDViewer.html", title= "3D Viewer",)


if __name__ == "__main__":
    app.run(debug=True)