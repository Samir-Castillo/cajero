from flask import Flask, jsonify, render_template, request
from core.simulator import SupermarketSimulation, run_experiment
from core.statistics import (
    calculate_descriptive_stats,
    calculate_confidence_interval,
    two_sample_hypothesis_test,
    theoretical_erlang_c
)

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


@app.get("/simulador")
def simulador():
    return render_template("simulador.html")


@app.get("/estudio-estadistico")
def estudio_estadistico():
    # Ejecuta el experimento formal de 30 réplicas para los 3 escenarios
    # con parámetros del problema (Turno de 8h = 28800s, arribos cada 90s, servicio media 73.7s std 64.35s)
    exp_c1 = run_experiment(num_cajeros=1, replications=30, base_seed=1001)
    exp_c2 = run_experiment(num_cajeros=2, replications=30, base_seed=1001)
    exp_c3 = run_experiment(num_cajeros=3, replications=30, base_seed=1001)

    stats_c1 = calculate_descriptive_stats(exp_c1["wait_times"])
    stats_c2 = calculate_descriptive_stats(exp_c2["wait_times"])
    stats_c3 = calculate_descriptive_stats(exp_c3["wait_times"])

    ci_c1 = calculate_confidence_interval(exp_c1["wait_times"], confidence=0.95)
    ci_c2 = calculate_confidence_interval(exp_c2["wait_times"], confidence=0.95)
    ci_c3 = calculate_confidence_interval(exp_c3["wait_times"], confidence=0.95)

    hypothesis_test_1v2 = two_sample_hypothesis_test(
        exp_c1["wait_times"],
        exp_c2["wait_times"],
        alpha=0.05,
        scenario_1_name="1 Cajero (Actual)",
        scenario_2_name="2 Cajeros (Propuesto)"
    )

    hypothesis_test_2v3 = two_sample_hypothesis_test(
        exp_c2["wait_times"],
        exp_c3["wait_times"],
        alpha=0.05,
        scenario_1_name="2 Cajeros (Propuesto)",
        scenario_2_name="3 Cajeros (Expansión)"
    )

    # Validación analítica M/M/c Erlang-C
    erlang_c1 = theoretical_erlang_c(1.0 / 90.0, 1.0 / 73.70, num_servers_c=1)
    erlang_c2 = theoretical_erlang_c(1.0 / 90.0, 1.0 / 73.70, num_servers_c=2)
    erlang_c3 = theoretical_erlang_c(1.0 / 90.0, 1.0 / 73.70, num_servers_c=3)

    return render_template(
        "estudio_estadistico.html",
        exp_c1=exp_c1,
        exp_c2=exp_c2,
        exp_c3=exp_c3,
        stats_c1=stats_c1,
        stats_c2=stats_c2,
        stats_c3=stats_c3,
        ci_c1=ci_c1,
        ci_c2=ci_c2,
        ci_c3=ci_c3,
        ht_1v2=hypothesis_test_1v2,
        ht_2v3=hypothesis_test_2v3,
        erlang_c1=erlang_c1,
        erlang_c2=erlang_c2,
        erlang_c3=erlang_c3
    )


@app.post("/api/simular")
def api_simular():
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        num_cajeros = int(data.get("num_cajeros", 1))
        horizon = float(data.get("horizon_seconds", 28800))
        mean_interarrival = float(data.get("mean_interarrival", 90))
        service_mean = float(data.get("service_mean", 73.7))
        service_std = float(data.get("service_std", 64.35))
        service_dist = str(data.get("service_dist", "lognormal"))
        replications = int(data.get("replications", 30))
        seed = int(data.get("seed", 1001))

        # Corrida individual para traza detallada
        sim_single = SupermarketSimulation(
            num_cajeros=num_cajeros,
            horizon_seconds=horizon,
            mean_interarrival=mean_interarrival,
            service_mean=service_mean,
            service_std=service_std,
            service_dist=service_dist,
            seed=seed
        )
        single_result = sim_single.run_single()

        # Experimento con réplicas para estadística
        experiment = run_experiment(
            num_cajeros=num_cajeros,
            horizon_seconds=horizon,
            mean_interarrival=mean_interarrival,
            service_mean=service_mean,
            service_std=service_std,
            service_dist=service_dist,
            replications=replications,
            base_seed=seed
        )

        stats = calculate_descriptive_stats(experiment["wait_times"])
        ci = calculate_confidence_interval(experiment["wait_times"], confidence=0.95)

        # Validación teórica M/M/c
        lambda_rate = 1.0 / mean_interarrival
        mu_rate = 1.0 / service_mean
        erlang_val = theoretical_erlang_c(lambda_rate, mu_rate, num_cajeros)

        return jsonify({
            "status": "success",
            "single_run": single_result,
            "experiment": {
                "replica_results": experiment["replica_results"],
                "wait_times": experiment["wait_times"],
                "utilizations": experiment["utilizations"]
            },
            "stats": stats,
            "confidence_interval": ci,
            "theoretical_erlang": erlang_val
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run()
