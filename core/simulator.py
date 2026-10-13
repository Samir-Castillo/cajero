"""
Motor de Simulación de Eventos Discretos para Caja(s) de Supermercado.
Implementa el modelo multicanal FIFO formalizado en 'relaciones_logico_matematicas.html'.
"""

import math
from typing import Dict, Any, List, Optional
from .generators import RandomVariateGenerator


class SupermarketSimulation:
    """
    Simulador de eventos discretos para el sistema de atención en cajas de supermercado.
    """

    def __init__(
        self,
        num_cajeros: int = 1,
        horizon_seconds: float = 28800.0,  # 8 horas por defecto
        mean_interarrival: float = 90.0,   # Tiempo medio entre llegadas (segundos)
        service_mean: float = 73.70,       # Tiempo medio de servicio (POS TranTime)
        service_std: float = 64.35,        # Desviación de servicio (POS TranTime)
        service_dist: str = "lognormal",   # 'lognormal' o 'exponential'
        seed: int = 42
    ):
        if num_cajeros < 1:
            raise ValueError("El número de cajeros debe ser al menos 1.")
        if horizon_seconds <= 0:
            raise ValueError("El horizonte de simulación debe ser positivo.")
        if mean_interarrival <= 0:
            raise ValueError("El tiempo medio entre llegadas debe ser positivo.")

        self.num_cajeros = num_cajeros
        self.horizon = horizon_seconds
        self.mean_interarrival = mean_interarrival
        self.service_mean = service_mean
        self.service_std = service_std
        self.service_dist = service_dist
        self.seed = seed
        self.rng = RandomVariateGenerator(seed=seed)

    def _next_service_time(self) -> float:
        """Genera la duración del servicio según la distribución configurada."""
        if self.service_dist == "lognormal":
            return self.rng.lognormal(self.service_mean, self.service_std)
        elif self.service_dist == "exponential":
            return self.rng.exponential(self.service_mean)
        else:
            return self.rng.lognormal(self.service_mean, self.service_std)

    def run_single(self) -> Dict[str, Any]:
        """
        Ejecuta una corrida completa de simulación sobre el horizonte temporal especificado.
        Registra clientes, instantes temporales y métricas de rendimiento.
        """
        # Vector de disponibilidad de los c cajeros: F_j = instante en que se desocupa el cajero j
        # Al inicio (t=0), todos los cajeros están libres (F_j = 0)
        cajero_free_time = [0.0] * self.num_cajeros
        cajero_busy_time = [0.0] * self.num_cajeros

        current_time = 0.0
        client_id = 0
        clients = []

        # Trazas temporales para graficar la cola a lo largo del tiempo
        queue_timeline = [{"t": 0.0, "queue": 0, "system": 0}]

        # Generar clientes que arriban durante el horizonte de simulación
        while True:
            # Tiempo entre llegadas I_i ~ Exponencial(lambda)
            interarrival = self.rng.exponential(self.mean_interarrival)
            arrival_time = current_time + interarrival

            if arrival_time > self.horizon:
                # El cliente llega después del horizonte
                break

            client_id += 1
            current_time = arrival_time
            service_time = self._next_service_time()

            # Encontrar el cajero que se desocupa más temprano: min_j F_j
            earliest_cajero_idx = 0
            min_free_time = cajero_free_time[0]
            for j in range(1, self.num_cajeros):
                if cajero_free_time[j] < min_free_time:
                    min_free_time = cajero_free_time[j]
                    earliest_cajero_idx = j

            # B_i = max(A_i, min_j F_j)
            begin_service_time = max(arrival_time, min_free_time)

            # W_i = B_i - A_i (Tiempo de espera en fila)
            wait_time = max(0.0, begin_service_time - arrival_time)

            # D_i = B_i + S_i (Instante de salida de atención)
            departure_time = begin_service_time + service_time

            # Actualizar disponibilidad del cajero asignado: F_j = D_i
            cajero_free_time[earliest_cajero_idx] = departure_time

            # Acumular tiempo de ocupación efectivo dentro del horizonte
            # Si el servicio comenzó antes del horizonte, registrar la porción útil
            occupied_start = max(0.0, begin_service_time)
            occupied_end = min(self.horizon, departure_time)
            if occupied_end > occupied_start:
                cajero_busy_time[earliest_cajero_idx] += (occupied_end - occupied_start)

            completed = (departure_time <= self.horizon)

            clients.append({
                "id": client_id,
                "arrival_time": round(arrival_time, 2),
                "interarrival": round(interarrival, 2),
                "service_time": round(service_time, 2),
                "begin_service": round(begin_service_time, 2),
                "departure_time": round(departure_time, 2),
                "wait_time": round(wait_time, 2),
                "system_time": round(departure_time - arrival_time, 2),
                "cajero_id": earliest_cajero_idx + 1,
                "completed": completed
            })

        # Clientes atendidos completamente antes del horizonte
        completed_clients = [c for c in clients if c["completed"]]
        # Clientes que alcanzaron a iniciar o están en fila al fin del horizonte
        in_service_at_end = [c for c in clients if c["begin_service"] <= self.horizon < c["departure_time"]]
        in_queue_at_end = [c for c in clients if c["begin_service"] > self.horizon]

        n_completed = len(completed_clients)
        avg_wait_time = (
            sum(c["wait_time"] for c in completed_clients) / n_completed
            if n_completed > 0 else 0.0
        )
        avg_system_time = (
            sum(c["system_time"] for c in completed_clients) / n_completed
            if n_completed > 0 else 0.0
        )
        avg_service_time = (
            sum(c["service_time"] for c in completed_clients) / n_completed
            if n_completed > 0 else 0.0
        )

        # Utilización promedio de cajeros: U = sum(tiempo_ocupado) / (c * H)
        total_busy = sum(cajero_busy_time)
        utilization = total_busy / (self.num_cajeros * self.horizon)
        utilization = min(1.0, max(0.0, utilization))

        # Construir puntos de muestreo de cola a lo largo del tiempo para visualización (cada 300s / 5min)
        step = max(60.0, self.horizon / 60.0)
        t_sample = 0.0
        while t_sample <= self.horizon:
            # Clientes en cola en t_sample: A_i <= t < B_i
            q_t = sum(1 for c in clients if c["arrival_time"] <= t_sample < c["begin_service"])
            # Clientes en atención en t_sample: B_i <= t < D_i
            busy_t = sum(1 for c in clients if c["begin_service"] <= t_sample < c["departure_time"])
            queue_timeline.append({
                "t_min": round(t_sample / 60.0, 1),
                "queue": q_t,
                "system": q_t + busy_t
            })
            t_sample += step

        # Estimación del promedio temporal de la cola L_q
        avg_queue_length = (
            sum(pt["queue"] for pt in queue_timeline) / len(queue_timeline)
            if queue_timeline else 0.0
        )

        return {
            "num_cajeros": self.num_cajeros,
            "horizon_hours": self.horizon / 3600.0,
            "horizon_seconds": self.horizon,
            "total_arrivals": len(clients),
            "completed_clients": n_completed,
            "in_service_at_end": len(in_service_at_end),
            "in_queue_at_end": len(in_queue_at_end),
            "avg_wait_time": round(avg_wait_time, 2),
            "avg_system_time": round(avg_system_time, 2),
            "avg_service_time": round(avg_service_time, 2),
            "avg_queue_length": round(avg_queue_length, 2),
            "utilization_pct": round(utilization * 100.0, 2),
            "cajero_busy_times": [round(bt, 2) for bt in cajero_busy_time],
            "clients_sample": clients[:50],  # Primeros 50 clientes para inspección
            "queue_timeline": queue_timeline
        }


def run_experiment(
    num_cajeros: int = 1,
    horizon_seconds: float = 28800.0,
    mean_interarrival: float = 90.0,
    service_mean: float = 73.70,
    service_std: float = 64.35,
    service_dist: str = "lognormal",
    replications: int = 30,
    base_seed: int = 1001
) -> Dict[str, Any]:
    """
    Ejecuta un experimento con múltiples réplicas independientes.
    Retorna resultados de cada réplica y estadísticas agregadas.
    """
    replica_results = []
    wait_times = []
    utilizations = []
    queue_lengths = []
    arrivals = []
    completed = []

    for rep in range(1, replications + 1):
        rep_seed = base_seed + (rep * 997)
        sim = SupermarketSimulation(
            num_cajeros=num_cajeros,
            horizon_seconds=horizon_seconds,
            mean_interarrival=mean_interarrival,
            service_mean=service_mean,
            service_std=service_std,
            service_dist=service_dist,
            seed=rep_seed
        )
        res = sim.run_single()
        
        replica_data = {
            "replica": rep,
            "seed": rep_seed,
            "arrivals": res["total_arrivals"],
            "completed": res["completed_clients"],
            "avg_wait_time": res["avg_wait_time"],
            "avg_system_time": res["avg_system_time"],
            "avg_queue_length": res["avg_queue_length"],
            "utilization_pct": res["utilization_pct"]
        }
        replica_results.append(replica_data)

        wait_times.append(res["avg_wait_time"])
        utilizations.append(res["utilization_pct"])
        queue_lengths.append(res["avg_queue_length"])
        arrivals.append(res["total_arrivals"])
        completed.append(res["completed_clients"])

    return {
        "num_cajeros": num_cajeros,
        "replications": replications,
        "horizon_seconds": horizon_seconds,
        "mean_interarrival": mean_interarrival,
        "service_mean": service_mean,
        "replica_results": replica_results,
        "wait_times": wait_times,
        "utilizations": utilizations,
        "queue_lengths": queue_lengths,
        "arrivals": arrivals,
        "completed": completed
    }
