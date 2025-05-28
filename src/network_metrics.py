import subprocess
import speedtest as st
import igraph as ig
import matplotlib.pyplot as plt
import platform

hosts = ["172.29.150.87", "172.29.5.37", "172.29.130.128", "172.29.42.70"]
latencias = {}  # Guardaremos latencia por host

# Función para medir latencia con ping
def medir_latencia(host):
    so = platform.system().lower()
    if so == "windows":
        comando = ["ping", "-n", "4", host]
    else:
        comando = ["ping", "-c", "4", host]

    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=10)
        salida = resultado.stdout

        # Procesar salida según sistema operativo
        latencias_lista = []
        if so == "windows":
            lineas = [line for line in salida.split("\n") if "Tiempo=" in line or "tiempo=" in line]
            for linea in lineas:
                partes = linea.split("Tiempo=" if "Tiempo=" in linea else "tiempo=")
                if len(partes) > 1:
                    tiempo = partes[1].split("ms")[0].strip()
                    latencias_lista.append(float(tiempo))
        else:
            lineas = [line for line in salida.split("\n") if "time=" in line]
            for linea in lineas:
                partes = linea.split("time=")
                if len(partes) > 1:
                    tiempo = partes[1].split(" ")[0]
                    latencias_lista.append(float(tiempo))

        if latencias_lista:
            promedio = sum(latencias_lista) / len(latencias_lista)
            latencias[host] = promedio  # Guardamos latencia globalmente
            print(f"Latencia promedio a {host}: {promedio:.2f} ms")
            return promedio
        else:
            print(f"No se pudo obtener latencia para {host}")
            return None

    except subprocess.TimeoutExpired:
        print(f"Tiempo de espera agotado para {host}")
        return None
    except Exception as e:
        print(f"Error midiendo latencia en {host}: {e}")
        return None

# Función para medir ancho de banda con speedtest-cli
def medir_ancho_de_banda():
    try:
        speed = st.Speedtest()
        speed.get_best_server()
        download_speed = speed.download() / 1e6  # Mbps
        upload_speed = speed.upload() / 1e6  # Mbps
        return download_speed, upload_speed
    except Exception as e:
        print(f"Error midiendo ancho de banda: {e}")
        return None

# Función para construir el grafo
# Función para construir el grafo
def grafo():
    g = ig.Graph()
    g.add_vertices(len(hosts))
    edges = [(i, j) for i in range(len(hosts)) for j in range(i + 1, len(hosts))]
    g.add_edges(edges)
    g.vs["label"] = hosts
    edge_labels = []
    edge_weights = []
    for i, j in edges:
        host_i = hosts[i]
        host_j = hosts[j]
        if host_i in latencias and host_j in latencias:
            promedio = (latencias[host_i] + latencias[host_j]) / 2
            label = f"{promedio:.1f} ms"
            weight = promedio
        else:
            label = "N/A"
            weight = 0  # Peso nulo si no hay datos
        edge_labels.append(label)
        edge_weights.append(weight)
    g.es["label"] = edge_labels
    g.es["weight"] = edge_weights
    layout = g.layout("circle")
    # Mostrar el grafo con latencias como etiquetas de arista
    ig.plot(
        g,
        target="grafo_red.png",
        layout=layout,
        vertex_size=40,
        vertex_color="skyblue",
        vertex_label=g.vs["label"],
        edge_color="gray",
        edge_label=g.es["label"],
        edge_width=[1 + (w / 10 if w else 1) for w in g.es["weight"]],  # Grosor opcional según latencia
        bbox=(700, 700),
        margin=60
    )
# Medir latencia para cada host
for host in hosts:
    medir_latencia(host)

resultado = medir_ancho_de_banda()
if resultado:
    print(f"Ancho de banda: {resultado[0]:.1f} Mbps (descarga), {resultado[1]:.1f} Mbps (subida)")

grafo()