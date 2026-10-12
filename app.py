from flask import Flask, jsonify, render_template

app = Flask(__name__, static_folder="images", static_url_path="/images")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/definicion-sistema")
def definicion_sistema():
    return render_template("definicion_sistema.html")


@app.get("/problema")
def problema():
    return render_template("problema.html")


@app.get("/variables-parametros")
def variables_parametros():
    return render_template("variables_parametros.html")


@app.get("/relaciones-logico-matematicas")
def relaciones_logico_matematicas():
    return render_template("relaciones_logico_matematicas.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run()
