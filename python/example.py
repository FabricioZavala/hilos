import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class AplicacionPipelinePlatos:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Simulador de lavado de Platos")
        raiz.geometry("900x700")
        
        # estiloss
        estilo = ttk.Style()
        estilo.configure("TButton", font=("Arial", 10, "bold"))
        estilo.configure("TLabel", font=("Arial", 10))
        estilo.configure("Title.TLabel", font=("Arial", 12, "bold"))
        
        # Variables utilizadas
        self.NUMERO_PLATOS = 5
        self.lavados = 0
        self.secados = 0
        self.guardados = 0
        self.historial_ejecuciones = []
        self.uso_cpu = []
        self.puntos_tiempo = []
        self.registros_log = [] 
        
        # Estas colas nos sirven para pasar los platos de una etapa a otra
        self.cola_lavar_a_secar = queue.Queue()
        self.cola_secar_a_guardar = queue.Queue()
        
        # Panel principal 
        marco_principal = ttk.Frame(raiz, padding="10")
        marco_principal.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo para los controles y configuración
        panel_izquierdo = ttk.Frame(marco_principal, padding="10")
        panel_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Título del programa
        etiqueta_titulo = ttk.Label(panel_izquierdo, text="Simulador de lavadps de Platos", style="Title.TLabel")
        etiqueta_titulo.pack(pady=(0, 20))
        
        # Sección donde configuramos cuántos platos queremos procesar
        marco_config = ttk.LabelFrame(panel_izquierdo, text="Configuración", padding="10")
        marco_config.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(marco_config, text="Cantidad de platos:").pack(anchor=tk.W)
        
        self.var_platos = tk.StringVar(value="5")
        self.entrada_platos = ttk.Spinbox(marco_config, from_=1, to=20, textvariable=self.var_platos, width=5)
        self.entrada_platos.pack(anchor=tk.W, pady=(0, 10))
        
        # Sección que muestra el progreso del lavado, secado y guardado
        marco_proceso = ttk.LabelFrame(panel_izquierdo, text="Estado del Proceso", padding="10")
        marco_proceso.pack(fill=tk.X, pady=(0, 10))
        
        self.etq_lavado = ttk.Label(marco_proceso, text="Lavados: 0")
        self.etq_secado = ttk.Label(marco_proceso, text="Secados: 0")
        self.etq_guardado = ttk.Label(marco_proceso, text="Guardados: 0")
        self.etq_tiempo = ttk.Label(marco_proceso, text="Tiempo: 0.00s")
        self.etq_cpu = ttk.Label(marco_proceso, text="CPU: 0.0%")
        
        self.etq_lavado.pack(anchor=tk.W, pady=2)
        self.etq_secado.pack(anchor=tk.W, pady=2)
        self.etq_guardado.pack(anchor=tk.W, pady=2)
        self.etq_tiempo.pack(anchor=tk.W, pady=2)
        self.etq_cpu.pack(anchor=tk.W, pady=2)
        
        # Botones para iniciar y reiniciar la simulación
        marco_control = ttk.Frame(panel_izquierdo)
        marco_control.pack(pady=10)
        
        self.boton_iniciar = ttk.Button(marco_control, text="Iniciar", command=self.iniciar_simulacion)
        self.boton_reiniciar = ttk.Button(marco_control, text="Reiniciar", command=self.reiniciar_simulacion, state="disabled")
        
        self.boton_iniciar.grid(row=0, column=0, padx=5)
        self.boton_reiniciar.grid(row=0, column=1, padx=5)
        
        # Panel derecho para la gráfica, el historial y el log
        panel_derecho = ttk.Frame(marco_principal, padding="10")
        panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Espacio para mostrar la gráfica de uso del CPU
        self.marco_grafica = ttk.LabelFrame(panel_derecho, text="Uso de CPU en Tiempo Real", padding="10")
        self.marco_grafica.pack(fill=tk.BOTH, expand=True)
        
        # Logs de los hilossss
        marco_log = ttk.LabelFrame(panel_derecho, text="Log de Actividad de Hilos", padding="10")
        marco_log.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # scroll para el log
        frame_scroll_log = ttk.Frame(marco_log)
        frame_scroll_log.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_log = ttk.Scrollbar(frame_scroll_log)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.texto_log = tk.Text(frame_scroll_log, height=8, width=40)
        self.texto_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.texto_log.config(state="disabled", wrap=tk.WORD)        
        self.texto_log.config(yscrollcommand=scrollbar_log.set)
        scrollbar_log.config(command=self.texto_log.yview)
        
        # ejecuciones anteriores
        marco_historial = ttk.LabelFrame(panel_derecho, text="Historial de Ejecuciones", padding="10")
        marco_historial.pack(fill=tk.X, expand=False, pady=(10, 0))
        
        self.texto_historial = tk.Text(marco_historial, height=6, width=40)
        self.texto_historial.pack(fill=tk.BOTH, expand=True)
        self.texto_historial.config(state="disabled")
        
        # funcion para mostrar la grafica
        self.configurar_grafica()
    
    def configurar_grafica(self):
        self.figura, self.eje = plt.subplots(figsize=(5, 3))
        self.eje.set_ylim(0, 100)
        self.eje.set_xlabel('Tiempo (s)')
        self.eje.set_ylabel('CPU (%)')
        self.eje.set_title('Uso de CPU')
        self.eje.grid(True)
        
        self.lienzo = FigureCanvasTkAgg(self.figura, master=self.marco_grafica)
        self.lienzo.draw()
        self.lienzo.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def agregar_log(self, mensaje):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        mensaje_completo = f"[{timestamp}] {mensaje}"
        self.registros_log.append(mensaje_completo)
        
        self.texto_log.config(state="normal")
        self.texto_log.insert(tk.END, mensaje_completo + "\n")
        self.texto_log.see(tk.END)
        self.texto_log.config(state="disabled")
    
    def iniciar_simulacion(self):
        self.NUMERO_PLATOS = int(self.var_platos.get())
        self.boton_iniciar.config(state="disabled")
        self.boton_reiniciar.config(state="disabled")
        
        self.texto_log.config(state="normal")
        self.texto_log.delete(1.0, tk.END)
        self.texto_log.config(state="disabled")
        self.registros_log = []
        
        self.agregar_log(f"Iniciando simulación con {self.NUMERO_PLATOS} platos")
        
        # como es nueva simulación se reinician los contadores
        self.lavados = 0
        self.secados = 0
        self.guardados = 0
        
        # se vacian las colas
        while not self.cola_lavar_a_secar.empty():
            self.cola_lavar_a_secar.get()
        while not self.cola_secar_a_guardar.empty():
            self.cola_secar_a_guardar.get()
        
        self.agregar_log("Colas vacías y listas para comenzar")
            
        self.uso_cpu = []
        self.puntos_tiempo = []
        self.eje.clear()
        self.eje.set_ylim(0, 100)
        self.eje.set_xlabel('Tiempo (s)')
        self.eje.set_ylabel('CPU (%)')
        self.eje.set_title('Uso de CPU')
        self.eje.grid(True)
        
        # se guarda el tiempo de inicio de la simulación
        self.tiempo_inicio = time.time()

        self.agregar_log("Iniciando hilos de trabajo...")
        threading.Thread(name="Lavador", target=self.lavador, daemon=True).start()
        threading.Thread(name="Secador", target=self.secador, daemon=True).start()
        threading.Thread(name="Guardador", target=self.guardador, daemon=True).start()
        
        # Iniciamos las funciones que actualizan lo que vemos
        self.actualizar_reloj()
        self.monitorear_cpu()
    
    def lavador(self):
        id_hilo = threading.current_thread().name
        self.agregar_log(f"Hilo {id_hilo} iniciado - Lavará {self.NUMERO_PLATOS} platos")
        
        for i in range(self.NUMERO_PLATOS):
            self.agregar_log(f"{id_hilo}: Lavando plato #{i+1}...")
            time.sleep(1)
            self.lavados += 1
            self.cola_lavar_a_secar.put("plato")
            self.etq_lavado.config(text=f"Lavados: {self.lavados}")
            self.agregar_log(f"{id_hilo}: Plato #{i+1} lavado y enviado a secado")
        
        self.agregar_log(f"Hilo {id_hilo} completado - {self.lavados} platos lavados")
    
    def secador(self):
        id_hilo = threading.current_thread().name
        self.agregar_log(f"Hilo {id_hilo} iniciado - Esperando platos para secar")
        
        for i in range(self.NUMERO_PLATOS):
            self.agregar_log(f"{id_hilo}: Esperando plato #{i+1} para secar...")
            self.cola_lavar_a_secar.get()
            self.agregar_log(f"{id_hilo}: Plato #{i+1} recibido, secando...")
            time.sleep(1)
            self.secados += 1
            self.cola_secar_a_guardar.put("plato")
            self.etq_secado.config(text=f"Secados: {self.secados}")
            self.agregar_log(f"{id_hilo}: Plato #{i+1} secado y enviado a guardar")
        
        self.agregar_log(f"Hilo {id_hilo} completado - {self.secados} platos secados")
    
    def guardador(self):
        id_hilo = threading.current_thread().name
        self.agregar_log(f"Hilo {id_hilo} iniciado - Esperando platos para guardar")
        
        for i in range(self.NUMERO_PLATOS):
            self.agregar_log(f"{id_hilo}: Esperando plato #{i+1} para guardar...")
            self.cola_secar_a_guardar.get()
            self.agregar_log(f"{id_hilo}: Plato #{i+1} recibido, guardando...")
            time.sleep(0.8)
            self.guardados += 1
            self.etq_guardado.config(text=f"Guardados: {self.guardados}")
            self.agregar_log(f"{id_hilo}: Plato #{i+1} guardado correctamente")
        
        self.agregar_log(f"Hilo {id_hilo} completado - {self.guardados} platos guardados")
    
    def actualizar_reloj(self):
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        self.etq_tiempo.config(text=f"Tiempo: {tiempo_transcurrido:.2f}s")
        
        if self.guardados < self.NUMERO_PLATOS:
            self.raiz.after(100, self.actualizar_reloj)
        else:
            tiempo_final = tiempo_transcurrido
            self.boton_reiniciar.config(state="normal")
            self.etq_tiempo.config(text=f"¡Finalizado en {tiempo_final:.2f}s!")
            self.agregar_log(f"SIMULACIÓN COMPLETADA en {tiempo_final:.2f}s - Todos los platos procesados")
            
            self.historial_ejecuciones.append(
                f"Ejecución: {len(self.historial_ejecuciones)+1} - {self.NUMERO_PLATOS} platos en {tiempo_final:.2f}s"
            )
            self.actualizar_texto_historial()
    
    def monitorear_cpu(self):
        if self.guardados < self.NUMERO_PLATOS:
            uso = psutil.cpu_percent()
            self.etq_cpu.config(text=f"CPU: {uso:.1f}%")
            
            tiempo_transcurrido = time.time() - self.tiempo_inicio
            self.puntos_tiempo.append(tiempo_transcurrido)
            self.uso_cpu.append(uso)
            
            self.eje.clear()
            self.eje.set_ylim(0, 100)
            self.eje.plot(self.puntos_tiempo, self.uso_cpu, 'b-')
            self.eje.set_xlabel('Tiempo (s)')
            self.eje.set_ylabel('CPU (%)')
            self.eje.set_title('Uso de CPU ')
            self.eje.grid(True)
            self.lienzo.draw()
            
            self.raiz.after(500, self.monitorear_cpu)
    
    def actualizar_texto_historial(self):
        self.texto_historial.config(state="normal")
        self.texto_historial.delete(1.0, tk.END)
        for entrada in self.historial_ejecuciones:
            self.texto_historial.insert(tk.END, entrada + "\n")
        self.texto_historial.config(state="disabled")
    
    def reiniciar_simulacion(self):
        self.etq_lavado.config(text="Lavados: 0")
        self.etq_secado.config(text="Secados: 0")
        self.etq_guardado.config(text="Guardados: 0")
        self.etq_tiempo.config(text="Tiempo: 0.00s")
        self.etq_cpu.config(text="CPU: 0.0%")
        
        self.boton_iniciar.config(state="normal")
        self.boton_reiniciar.config(state="disabled")
        
        self.agregar_log("Simulación reiniciada - Sistema listo para una nueva ejecución")

if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacionPipelinePlatos(raiz)
    raiz.mainloop()
