import threading
import queue
import time
import tkinter as tk
from tkinter import ttk

NUM_DISHES = 5

class DishPipelineApp:
    def __init__(self, root):
        self.root = root
        root.title("Lavar → Secar → Guardar Platos")

        # Contadores
        self.washed = 0
        self.dried  = 0
        self.stored = 0

        # Queues entre etapas
        self.q_wash_to_dry = queue.Queue()
        self.q_dry_to_store = queue.Queue()

        # Labels GUI
        self.lbl_wash = ttk.Label(root, text="Lavados: 0")
        self.lbl_dry  = ttk.Label(root, text="Secados:  0")
        self.lbl_store= ttk.Label(root, text="Guardados: 0")
        self.lbl_time = ttk.Label(root, text="Tiempo transcurrido: 0.00s")

        self.lbl_wash.pack(padx=10, pady=5)
        self.lbl_dry.pack(padx=10, pady=5)
        self.lbl_store.pack(padx=10, pady=5)
        self.lbl_time.pack(padx=10, pady=10)

        # Botón de inicio
        self.btn_start = ttk.Button(root, text="Iniciar pipeline", command=self.start_pipeline)
        self.btn_start.pack(pady=5)

    def start_pipeline(self):
        self.btn_start.config(state="disabled")
        self.start_time = time.time()

        # Hilos
        threading.Thread(target=self.washer, daemon=True).start()
        threading.Thread(target=self.dryer, daemon=True).start()
        threading.Thread(target=self.storer, daemon=True).start()

        # Actualización periódica de tiempo
        self.update_clock()

    def washer(self):
        for i in range(NUM_DISHES):
            time.sleep(1)                      # Simula lavar un plato
            self.washed += 1
            self.q_wash_to_dry.put("plato")
            self.lbl_wash.config(text=f"Lavados: {self.washed}")

    def dryer(self):
        for _ in range(NUM_DISHES):
            self.q_wash_to_dry.get()           # Espera un plato lavado
            time.sleep(1)                      # Simula secar plato
            self.dried += 1
            self.q_dry_to_store.put("plato")
            self.lbl_dry.config(text=f"Secados:  {self.dried}")

    def storer(self):
        for _ in range(NUM_DISHES):
            self.q_dry_to_store.get()          # Espera un plato seco
            time.sleep(1)                      # Simula guardar plato
            self.stored += 1
            self.lbl_store.config(text=f"Guardados: {self.stored}")

    def update_clock(self):
        elapsed = time.time() - self.start_time
        self.lbl_time.config(text=f"Tiempo transcurrido: {elapsed:.2f}s")
        if self.stored < NUM_DISHES:
            # Sigue actualizando mientras no termine
            self.root.after(100, self.update_clock)
        else:
            self.btn_start.config(state="normal")
            self.lbl_time.config(text=f"¡Finalizado en {elapsed:.2f}s!")

if __name__ == "__main__":
    root = tk.Tk()
    app = DishPipelineApp(root)
    root.mainloop()
