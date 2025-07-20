<center>
<h1 style="color: #2ecc71; font-size: 48px;">Proyecto transferencia optima por Vpn</h1>

<img height="600" width ="750" src="https://github.com/user-attachments/assets/2280b2e9-b774-493e-a314-c03ae2b4481e"><br>
⚙️ ¿Cómo funciona?

1. **Conexión VPN:** Todos los dispositivos deben estar conectados por una red privada (ej. ZeroTier).
2. **Medición de latencias:** Se usa `ping` para obtener la latencia entre cada par de nodos.
3. **Creación del grafo:** Cada nodo es un dispositivo y cada conexión es una arista con peso basado en la latencia.
4. **Optimización:**
   - 🧭 *Dijkstra:* Encuentra la ruta más rápida entre dos nodos.
   - 🌳 *Kruskal:* Construye el árbol más eficiente que conecta todos los nodos.
5. **Visualización:** Se genera un grafo con rutas resaltadas y detalles de latencias.
<br>
<img width="839" height="431" alt="image" src="https://github.com/user-attachments/assets/d7d303fe-6f19-471c-a841-124b5dedda69" /><br>
<img width="836" height="430" alt="image" src="https://github.com/user-attachments/assets/7128ad45-7a0c-430d-8895-3ed59f96a142" /><br>

Todos los archivos fuente se encuentran en la carpeta `src/`. A continuación, una breve descripción de cada uno:

- `app_dijkstra.py`: Interfaz gráfica e implementación del algoritmo de Dijkstra para optimización de rutas entre nodos.
- `app_kruskal.py`: Interfaz gráfica e implementación del algoritmo de Kruskal para optimización de conexiones en la red.
- `menu_principal.py`: Pantalla de inicio desde donde se accede a las dos aplicaciones anteriores.
- `network.py`: Script experimental para medir latencias mediante IPs privadas. Aunque no se invoca directamente, parte de su lógica está integrada en los otros módulos.
<br>
<h1 style="color: #2ecc71; font-size: 28px;">Requisitos para la  instalacion  y ejecucion del proyecto</h1>

- ZeroTier instalado y configurado en todos los servidores
- Una carpeta compartida llamada "ZT_Share" en cada servidor (C:\ZT_Share)
- Permisos SMB correctamente configurados
-Firewall con el puerto 445 (SMB) abierto entre los nodos

Librerias que debes de instalar
- CustomTkinter (interfaz gráfica)
- NetworkX
- Matplotlib
- speedtest-cli (ancho de banda)

</center>

