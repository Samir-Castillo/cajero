"""
Módulo de Generadores Pseudoaleatorios y Variables Aleatorias.
Reutiliza los principios del generador congruencial lineal (LCG) desarrollado
en la actividad previa y métodos de transformada inversa para distribuciones continuas.
"""

import math
from typing import Dict, Any, List, Optional, Tuple


def lcg_generator(seed: int, n: int, a: int = 1664525, c: int = 1013904223, m: int = 2**32) -> List[float]:
    """
    Generador Congruencial Lineal (LCG Mixto).
    Parámetros de Numerical Recipes: período completo garantizado por Hull-Dobell.
    Retorna números pseudoaleatorios normalizados en el intervalo [0, 1).
    """
    numbers = []
    x = seed
    for _ in range(n):
        x = (a * x + c) % m
        r = x / m
        # Asegurar que r esté estrictamente en (0, 1) para transformadas logarítmicas
        if r <= 0.0:
            r = 1e-10
        elif r >= 1.0:
            r = 1.0 - 1e-10
        numbers.append(r)
    return numbers


class RandomVariateGenerator:
    """
    Generador de variables aleatorias a partir de números pseudoaleatorios U(0, 1).
    Implementa el método de la transformada inversa y transformaciones estándar.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.current_x = seed
        self.a = 1664525
        self.c = 1013904223
        self.m = 2**32

    def uniform(self) -> float:
        """Genera un número pseudoaleatorio uniforme U(0, 1)."""
        self.current_x = (self.a * self.current_x + self.c) % self.m
        r = self.current_x / self.m
        if r <= 0.0:
            return 1e-10
        if r >= 1.0:
            return 1.0 - 1e-10
        return r

    def exponential(self, mean: float) -> float:
        """
        Genera una variable aleatoria exponencial con media dada.
        Transformada inversa: X = -media * ln(1 - U)
        """
        u = self.uniform()
        return -mean * math.log(1.0 - u)

    def lognormal(self, mean: float, std_dev: float) -> float:
        """
        Genera una variable aleatoria lognormal ajustada a la media y desviación observadas.
        Si X ~ Lognormal, entonces ln(X) ~ Normal(mu_n, sigma_n^2).
        Utiliza el método de Box-Muller.
        """
        # Conversión de media y varianza observadas a parámetros de la distribución normal subyacente
        var = std_dev ** 2
        mu_n = math.log((mean ** 2) / math.sqrt(var + mean ** 2))
        sigma_n = math.sqrt(math.log(1.0 + var / (mean ** 2)))

        # Box-Muller transform
        u1 = self.uniform()
        u2 = self.uniform()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

        val = math.exp(mu_n + sigma_n * z0)
        return max(val, 1.0)  # Un tiempo de servicio no puede ser menor a 1 segundo

    def empirical_service_time(self, default_mean: float = 73.70, default_std: float = 64.35) -> float:
        """
        Genera tiempos de servicio usando el modelo Lognormal basado en los parámetros
        observados en la variable TranTime del dataset POS (media = 73.70s, std = 64.35s).
        """
        return self.lognormal(default_mean, default_std)
