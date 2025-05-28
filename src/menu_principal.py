import customtkinter as ctk
from tkinter import messagebox
from dijkstra_app import DijkstraApp
from kruskal_app import KruskalApp

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Herramientas de Optimización de Red")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Configurar layout principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Crear sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo y título
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="Herramientas de Red",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Botones del menú
        self.dijkstra_button = ctk.CTkButton(
            self.sidebar, 
            text="Optimizar Ruta (Dijkstra)", 
            command=self.show_dijkstra
        )
        self.dijkstra_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.kruskal_button = ctk.CTkButton(
            self.sidebar, 
            text="Árbol de Expansión (Kruskal)", 
            command=self.show_kruskal
        )
        self.kruskal_button.grid(row=2, column=0, padx=20, pady=10)
        
        # Botón de salida
        self.exit_button = ctk.CTkButton(
            self.sidebar, 
            text="Salir", 
            command=self.destroy,
            fg_color="#d9534f",
            hover_color="#c9302c"
        )
        self.exit_button.grid(row=5, column=0, padx=20, pady=20)
        
        # Frame principal para contenido
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Inicializar aplicaciones
        self.dijkstra_app = DijkstraApp(self.main_frame)
        self.kruskal_app = KruskalApp(self.main_frame)
        
        # Mostrar Dijkstra por defecto
        self.show_dijkstra()
    
    def show_dijkstra(self):
        self.kruskal_app.grid_forget()
        self.dijkstra_app.grid(row=0, column=0, sticky="nsew")
        self.dijkstra_button.configure(fg_color="#2b8cbe")
        self.kruskal_button.configure(fg_color=["#3a7ebf", "#1f538d"])
    
    def show_kruskal(self):
        self.dijkstra_app.grid_forget()
        self.kruskal_app.grid(row=0, column=0, sticky="nsew")
        self.kruskal_button.configure(fg_color="#2b8cbe")
        self.dijkstra_button.configure(fg_color=["#3a7ebf", "#1f538d"])

if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()