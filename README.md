# Modelación y Simulación de Cajas de Supermercado (Flask)

**Universidad de Cundinamarca**  
**Asignatura:** Modelación y Simulación (9.º Semestre)  
**Tema:** Simulación de Eventos Discretos (DES) - Sistema de Colas Multicanal FIFO  

---

## 📌 Descripción del Proyecto

Aplicación web interactiva y modular en **Flask** que aborda la totalidad de los **12 puntos de la guía de modelación y simulación**:

1. **Definición del Sistema:** Elementos, entidades (*Cliente*), recursos (*Cajero*), procesos de cobro y restricciones operativas (`/definicion-sistema`).
2. **Planteamiento del Problema:** Situación monopuesto actual, causas de congestión, variable de interés principal ($W_q$) y pregunta de investigación (`/problema`).
3. **Variables y Parámetros:** Especificación metodológica completa sustentada en el dataset transaccional POS (`/variables-parametros`).
4. **Relaciones Lógico-Matemáticas:** Ecuaciones de eventos discretos, cálculo de instantes temporales ($A_i, B_i, D_i$), colas ($Q(t)$) y métricas de desempeño (`/relaciones-logico-matematicas`).
5. **Construcción del Modelo de Simulación:** Motor de simulación en Python puro (`core/simulator.py`) utilizando transformadas inversas y el algoritmo Congruencial Lineal (LCG).
6. **Verificación y Validación:** Pruebas unitarias de consistencia temporal y conservación de flujo (`tests/test_simulation.py`), contrastadas analíticamente con el modelo de colas Erlang-C ($M/M/c$).
7. **Diseño y Ejecución de la Simulación:** Turno de 8 horas (28.800 s), 30 réplicas independientes, condición de sistema vacío y esquema de semillas reproducibles.
8. **Estudio Estadístico:** Media, desviación estándar, varianza, mediana, cuartiles ($IQR$), mínimo, máximo, asimetría e histogramas con Chart.js.
9. **Pruebas de Hipótesis:** Contraste formal de Welch ($t$-Student) comparando $c=1$ vs $c=2$ con nivel de significancia $\alpha = 0.05$ y cálculo de $p$-valor.
10. **Intervalos de Confianza:** Estimaciones por intervalo al 95% de confianza para el tiempo promedio de espera en fila en cada escenario.
11. **Análisis de Escenarios y Sensibilidad:** Comparativa de $c=1$ (actual), $c=2$ (propuesto) y $c=3$ (expansión), evaluando rendimientos decrecientes y saturación.
12. **Conclusiones y Toma de Decisiones:** Sustentación cuantitativa y recomendaciones operativas para la gerencia del supermercado.

---

## 🚀 Instalación y Ejecución

### 1. Requisitos
- Python 3.9 o superior

### 2. Iniciar la Aplicación en Windows (PowerShell)

```powershell
python -m pip install -r requirements.txt
python run.py
```

Abre en tu navegador:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧭 Rutas de la Aplicación

- `/`: Menú interactivo principal y mapa de navegación de los 12 puntos.
- `/definicion-sistema`: Elementos y flujo operativo con diagrama de atención.
- `/problema`: Formulación estructurada del problema y variable de interés.
- `/variables-parametros`: Fichas técnicas de variables de entrada, estado y salida.
- `/relaciones-logico-matematicas`: Ecuaciones matemáticas del modelo de simulación.
- `/simulador`: **Simulador interactivo en tiempo real** con controles, gráficos de colas e histogramas con Chart.js.
- `/estudio-estadistico`: **Informe integral de los Puntos 6 al 12** con tablas de réplicas, pruebas de hipótesis paso a paso e intervalos de confianza.
- `/health`: Endpoint de estado (`{"status": "ok"}`).

---

## 🧪 Pruebas Unitarias de Verificación (Punto 6)

Para ejecutar la batería de pruebas de verificación automatizadas:

```powershell
python -m unittest discover tests
```
