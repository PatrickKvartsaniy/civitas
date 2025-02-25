@app.route("/")
@app.route("/home")
def home():
    return render_template("base.html", title="home")


@app.route("/mapexplorer")
def MapExplorer():
    return render_template("MapExplorer.html", title="Map Explorer")


@app.route("/map")  # for map full screen mode
def map():
    return render_template("map.html", title="Map")


# page container for the insights page
@app.route("/dashboard")
def dashboard():
    context = {"title": "Dashboard", "data_variables": datascript.data_variables}
    return render_template("Dashboard.html", **context)


@app.route("/dashboard/index")
def dashboard_index():
    context = {
        "title": "Insights Dashboard",
        "today_date": datetime.today().strftime("%b %d, %Y"),  # Format: Feb 13, 2025
        "current_hour": datetime.now().strftime("%H") + ":00",
        "data_variables": datascript.data_variables,
    }
    return render_template("dashboard_index.html", **context)


# @app.route('/export-pdf')
# def export_pdf():
#     # Render HTML content
#     html = render_template('export.html')  # This is the page you want to convert
#     pdf = HTML(string=html).write_pdf()  # Convert HTML to PDF
#     # Return PDF as downloadable file
#     return Response(pdf, content_type='application/pdf', headers={"Content-Disposition": "attachment; filename=exported.pdf"})


@app.route("/threedviewer")
def threedviewer():
    return render_template("ThreeDViewer.html", title="3D Viewer")


# ensures that the script runs only when executed directly (not when imported).
if __name__ == "__main__":
    app.run(debug=True)
# debug=True enables debug mode, which:
# Automatically restarts the server on code changes and Shows detailed error messages in the browser if something goes wrong.
