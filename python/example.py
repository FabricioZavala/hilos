import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DishPipelineApp:
    def __init__(self, root):
        self.root = root
        root.title("Simulador de Pipeline de Platos")
        root.geometry("800x600")
        
        # Estilo
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10, "bold"))
        style.configure("TLabel", font=("Arial", 10))
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        
        # Variables
        self.NUM_DISHES = 5
        self.washed = 0
        self.dried = 0
        self.stored = 0
        self.execution_history = []
        self.cpu_usage = []
        self.time_points = []
        
        # Queues entre etapas
        self.q_wash_to_dry = queue.Queue()
        self.q_dry_to_store = queue.Queue()
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame izquierdo para controles
        left_frame = ttk.Frame(main_frame, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Título de la simulación
        title_lbl = ttk.Label(left_frame, text="Pipeline de Procesamiento de Platos", style="Title.TLabel")
        title_lbl.pack(pady=(0, 20))
        
        # Configuración
        config_frame = ttk.LabelFrame(left_frame, text="Configuración", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(config_frame, text="Cantidad de platos:").pack(anchor=tk.W)
        
        self.dishes_var = tk.StringVar(value="5")
        self.dishes_entry = ttk.Spinbox(config_frame, from_=1, to=20, textvariable=self.dishes_var, width=5)
        self.dishes_entry.pack(anchor=tk.W, pady=(0, 10))
        
        # Indicadores de proceso
        process_frame = ttk.LabelFrame(left_frame, text="Estado del Proceso", padding="10")
        process_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_wash = ttk.Label(process_frame, text="Lavados: 0")
        self.lbl_dry = ttk.Label(process_frame, text="Secados: 0")
        self.lbl_store = ttk.Label(process_frame, text="Guardados: 0")
        self.lbl_time = ttk.Label(process_frame, text="Tiempo: 0.00s")
        self.lbl_cpu = ttk.Label(process_frame, text="CPU: 0.0%")
        
        self.lbl_wash.pack(anchor=tk.W, pady=2)
        self.lbl_dry.pack(anchor=tk.W, pady=2)
        self.lbl_store.pack(anchor=tk.W, pady=2)
        self.lbl_time.pack(anchor=tk.W, pady=2)
        self.lbl_cpu.pack(anchor=tk.W, pady=2)
        
        # Controles
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(pady=10)
        
        self.btn_start = ttk.Button(control_frame, text="Iniciar Pipeline", command=self.start_pipeline)
        self.btn_reset = ttk.Button(control_frame, text="Reiniciar", command=self.reset_simulation, state="disabled")
        
        self.btn_start.grid(row=0, column=0, padx=5)
        self.btn_reset.grid(row=0, column=1, padx=5)
        
        # Frame derecho para gráficas y resultados
        right_frame = ttk.Frame(main_frame, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Espacio para la gráfica
        self.graph_frame = ttk.LabelFrame(right_frame, text="Uso de CPU en Tiempo Real", padding="10")
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Historial de ejecuciones
        history_frame = ttk.LabelFrame(right_frame, text="Historial de Ejecuciones", padding="10")
        history_frame.pack(fill=tk.X, expand=False, pady=(10, 0))
        
        self.history_text = tk.Text(history_frame, height=6, width=40)
        self.history_text.pack(fill=tk.BOTH, expand=True)
        self.history_text.config(state="disabled")
        
        # Preparar gráfico
        self.setup_graph()
        
        # Mostrar explicación
        self.show_help_info()
    
    def setup_graph(self):
        self.figure, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel('Tiempo (s)')
        self.ax.set_ylabel('CPU (%)')
        self.ax.set_title('Uso de CPU')
        self.ax.grid(True)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_help_info(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Información sobre Hilos")
        help_window.geometry("500x300")
        
        info_text = """
        # Simulador de Pipeline con Hilos

        Esta aplicación demuestra el uso de hilos (threads) en Python para:
        
        1. **Paralelismo**: Cada etapa del proceso (lavar, secar, guardar) 
           se ejecuta en un hilo separado.
        
        2. **Sincronización**: Las colas (Queues) permiten la comunicación 
           segura entre hilos.
        
        3. **Comunicación entre procesos**: Los datos fluyen de un hilo a otro 
           de forma ordenada.
        
        La gráfica muestra el uso de CPU para visualizar cómo los hilos 
        consumen recursos del sistema mientras se ejecutan concurrentemente.
        """
        
        help_text = tk.Text(help_window, wrap=tk.WORD, padx=15, pady=15)
        help_text.pack(fill=tk.BOTH, expand=True)
        help_text.insert(tk.END, info_text)
        help_text.config(state="disabled")
    
    def start_pipeline(self):
        self.NUM_DISHES = int(self.dishes_var.get())
        self.btn_start.config(state="disabled")
        self.btn_reset.config(state="disabled")
        
        # Reiniciar contadores
        self.washed = 0
        self.dried = 0
        self.stored = 0
        
        # Limpiar colas por si acaso
        while not self.q_wash_to_dry.empty():
            self.q_wash_to_dry.get()
        while not self.q_dry_to_store.empty():
            self.q_dry_to_store.get()
            
        # Resetear gráfica
        self.cpu_usage = []
        self.time_points = []
        self.ax.clear()
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel('Tiempo (s)')
        self.ax.set_ylabel('CPU (%)')
        self.ax.set_title('Uso de CPU durante el Pipeline')
        self.ax.grid(True)
        
        self.start_time = time.time()
        
        # Iniciar hilos
        threading.Thread(target=self.washer, daemon=True).start()
        threading.Thread(target=self.dryer, daemon=True).start()
        threading.Thread(target=self.storer, daemon=True).start()
        
        # Iniciar monitoreo
        self.update_clock()
        self.monitor_cpu()
    
    def washer(self):
        for i in range(self.NUM_DISHES):
            time.sleep(1)  # Simula lavar un plato
            self.washed += 1
            self.q_wash_to_dry.put("plato")
            self.lbl_wash.config(text=f"Lavados: {self.washed}")
    
    def dryer(self):
        for _ in range(self.NUM_DISHES):
            self.q_wash_to_dry.get()  # Espera un plato lavado
            time.sleep(1.2)  # Simula secar plato (un poco más lento)
            self.dried += 1
            self.q_dry_to_store.put("plato")
            self.lbl_dry.config(text=f"Secados: {self.dried}")
    
    def storer(self):
        for _ in range(self.NUM_DISHES):
            self.q_dry_to_store.get()  # Espera un plato seco
            time.sleep(0.8)  # Simula guardar plato (un poco más rápido)
            self.stored += 1
            self.lbl_store.config(text=f"Guardados: {self.stored}")
    
    def update_clock(self):
        elapsed = time.time() - self.start_time
        self.lbl_time.config(text=f"Tiempo: {elapsed:.2f}s")
        
        if self.stored < self.NUM_DISHES:
            # Sigue actualizando mientras no termine
            self.root.after(100, self.update_clock)
        else:
            final_time = elapsed
            # Añadir al historial
            self.btn_reset.config(state="normal")
            self.lbl_time.config(text=f"¡Finalizado en {final_time:.2f}s!")
            
            # Actualizar historial
            self.execution_history.append(
                f"Ejecución: {len(self.execution_history)+1} - {self.NUM_DISHES} platos en {final_time:.2f}s"
            )
            self.update_history_text()
    
    def monitor_cpu(self):
        if self.stored < self.NUM_DISHES:
            cpu = psutil.cpu_percent()
            self.lbl_cpu.config(text=f"CPU: {cpu:.1f}%")
            
            # Actualizar gráfica
            elapsed = time.time() - self.start_time
            self.time_points.append(elapsed)
            self.cpu_usage.append(cpu)
            
            self.ax.clear()
            self.ax.set_ylim(0, 100)
            self.ax.plot(self.time_points, self.cpu_usage, 'b-')
            self.ax.set_xlabel('Tiempo (s)')
            self.ax.set_ylabel('CPU (%)')
            self.ax.set_title('Uso de CPU durante el Pipeline')
            self.ax.grid(True)
            self.canvas.draw()
            
            # Seguir monitoreando
            self.root.after(500, self.monitor_cpu)
    
    def update_history_text(self):
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        for entry in self.execution_history:
            self.history_text.insert(tk.END, entry + "\n")
        self.history_text.config(state="disabled")
    
    def reset_simulation(self):
        # Reiniciar contadores visualmente
        self.lbl_wash.config(text="Lavados: 0")
        self.lbl_dry.config(text="Secados: 0")
        self.lbl_store.config(text="Guardados: 0")
        self.lbl_time.config(text="Tiempo: 0.00s")
        self.lbl_cpu.config(text="CPU: 0.0%")
        
        # Habilitar inicio
        self.btn_start.config(state="normal")
        self.btn_reset.config(state="disabled")

if __name__ == "__main__":
    # Se requiere instalar: matplotlib, psutil
    # pip install matplotlib psutil
    root = tk.Tk()
    app = DishPipelineApp(root)
    root.mainloop()
