"""
Pruebas Unitarias y de Verificación del Sistema de Simulación.
Demuestra la verificación del modelo (Punto 6 de la guía de modelación):
- Verificación de generadores y variables aleatorias.
- Conservación de entidades en el sistema.
- Consistencia temporal de eventos discretos (A_i <= B_i <= D_i, W_i >= 0).
- Coherencia del cálculo estadístico e inferencial.
"""

import unittest
from core.generators import RandomVariateGenerator, lcg_generator
from core.simulator import SupermarketSimulation, run_experiment
from core.statistics import (
    calculate_descriptive_stats,
    calculate_confidence_interval,
    two_sample_hypothesis_test,
    theoretical_erlang_c
)


class TestSimulationVerification(unittest.TestCase):

    def test_lcg_generator_range(self):
        """Verifica que el generador LCG produzca valores en (0, 1)."""
        numbers = lcg_generator(seed=12345, n=1000)
        self.assertEqual(len(numbers), 1000)
        for r in numbers:
            self.assertGreater(r, 0.0)
            self.assertLess(r, 1.0)

    def test_exponential_and_lognormal_variates(self):
        """Verifica que las variables aleatorias sean estrictamente positivas."""
        rng = RandomVariateGenerator(seed=999)
        for _ in range(200):
            exp_val = rng.exponential(mean=90.0)
            log_val = rng.lognormal(mean=73.70, std_dev=64.35)
            self.assertGreater(exp_val, 0.0)
            self.assertGreater(log_val, 0.0)

    def test_conservation_of_entities(self):
        """
        Verifica el principio de conservación de flujo:
        Total llegadas = Atendidos + En atención al final + En fila al final
        """
        sim = SupermarketSimulation(
            num_cajeros=2,
            horizon_seconds=7200.0,
            mean_interarrival=90.0,
            seed=42
        )
        res = sim.run_single()
        total = res["total_arrivals"]
        completed = res["completed_clients"]
        in_service = res["in_service_at_end"]
        in_queue = res["in_queue_at_end"]
        self.assertEqual(total, completed + in_service + in_queue)

    def test_temporal_consistency(self):
        """
        Verifica las relaciones lógico-matemáticas temporales para cada cliente:
        - B_i >= A_i (la atención nunca comienza antes de la llegada)
        - W_i = B_i - A_i >= 0 (no hay tiempo de espera negativo)
        - D_i = B_i + S_i (la salida coincide con el fin del servicio)
        """
        sim = SupermarketSimulation(
            num_cajeros=1,
            horizon_seconds=3600.0,
            mean_interarrival=60.0,
            seed=101
        )
        res = sim.run_single()
        for client in res["clients_sample"]:
            self.assertGreaterEqual(client["begin_service"], client["arrival_time"])
            self.assertGreaterEqual(client["wait_time"], 0.0)
            expected_wait = round(client["begin_service"] - client["arrival_time"], 2)
            self.assertAlmostEqual(client["wait_time"], expected_wait, places=1)
            expected_departure = round(client["begin_service"] + client["service_time"], 2)
            self.assertAlmostEqual(client["departure_time"], expected_departure, places=1)

    def test_capacity_scaling_reduces_wait(self):
        """
        Verifica que al aumentar de 1 a 3 cajeros con la misma semilla y carga,
        el tiempo promedio de espera se reduzca significativamente.
        """
        sim_1 = SupermarketSimulation(num_cajeros=1, horizon_seconds=14400.0, seed=777)
        res_1 = sim_1.run_single()

        sim_3 = SupermarketSimulation(num_cajeros=3, horizon_seconds=14400.0, seed=777)
        res_3 = sim_3.run_single()

        self.assertLess(res_3["avg_wait_time"], res_1["avg_wait_time"])

    def test_descriptive_stats(self):
        """Verifica el cálculo de estadísticas descriptivas con datos controlados."""
        data = [10.0, 20.0, 30.0, 40.0, 50.0]
        stats = calculate_descriptive_stats(data)
        self.assertEqual(stats["n"], 5)
        self.assertAlmostEqual(stats["mean"], 30.0)
        self.assertAlmostEqual(stats["median"], 30.0)
        self.assertAlmostEqual(stats["min"], 10.0)
        self.assertAlmostEqual(stats["max"], 50.0)

    def test_confidence_interval(self):
        """Verifica que el intervalo de confianza contenga la estimación puntual."""
        data = [100.0, 105.0, 95.0, 110.0, 98.0, 102.0, 104.0, 99.0]
        ci = calculate_confidence_interval(data, confidence=0.95)
        self.assertLess(ci["lower_bound"], ci["point_estimate"])
        self.assertGreater(ci["upper_bound"], ci["point_estimate"])
        self.assertEqual(ci["df"], len(data) - 1)

    def test_hypothesis_test_rejects_null_when_means_differ(self):
        """Verifica que la prueba t de Welch rechace H0 ante muestras disímiles."""
        sample_high = [250.0, 260.0, 240.0, 255.0, 265.0, 245.0]
        sample_low = [20.0, 25.0, 18.0, 22.0, 24.0, 19.0]
        test_res = two_sample_hypothesis_test(sample_high, sample_low, alpha=0.05)
        self.assertTrue(test_res["reject_h0"])
        self.assertLess(test_res["p_value"], 0.001)

    def test_theoretical_erlang_c_stability(self):
        """Verifica el cálculo analítico del modelo Erlang-C M/M/c."""
        # Llegadas: 1 cliente cada 120s (lambda = 1/120)
        # Servicio: 73.7s (mu = 1/73.7)
        # Con c=1: rho = 73.7 / 120 = 0.614 < 1 (estable)
        lam = 1.0 / 120.0
        mu = 1.0 / 73.7
        res = theoretical_erlang_c(lam, mu, num_servers_c=1)
        self.assertTrue(res["stable"])
        self.assertGreater(res["Wq_avg_wait_seconds"], 0.0)
        self.assertLess(res["utilization_rho"], 1.0)


if __name__ == "__main__":
    unittest.main()
