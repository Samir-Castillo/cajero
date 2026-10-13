"""
Módulo de Métodos Estadísticos y Teoría de Colas.
Implementa:
1. Estadísticos Descriptivos (Media, Varianza, Cuartiles, IQR, Asimetría).
2. Intervalos de Confianza t-Student (Punto 10).
3. Pruebas de Hipótesis para Diferencia de Medias (Punto 9).
4. Solución Analítica M/M/c de Erlang-C para Verificación y Validación (Punto 6).
"""

import math
from typing import Dict, Any, List, Tuple


def student_t_pdf(t: float, df: float) -> float:
    """Función de densidad de probabilidad t de Student."""
    coef = math.gamma((df + 1.0) / 2.0) / (math.sqrt(df * math.pi) * math.gamma(df / 2.0))
    return coef * ((1.0 + (t ** 2) / df) ** (-(df + 1.0) / 2.0))


def student_t_cdf(t: float, df: float, steps: int = 1000) -> float:
    """Función de distribución acumulada t de Student usando regla de Simpson."""
    if t == 0.0:
        return 0.5
    sign = 1.0 if t > 0.0 else -1.0
    t_abs = abs(t)
    h = t_abs / steps
    integral = student_t_pdf(0.0, df) + student_t_pdf(t_abs, df)
    for i in range(1, steps):
        x = i * h
        integral += (4.0 if i % 2 == 1 else 2.0) * student_t_pdf(x, df)
    area = (h / 3.0) * integral
    res = 0.5 + sign * area
    return min(1.0, max(0.0, res))


def student_t_ppf(p: float, df: float) -> float:
    """Función de cuantiles (inversa de CDF) para t de Student mediante búsqueda binaria."""
    if p <= 0.0:
        return -50.0
    if p >= 1.0:
        return 50.0
    if abs(p - 0.5) < 1e-9:
        return 0.0

    target = p if p > 0.5 else (1.0 - p)
    low, high = 0.0, 50.0
    for _ in range(50):
        mid = (low + high) / 2.0
        if student_t_cdf(mid, df) < target:
            low = mid
        else:
            high = mid
    val = (low + high) / 2.0
    return val if p > 0.5 else -val


def calculate_descriptive_stats(data: List[float], num_bins: int = 8) -> Dict[str, Any]:
    """
    Calcula estadísticos descriptivos completos para una muestra de datos.
    """
    n = len(data)
    if n == 0:
        raise ValueError("La lista de datos no puede estar vacía.")

    s_data = sorted(data)
    mean_val = sum(s_data) / n

    if n > 1:
        variance_val = sum((x - mean_val) ** 2 for x in s_data) / (n - 1)
        std_val = math.sqrt(variance_val)
    else:
        variance_val = 0.0
        std_val = 0.0

    # Mediana y cuartiles
    def get_percentile(sorted_list: List[float], p: float) -> float:
        idx = p * (len(sorted_list) - 1)
        low = int(math.floor(idx))
        high = int(math.ceil(idx))
        if low == high:
            return sorted_list[low]
        weight = idx - low
        return sorted_list[low] * (1.0 - weight) + sorted_list[high] * weight

    median_val = get_percentile(s_data, 0.50)
    q1_val = get_percentile(s_data, 0.25)
    q3_val = get_percentile(s_data, 0.75)
    iqr_val = q3_val - q1_val

    min_val = s_data[0]
    max_val = s_data[-1]

    # Coeficiente de asimetría de Fisher
    if n > 2 and std_val > 1e-9:
        skewness_val = (sum((x - mean_val) ** 3 for x in s_data) / n) / (std_val ** 3)
    else:
        skewness_val = 0.0

    # Construcción de histograma
    bin_min = min_val
    bin_max = max_val if max_val > min_val else min_val + 1.0
    bin_width = (bin_max - bin_min) / num_bins
    bins = []
    for b in range(num_bins):
        low_edge = bin_min + b * bin_width
        high_edge = bin_min + (b + 1) * bin_width
        # Si es el último bin, incluye el extremo superior
        if b == num_bins - 1:
            count = sum(1 for x in s_data if low_edge <= x <= high_edge)
        else:
            count = sum(1 for x in s_data if low_edge <= x < high_edge)
        bins.append({
            "bin_label": f"[{round(low_edge, 1)} - {round(high_edge, 1)})",
            "low": round(low_edge, 2),
            "high": round(high_edge, 2),
            "mid": round((low_edge + high_edge) / 2.0, 2),
            "count": count,
            "relative_freq": round(count / n, 4)
        })

    return {
        "n": n,
        "mean": round(mean_val, 2),
        "std": round(std_val, 2),
        "variance": round(variance_val, 2),
        "median": round(median_val, 2),
        "q1": round(q1_val, 2),
        "q3": round(q3_val, 2),
        "iqr": round(iqr_val, 2),
        "min": round(min_val, 2),
        "max": round(max_val, 2),
        "skewness": round(skewness_val, 2),
        "histogram_bins": bins
    }


def calculate_confidence_interval(data: List[float], confidence: float = 0.95) -> Dict[str, Any]:
    """
    Construye el intervalo de confianza bilateral al nivel dado (ej. 95%)
    usando la distribución t de Student con n - 1 grados de libertad:
    IC = X_bar ± t_(alpha/2, n-1) * (S / sqrt(n))
    """
    n = len(data)
    if n < 2:
        raise ValueError("Se requieren al menos 2 réplicas para calcular el intervalo de confianza.")

    alpha = 1.0 - confidence
    mean_val = sum(data) / n
    var_val = sum((x - mean_val) ** 2 for x in data) / (n - 1)
    std_val = math.sqrt(var_val)
    df = n - 1

    t_crit = student_t_ppf(1.0 - alpha / 2.0, df)
    std_error = std_val / math.sqrt(n)
    margin_error = t_crit * std_error

    lower_bound = max(0.0, mean_val - margin_error)
    upper_bound = mean_val + margin_error

    return {
        "confidence_level": confidence,
        "confidence_pct": round(confidence * 100, 1),
        "n": n,
        "df": df,
        "point_estimate": round(mean_val, 2),
        "std_dev": round(std_val, 2),
        "std_error": round(std_error, 2),
        "t_critical": round(t_crit, 4),
        "margin_of_error": round(margin_error, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "interval_str": f"[{round(lower_bound, 2)}, {round(upper_bound, 2)}]"
    }


def two_sample_hypothesis_test(
    sample_1: List[float],
    sample_2: List[float],
    alpha: float = 0.05,
    scenario_1_name: str = "Escenario 1 (1 cajero)",
    scenario_2_name: str = "Escenario 2 (2 cajeros)"
) -> Dict[str, Any]:
    """
    Prueba de hipótesis t de Student (Welch t-test para varianzas desiguales):
    H0: mu_1 <= mu_2 (Agregar cajeros NO reduce el tiempo promedio de espera)
    H1: mu_1 > mu_2  (Agregar cajeros REDUCE significativamente el tiempo promedio de espera)
    """
    n1 = len(sample_1)
    n2 = len(sample_2)
    if n1 < 2 or n2 < 2:
        raise ValueError("Cada muestra debe tener al menos 2 observaciones.")

    mean1 = sum(sample_1) / n1
    mean2 = sum(sample_2) / n2

    var1 = sum((x - mean1) ** 2 for x in sample_1) / (n1 - 1)
    var2 = sum((x - mean2) ** 2 for x in sample_2) / (n2 - 1)

    s1 = math.sqrt(var1)
    s2 = math.sqrt(var2)

    diff_means = mean1 - mean2
    std_error_diff = math.sqrt((var1 / n1) + (var2 / n2))

    t_stat = diff_means / std_error_diff if std_error_diff > 1e-12 else 0.0

    # Grados de libertad por aproximación de Welch-Satterthwaite
    num_df = ((var1 / n1) + (var2 / n2)) ** 2
    den_df = (((var1 / n1) ** 2) / (n1 - 1)) + (((var2 / n2) ** 2) / (n2 - 1))
    df_welch = num_df / den_df if den_df > 1e-12 else min(n1 - 1, n2 - 1)

    # Valor crítico unilateral derecho para alpha
    t_crit = student_t_ppf(1.0 - alpha, df_welch)

    # p-valor unilateral: P(T >= t_stat) = 1 - CDF(t_stat)
    p_value = 1.0 - student_t_cdf(t_stat, df_welch)

    reject_h0 = bool(t_stat > t_crit and p_value < alpha)

    if reject_h0:
        conclusion = (
            f"Con un nivel de significancia de α = {alpha} (confianza del {(1-alpha)*100:.0f}%), "
            f"se RECHAZA la hipotesis nula H0 (t = {t_stat:.4f} > t_critico = {t_crit:.4f}, p-valor = {p_value:.4e} < {alpha}). "
            f"Existe evidencia estadistica altamente significativa de que la habilitacion de mas cajeros "
            f"reduce sustancialmente el tiempo promedio de espera en fila."
        )
    else:
        conclusion = (
            f"Con un nivel de significancia de α = {alpha}, "
            f"NO se rechaza la hipotesis nula H0 (t = {t_stat:.4f} <= t_critico = {t_crit:.4f}, p-valor = {p_value:.4f}). "
            f"No existe suficiente evidencia estadistica para afirmar una diferencia significativa."
        )

    return {
        "scenario_1": scenario_1_name,
        "scenario_2": scenario_2_name,
        "n1": n1,
        "n2": n2,
        "mean1": round(mean1, 2),
        "mean2": round(mean2, 2),
        "std1": round(s1, 2),
        "std2": round(s2, 2),
        "diff_means": round(diff_means, 2),
        "t_statistic": round(t_stat, 4),
        "df": round(df_welch, 2),
        "alpha": alpha,
        "t_critical": round(t_crit, 4),
        "p_value": round(p_value, 6) if p_value >= 1e-6 else float(f"{p_value:.2e}"),
        "reject_h0": reject_h0,
        "decision": "Rechazar H0" if reject_h0 else "No rechazar H0",
        "conclusion": conclusion
    }


def theoretical_erlang_c(
    arrival_rate_lambda: float,
    service_rate_mu: float,
    num_servers_c: int
) -> Dict[str, Any]:
    """
    Cálculo analítico del modelo de colas M/M/c (Erlang-C) para validación teórica.
    arrival_rate_lambda: clientes por segundo
    service_rate_mu: clientes atendidos por segundo por cada cajero
    num_servers_c: número de cajeros
    """
    c = num_servers_c
    lam = arrival_rate_lambda
    mu = service_rate_mu

    if lam <= 0 or mu <= 0 or c < 1:
        raise ValueError("Parámetros inválidos para modelo Erlang-C.")

    # Intensidad de tráfico y utilización
    traffic_intensity = lam / mu  # r = lambda / mu
    rho = traffic_intensity / c    # rho = lambda / (c * mu)

    # Condición de estabilidad: rho < 1
    if rho >= 1.0:
        return {
            "stable": False,
            "rho": round(rho, 4),
            "message": "El sistema es inestable (tasa de llegadas supera la capacidad de atención global, rho >= 1)."
        }

    # Cálculo de P0 (Probabilidad de sistema vacío)
    sum_terms = sum((traffic_intensity ** k) / math.factorial(k) for k in range(c))
    last_term = ((traffic_intensity ** c) / (math.factorial(c) * (1.0 - rho)))
    p0 = 1.0 / (sum_terms + last_term)

    # Probabilidad de espera (Fórmula de Erlang-C: C(c, r))
    erlang_c_prob = last_term * p0

    # Lq: Clientes promedio en cola
    lq = (erlang_c_prob * rho) / (1.0 - rho)

    # Wq: Tiempo promedio de espera en cola (segundos) por fórmula de Little
    wq = lq / lam

    # W: Tiempo promedio total en el sistema (segundos)
    w = wq + (1.0 / mu)

    # L: Clientes promedio en el sistema
    l_sys = lam * w

    return {
        "stable": True,
        "c": c,
        "lambda_arrivals_sec": round(lam, 6),
        "mu_service_sec": round(mu, 6),
        "traffic_intensity": round(traffic_intensity, 4),
        "utilization_rho": round(rho, 4),
        "p0_empty_system": round(p0, 4),
        "prob_wait_erlang_c": round(erlang_c_prob, 4),
        "Lq_avg_queue_customers": round(lq, 2),
        "Wq_avg_wait_seconds": round(wq, 2),
        "W_avg_system_seconds": round(w, 2),
        "L_avg_system_customers": round(l_sys, 2)
    }
