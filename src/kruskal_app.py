import customtkinter as ctk
import subprocess
import platform
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import speedtest as st
import threading
import os
import sys
import igraph as ig
from tkinter import ttk, messagebox

class KruskalApp(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.hosts = []
        self.latencias = {}
        self.running = False
        
        self.create_widgets()
        self.bind("<Configure>", self.on_resize)
    
    def create_widgets(self):
        # Configurar grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Frame superior
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        top_frame.grid_columnconfigure(0, weight=1)
        
        # Entrada de hosts
        self.hosts_label = ctk.CTkLabel(top_frame, text="Hosts (IPs separadas por comas):")
        self.hosts_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.hosts_entry = ctk.CTkEntry(top_frame)
        self.hosts_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.hosts_entry.insert(0, "172.29.150.87, 172.29.5.37, 172.29.130.128, 172.29.127.70, 172.29.42.70, 172.29.155.85")
        
        # Botones
        button_frame = ctk.CTkFrame(top_frame)
        button_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        self.analyze_button = ctk.CTkButton(
            button_frame, 
            text="Analizar Red", 
            command=self.start_analysis
        )
        self.analyze_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(
            button_frame, 
            text="Detener", 
            command=self.stop_analysis,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)
        
        self.progress = ctk.CTkProgressBar(top_frame, orientation="horizontal", mode="indeterminate")
        self.progress.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        # Pestañas de resultados
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")
        self.tabview.add("Consola")
        self.tabview.add("Resultados")
        
        # Consola
        self.console = ctk.CTkTextbox(self.tabview.tab("Consola"), wrap="word")
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para resultados
        results_frame = ctk.CTkFrame(self.tabview.tab("Resultados"))
        results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Gráficos
        self.graph_frame = ctk.CTkFrame(results_frame)
        self.graph_frame.pack(fill="both", expand=True, pady=(0,10), padx=10)
        
        # Configurar grid para gráficos
        self.graph_frame.grid_columnconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(1, weight=1)
        self.graph_frame.grid_rowconfigure(1, weight=1)
        
        # Títulos
        self.original_graph_label = ctk.CTkLabel(self.graph_frame, text="Topología Original")
        self.original_graph_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.mst_graph_label = ctk.CTkLabel(self.graph_frame, text="Árbol de Expansión Mínima")
        self.mst_graph_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Frame contenedor para canvas con scroll (Original)
        original_frame = ctk.CTkFrame(self.graph_frame)
        original_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Scrollbars para original
        original_scroll_x = ttk.Scrollbar(original_frame, orient="horizontal")
        original_scroll_y = ttk.Scrollbar(original_frame, orient="vertical")
        
        self.original_canvas = ctk.CTkCanvas(
            original_frame,
            bg="#2b2b2b",
            width=500,
            height=400,
            xscrollcommand=original_scroll_x.set,
            yscrollcommand=original_scroll_y.set,
            highlightthickness=0
        )
        
        original_scroll_x.config(command=self.original_canvas.xview)
        original_scroll_y.config(command=self.original_canvas.yview)
        
        # Grid layout para canvas original
        self.original_canvas.grid(row=0, column=0, sticky="nsew")
        original_scroll_y.grid(row=0, column=1, sticky="ns")
        original_scroll_x.grid(row=1, column=0, sticky="ew")
        
        original_frame.grid_rowconfigure(0, weight=1)
        original_frame.grid_columnconfigure(0, weight=1)
        
        # Frame contenedor para canvas con scroll (MST)
        mst_frame = ctk.CTkFrame(self.graph_frame)
        mst_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Scrollbars para MST
        mst_scroll_x = ttk.Scrollbar(mst_frame, orient="horizontal")
        mst_scroll_y = ttk.Scrollbar(mst_frame, orient="vertical")
        
        self.mst_canvas = ctk.CTkCanvas(
            mst_frame,
            bg="#2b2b2b",
            width=500,
            height=400,
            xscrollcommand=mst_scroll_x.set,
            yscrollcommand=mst_scroll_y.set,
            highlightthickness=0
        )
        
        mst_scroll_x.config(command=self.mst_canvas.xview)
        mst_scroll_y.config(command=self.mst_canvas.yview)
        
        # Grid layout para canvas MST
        self.mst_canvas.grid(row=0, column=0, sticky="nsew")
        mst_scroll_y.grid(row=0, column=1, sticky="ns")
        mst_scroll_x.grid(row=1, column=0, sticky="ew")
        
        mst_frame.grid_rowconfigure(0, weight=1)
        mst_frame.grid_columnconfigure(0, weight=1)
        
        # Comparación
        self.comparison_label = ctk.CTkLabel(results_frame, text="Comparación de Topologías")
        self.comparison_label.pack(pady=(10,5))
        
        # Frame para comparación con scroll horizontal
        comparison_frame = ctk.CTkFrame(results_frame)
        comparison_frame.pack(fill="x", pady=(0,10))
        
        comparison_scroll_x = ttk.Scrollbar(comparison_frame, orient="horizontal")
        comparison_scroll_x.pack(side="bottom", fill="x")
        
        self.comparison_canvas = ctk.CTkCanvas(
            comparison_frame,
            bg="#2b2b2b",
            width=800,
            height=200,
            xscrollcommand=comparison_scroll_x.set,
            highlightthickness=0
        )
        self.comparison_canvas.pack(side="top", fill="both", expand=True)
        comparison_scroll_x.config(command=self.comparison_canvas.xview)
        
        # Estadísticas
        self.stats_text = ctk.CTkTextbox(results_frame, wrap="word", height=150)
        self.stats_text.pack(fill="both", expand=True)
    
    def write(self, text):
        """Redirige la salida estándar al widget de consola."""
        self.console.insert("end", text)
        self.console.see("end")
        self.update()
    
    def flush(self):
        """Método necesario para redirección de stdout."""
        pass
    
    def start_analysis(self):
        """Inicia el análisis de la red."""
        raw_hosts = self.hosts_entry.get().strip()
        if not raw_hosts:
            self.print_to_console("Error: Por favor ingresa al menos un host para analizar.\n")
            return
        
        self.hosts = [h.strip() for h in raw_hosts.split(",")]
        self.latencias = {}
        self.console.delete("1.0", "end")
        self.stats_text.delete("1.0", "end")
        
        # Redirigir salida estándar
        self.old_stdout = sys.stdout
        sys.stdout = self
        
        # Actualizar UI
        self.analyze_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress.start()
        self.running = True
        
        # Iniciar análisis en un hilo separado
        self.analysis_thread = threading.Thread(target=self.run_analysis)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def stop_analysis(self):
        """Detiene el análisis en curso."""
        if self.running:
            self.running = False
            self.print_to_console("\nAnálisis detenido por el usuario.\n")
            self.reset_ui_after_analysis()
    
    def reset_ui_after_analysis(self):
        """Restablece la UI después del análisis."""
        self.progress.stop()
        self.analyze_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        sys.stdout = self.old_stdout
    
    def print_to_console(self, text):
        """Imprime texto en la consola."""
        self.console.insert("end", text)
        self.console.see("end")
        self.update()
    
    def on_resize(self, event):
        """Redimensiona los gráficos cuando cambia el tamaño de la ventana."""
        if hasattr(self, 'img_original_tk') and hasattr(self, 'img_mst_tk'):
            self.update_graphs()
    
    def medir_latencia(self, host):
        """Mide la latencia a un host usando ping."""
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
                self.latencias[host] = promedio
                print(f"Latencia promedio a {host}: {promedio:.2f} ms\n")
                return promedio
            else:
                print(f"No se pudo obtener latencia para {host}\n")
                return None

        except subprocess.TimeoutExpired:
            print(f"Tiempo de espera agotado para {host}\n")
            return None
        except Exception as e:
            print(f"Error midiendo latencia en {host}: {e}\n")
            return None
            
    def medir_ancho_de_banda(self):
        """Mide el ancho de banda usando speedtest-cli."""
        try:
            speed = st.Speedtest()
            speed.get_best_server()
            download_speed = speed.download() / 1e6  # Mbps
            upload_speed = speed.upload() / 1e6  # Mbps
            return download_speed, upload_speed
        except Exception as e:
            print(f"Error midiendo ancho de banda: {e}\n")
            return None
            
    def grafo_original(self):
        """Construye el grafo completo original."""
        g = ig.Graph()
        g.add_vertices(len(self.hosts))
        edges = [(i, j) for i in range(len(self.hosts)) for j in range(i + 1, len(self.hosts))]
        g.add_edges(edges)
        g.vs["label"] = self.hosts
        
        # Calculamos matriz de latencias entre cada par de hosts
        matriz_latencias = np.zeros((len(self.hosts), len(self.hosts)))
        edge_labels = []
        edge_weights = []
        
        for i, j in edges:
            host_i = self.hosts[i]
            host_j = self.hosts[j]
            if host_i in self.latencias and host_j in self.latencias:
                latencia_estimada = (self.latencias[host_i] + self.latencias[host_j]) / 2
                matriz_latencias[i][j] = matriz_latencias[j][i] = latencia_estimada
                label = f"{latencia_estimada:.1f} ms"
                weight = latencia_estimada
            else:
                label = "N/A"
                weight = 0  # Peso nulo si no hay datos
            edge_labels.append(label)
            edge_weights.append(weight)
        
        g.es["label"] = edge_labels
        g.es["weight"] = edge_weights
        
        # Calculamos el peso total de la topología completa
        peso_total_original = sum(edge_weights)
        
        # Usar layout kamada-kawai para mejor distribución
        layout = g.layout("kk")
        
        # Configuración de visualización mejorada
        visual_style = {
            "vertex_size": 30,
            "vertex_color": "lightblue",
            "vertex_label": g.vs["label"],
            "vertex_label_size": 10,
            "vertex_label_dist": 1.8,
            "edge_color": "gray",
            "edge_label": g.es["label"],
            "edge_label_size": 8,
            "edge_width": [0.5 + (w / 20 if w else 0.5) for w in g.es["weight"]],
            "edge_curved": 0.2,
            "layout": layout,
            "bbox": (1200, 1200),
            "margin": 100,
            "autocurve": True
        }
        
        # Generar imagen con alta resolución
        ig.plot(
            g,
            target="grafo_red_original.png",
            **visual_style
        )
        
        return g, matriz_latencias, peso_total_original
        
    def kruskal(self, matriz_latencias, num_nodos):
        """Implementación del algoritmo de Kruskal para MST."""
        aristas = []
        for i in range(num_nodos):
            for j in range(i+1, num_nodos):
                if matriz_latencias[i][j] > 0:
                    aristas.append((i, j, matriz_latencias[i][j]))
        
        aristas.sort(key=lambda x: x[2])
        
        padres = list(range(num_nodos))
        
        def encontrar(x):
            if padres[x] != x:
                padres[x] = encontrar(padres[x])
            return padres[x]
        
        def unir(x, y):
            padres[encontrar(x)] = encontrar(y)
        
        mst = []
        for u, v, peso in aristas:
            if encontrar(u) != encontrar(v):
                unir(u, v)
                mst.append((u, v, peso))
        
        return mst
        
    def grafo_kruskal(self, matriz_latencias):
        """Visualiza el MST generado por Kruskal."""
        num_nodos = len(self.hosts)
        mst = self.kruskal(matriz_latencias, num_nodos)
        
        g = ig.Graph()
        g.add_vertices(num_nodos)
        g.vs["label"] = self.hosts
        
        edges = []
        edge_labels = []
        edge_weights = []
        
        for u, v, peso in mst:
            edges.append((u, v))
            edge_labels.append(f"{peso:.1f} ms")
            edge_weights.append(peso)
        
        g.add_edges(edges)
        g.es["label"] = edge_labels
        g.es["weight"] = edge_weights
        
        peso_total_mst = sum(edge_weights)
        
        # Usar layout circular para MST
        layout = g.layout("circle")
        
        # Configuración de visualización mejorada
        visual_style = {
            "vertex_size": 35,
            "vertex_color": "lightgreen",
            "vertex_label": g.vs["label"],
            "vertex_label_size": 11,
            "vertex_label_dist": 1.8,
            "edge_color": "blue",
            "edge_label": g.es["label"],
            "edge_label_size": 9,
            "edge_width": [1 + (w / 15 if w else 1) for w in g.es["weight"]],
            "edge_curved": 0.1,
            "layout": layout,
            "bbox": (1200, 1200),
            "margin": 100,
            "autocurve": True
        }
        
        # Generar imagen con alta resolución
        ig.plot(
            g,
            target="grafo_red_kruskal.png",
            **visual_style
        )
        
        return g, peso_total_mst, mst
        
    def comparar_topologias(self, peso_original, peso_kruskal, mst):
        """Compara ambas topologías."""
        reduccion_porcentaje = ((peso_original - peso_kruskal) / peso_original) * 100
        
        plt.figure(figsize=(12, 6))
        plt.bar(['Topología Original', 'MST (Kruskal)'], [peso_original, peso_kruskal], color=['gray', 'green'])
        plt.title('Comparación de Latencia Total entre Topologías', pad=20)
        plt.ylabel('Suma de Latencias (ms)')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        for i, v in enumerate([peso_original, peso_kruskal]):
            plt.text(i, v + 5, f"{v:.1f} ms", ha='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig("comparacion_topologias.png", dpi=120)
        plt.close()
        
        print("\n--- COMPARACIÓN DE TOPOLOGÍAS ---\n")
        print(f"Peso total de la topología original: {peso_original:.2f} ms\n")
        print(f"Peso total del MST (Kruskal): {peso_kruskal:.2f} ms\n")
        print(f"Reducción de latencia: {reduccion_porcentaje:.2f}%\n")
        
        # Mostrar en la interfaz
        resultado = f"--- COMPARACIÓN DE TOPOLOGÍAS ---\n"
        resultado += f"Peso total de la topología original: {peso_original:.2f} ms\n"
        resultado += f"Peso total del MST (Kruskal): {peso_kruskal:.2f} ms\n"
        resultado += f"Reducción de latencia: {reduccion_porcentaje:.2f}%\n\n"
        resultado += "Conexiones en la topología optimizada:\n"
        
        print("\nConexiones en la topología optimizada:\n")
        for u, v, peso in mst:
            linea = f"  {self.hosts[u]} -- {self.hosts[v]} : {peso:.2f} ms\n"
            print(linea)
            resultado += linea
            
        self.stats_text.insert("end", resultado)
        self.stats_text.see("end")
        self.update()

    def update_graphs(self):
        """Actualiza los gráficos en la interfaz."""
        try:
            # Tamaños base para los canvas
            graph_width = 500
            graph_height = 400
            comparison_height = 200
            
            # Cargar y mostrar el grafo original
            if os.path.exists("grafo_red_original.png"):
                img_original = Image.open("grafo_red_original.png")
                
                # Calcular relación de aspecto
                original_ratio = img_original.width / img_original.height
                new_width = int(graph_height * original_ratio)
                new_height = graph_height
                
                # Redimensionar manteniendo aspecto
                img_original = img_original.resize(
                    (new_width, new_height), 
                    Image.LANCZOS
                )
                
                # Actualizar canvas
                self.original_canvas.config(
                    width=min(new_width, graph_width),
                    height=new_height,
                    scrollregion=(0, 0, new_width, new_height)
                )
                self.original_canvas.delete("all")
                
                self.img_original_tk = ImageTk.PhotoImage(img_original)
                self.original_canvas.create_image(0, 0, image=self.img_original_tk, anchor="nw")
            
            # Cargar y mostrar el grafo MST
            if os.path.exists("grafo_red_kruskal.png"):
                img_mst = Image.open("grafo_red_kruskal.png")
                
                mst_ratio = img_mst.width / img_mst.height
                new_width = int(graph_height * mst_ratio)
                new_height = graph_height
                
                img_mst = img_mst.resize(
                    (new_width, new_height), 
                    Image.LANCZOS
                )
                
                self.mst_canvas.config(
                    width=min(new_width, graph_width),
                    height=new_height,
                    scrollregion=(0, 0, new_width, new_height)
                )
                self.mst_canvas.delete("all")
                
                self.img_mst_tk = ImageTk.PhotoImage(img_mst)
                self.mst_canvas.create_image(0, 0, image=self.img_mst_tk, anchor="nw")
            
            # Cargar y mostrar la comparación
            if os.path.exists("comparacion_topologias.png"):
                img_comparison = Image.open("comparacion_topologias.png")
                
                comparison_ratio = img_comparison.width / img_comparison.height
                new_width = int(comparison_height * comparison_ratio)
                new_height = comparison_height
                
                img_comparison = img_comparison.resize(
                    (new_width, new_height), 
                    Image.LANCZOS
                )
                
                self.comparison_canvas.config(
                    scrollregion=(0, 0, new_width, new_height)
                )
                self.comparison_canvas.delete("all")
                
                self.img_comparison_tk = ImageTk.PhotoImage(img_comparison)
                self.comparison_canvas.create_image(0, 0, image=self.img_comparison_tk, anchor="nw")
                
            # Cambiar a la pestaña de resultados
            self.tabview.set("Resultados")
            
        except Exception as e:
            print(f"Error al cargar imágenes: {e}\n")
            # Mostrar mensaje de error en los canvas
            self.original_canvas.delete("all")
            self.original_canvas.create_text(
                150, 100, 
                text="Error cargando imagen", 
                fill="white", 
                font=("Arial", 12)
            )
            
            self.mst_canvas.delete("all")
            self.mst_canvas.create_text(
                150, 100, 
                text="Error cargando imagen", 
                fill="white", 
                font=("Arial", 12)
            )

    def run_analysis(self):
        """Ejecuta el análisis completo de la red."""
        try:
            # Paso 1: Medir latencias para cada host
            print("Midiendo latencias...\n")
            for host in self.hosts:
                if not self.running:
                    return
                self.medir_latencia(host)
            
            # Paso 2: Medir ancho de banda
            if not self.running:
                return
            print("\nMidiendo ancho de banda...\n")
            resultado = self.medir_ancho_de_banda()
            if resultado:
                print(f"Ancho de banda: {resultado[0]:.1f} Mbps (descarga), {resultado[1]:.1f} Mbps (subida)\n")
            
            # Paso 3: Generar y visualizar el grafo original
            if not self.running:
                return
            print("\nGenerando grafo original...\n")
            grafo_orig, matriz_latencias, peso_original = self.grafo_original()
            
            # Paso 4: Aplicar Kruskal para obtener MST
            if not self.running:
                return
            print("\nAplicando algoritmo de Kruskal...\n")
            grafo_mst, peso_kruskal, mst = self.grafo_kruskal(matriz_latencias)
            
            # Paso 5: Comparar topologías
            if not self.running:
                return
            self.comparar_topologias(peso_original, peso_kruskal, mst)
            
            print("\nAnálisis completado.\n")
            
            # Mostrar imágenes en la interfaz
            self.after(100, self.update_graphs)
            
        except Exception as e:
            print(f"\nError durante el análisis: {e}\n")
        finally:
            self.after(100, self.reset_ui_after_analysis)