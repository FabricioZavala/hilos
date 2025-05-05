import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AplicacionPipelinePlatos:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Simulador de lavado de Platos")
        raiz.geometry("800x600")
        
        # Mejoramos el aspecto visual de los botones y textos
        estilo = ttk.Style()
        estilo.configure("TButton", font=("Arial", 10, "bold"))
        estilo.configure("TLabel", font=("Arial", 10))
        estilo.configure("Title.TLabel", font=("Arial", 12, "bold"))
        
        # Variables para llevar el control de nuestro proceso
        self.NUMERO_PLATOS = 5
        self.lavados = 0
        self.secados = 0
        self.guardados = 0
        self.historial_ejecuciones = []
        self.uso_cpu = []
        self.puntos_tiempo = []
        
        # Estas colas nos sirven para pasar los platos de una etapa a otra
        self.cola_lavar_a_secar = queue.Queue()
        self.cola_secar_a_guardar = queue.Queue()
        
        # Panel principal que contendrá toda la interfaz
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
        
        self.boton_iniciar = ttk.Button(marco_control, text="Iniciar", command=self.iniciar_pipeline)
        self.boton_reiniciar = ttk.Button(marco_control, text="Reiniciar", command=self.reiniciar_simulacion, state="disabled")
        
        self.boton_iniciar.grid(row=0, column=0, padx=5)
        self.boton_reiniciar.grid(row=0, column=1, padx=5)
        
        # Panel derecho para la gráfica y el historial
        panel_derecho = ttk.Frame(marco_principal, padding="10")
        panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Espacio para mostrar la gráfica de uso del CPU
        self.marco_grafica = ttk.LabelFrame(panel_derecho, text="Uso de CPU en Tiempo Real", padding="10")
        self.marco_grafica.pack(fill=tk.BOTH, expand=True)
        
        # Espacio para mostrar el historial de ejecuciones anteriores
        marco_historial = ttk.LabelFrame(panel_derecho, text="Historial de Ejecuciones", padding="10")
        marco_historial.pack(fill=tk.X, expand=False, pady=(10, 0))
        
        self.texto_historial = tk.Text(marco_historial, height=6, width=40)
        self.texto_historial.pack(fill=tk.BOTH, expand=True)
        self.texto_historial.config(state="disabled")
        
        # Preparamos la gráfica inicial que mostrará el uso de CPU
        self.configurar_grafica()
    
    def configurar_grafica(self):
        # Preparamos una gráfica vacía para mostrar después el uso de CPU
        self.figura, self.eje = plt.subplots(figsize=(5, 3))
        self.eje.set_ylim(0, 100)
        self.eje.set_xlabel('Tiempo (s)')
        self.eje.set_ylabel('CPU (%)')
        self.eje.set_title('Uso de CPU')
        self.eje.grid(True)
        
        # Colocamos la gráfica en la ventana
        self.lienzo = FigureCanvasTkAgg(self.figura, master=self.marco_grafica)
        self.lienzo.draw()
        self.lienzo.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def iniciar_pipeline(self):
        # Tomamos el número de platos que el usuario eligió
        self.NUMERO_PLATOS = int(self.var_platos.get())
        self.boton_iniciar.config(state="disabled")
        self.boton_reiniciar.config(state="disabled")
        
        # Ponemos los contadores a cero para empezar de nuevo
        self.lavados = 0
        self.secados = 0
        self.guardados = 0
        
        # Vaciamos las colas por si quedó algo de antes
        while not self.cola_lavar_a_secar.empty():
            self.cola_lavar_a_secar.get()
        while not self.cola_secar_a_guardar.empty():
            self.cola_secar_a_guardar.get()
            
        # Limpiamos la gráfica para la nueva ejecución
        self.uso_cpu = []
        self.puntos_tiempo = []
        self.eje.clear()
        self.eje.set_ylim(0, 100)
        self.eje.set_xlabel('Tiempo (s)')
        self.eje.set_ylabel('CPU (%)')
        self.eje.set_title('Uso de CPU')
        self.eje.grid(True)
        
        # Guardamos el tiempo en que iniciamos para medir cuánto tardamos
        self.tiempo_inicio = time.time()
        
        # Iniciamos tres trabajadores (hilos) uno para cada tarea
        threading.Thread(target=self.lavador, daemon=True).start()
        threading.Thread(target=self.secador, daemon=True).start()
        threading.Thread(target=self.guardador, daemon=True).start()
        
        # Iniciamos las funciones que actualizan lo que vemos
        self.actualizar_reloj()
        self.monitorear_cpu()
    
    def lavador(self):
        # Este trabajador se encarga de lavar los platos
        for i in range(self.NUMERO_PLATOS):
            time.sleep(1)  # Tarda 1 segundo en lavar cada plato
            self.lavados += 1
            self.cola_lavar_a_secar.put("plato")  # Pasa el plato al secador
            self.etq_lavado.config(text=f"Lavados: {self.lavados}")
    
    def secador(self):
        # Este trabajador se encarga de secar los platos
        for _ in range(self.NUMERO_PLATOS):
            self.cola_lavar_a_secar.get()  # Espera a recibir un plato lavado
            time.sleep(1.2)  # Tarda 1.2 segundos en secar cada plato
            self.secados += 1
            self.cola_secar_a_guardar.put("plato")  # Pasa el plato al guardador
            self.etq_secado.config(text=f"Secados: {self.secados}")
    
    def guardador(self):
        # Este trabajador se encarga de guardar los platos
        for _ in range(self.NUMERO_PLATOS):
            self.cola_secar_a_guardar.get()  # Espera a recibir un plato seco
            time.sleep(0.8)  # Tarda 0.8 segundos en guardar cada plato
            self.guardados += 1
            self.etq_guardado.config(text=f"Guardados: {self.guardados}")
    
    def actualizar_reloj(self):
        # Actualizamos el tiempo que ha pasado desde que iniciamos
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        self.etq_tiempo.config(text=f"Tiempo: {tiempo_transcurrido:.2f}s")
        
        if self.guardados < self.NUMERO_PLATOS:
            # Si aún no terminamos todos los platos, seguimos actualizando
            self.raiz.after(100, self.actualizar_reloj)
        else:
            # Si ya terminamos, mostramos el resultado final
            tiempo_final = tiempo_transcurrido
            self.boton_reiniciar.config(state="normal")
            self.etq_tiempo.config(text=f"¡Finalizado en {tiempo_final:.2f}s!")
            
            # Guardamos esta ejecución en el historial
            self.historial_ejecuciones.append(
                f"Ejecución: {len(self.historial_ejecuciones)+1} - {self.NUMERO_PLATOS} platos en {tiempo_final:.2f}s"
            )
            self.actualizar_texto_historial()
    
    def monitorear_cpu(self):
        # Revisamos cuánta CPU se está usando mientras corre la simulación
        if self.guardados < self.NUMERO_PLATOS:
            uso = psutil.cpu_percent()
            self.etq_cpu.config(text=f"CPU: {uso:.1f}%")
            
            # Añadimos un punto a la gráfica
            tiempo_transcurrido = time.time() - self.tiempo_inicio
            self.puntos_tiempo.append(tiempo_transcurrido)
            self.uso_cpu.append(uso)
            
            # Actualizamos la gráfica con el nuevo punto
            self.eje.clear()
            self.eje.set_ylim(0, 100)
            self.eje.plot(self.puntos_tiempo, self.uso_cpu, 'b-')
            self.eje.set_xlabel('Tiempo (s)')
            self.eje.set_ylabel('CPU (%)')
            self.eje.set_title('Uso de CPU ')
            self.eje.grid(True)
            self.lienzo.draw()
            
            # Seguimos monitoreando cada medio segundo
            self.raiz.after(500, self.monitorear_cpu)
    
    def actualizar_texto_historial(self):
        # Actualizamos la caja de texto con el historial de ejecuciones
        self.texto_historial.config(state="normal")
        self.texto_historial.delete(1.0, tk.END)
        for entrada in self.historial_ejecuciones:
            self.texto_historial.insert(tk.END, entrada + "\n")
        self.texto_historial.config(state="disabled")
    
    def reiniciar_simulacion(self):
        # Preparamos todo para poder iniciar una nueva simulación
        self.etq_lavado.config(text="Lavados: 0")
        self.etq_secado.config(text="Secados: 0")
        self.etq_guardado.config(text="Guardados: 0")
        self.etq_tiempo.config(text="Tiempo: 0.00s")
        self.etq_cpu.config(text="CPU: 0.0%")
        
        # Activamos el botón de inicio y desactivamos el de reinicio
        self.boton_iniciar.config(state="normal")
        self.boton_reiniciar.config(state="disabled")

if __name__ == "__main__":
    # Este programa muestra cómo funciona un pipeline con hilos
    # simulando el proceso de lavar, secar y guardar platos
    raiz = tk.Tk()
    app = AplicacionPipelinePlatos(raiz)
    raiz.mainloop()
