// Configuración inicial del simulador
let NUMERO_PLATOS = 5;
let lavados = 0;
let secados = 0;
let guardados = 0;

// Historial de ejecuciones anteriores
const historialEjecuciones: string[] = [];

// Estas colas nos sirven para pasar platos entre las etapas
const colaLavarASecar: Array<null> = [];
const colaSecarAGuardar: Array<null> = [];

// Referencias a elementos del DOM
const etqLavados = document.getElementById('lavados') as HTMLDivElement;
const etqSecados = document.getElementById('secados') as HTMLDivElement;
const etqGuardados = document.getElementById('guardados') as HTMLDivElement;
const etqTiempo = document.getElementById(
  'tiempoTranscurrido'
) as HTMLDivElement;
const botonIniciar = document.getElementById(
  'botonIniciar'
) as HTMLButtonElement;
const botonReiniciar = document.getElementById(
  'botonReiniciar'
) as HTMLButtonElement;
const entradaNumPlatos = document.getElementById(
  'numPlatos'
) as HTMLInputElement;
const contenedorHistorial = document.getElementById(
  'historial'
) as HTMLDivElement;

// Para monitorear el tiempo y actualizaciones
let tiempoInicio: number = 0;
let intervaloActualizacion: number | undefined;

// Configuración inicial
botonIniciar.addEventListener('click', iniciarPipeline);
botonReiniciar.addEventListener('click', reiniciarSimulacion);

// Esta función inicia la simulación 
async function iniciarPipeline() {
  NUMERO_PLATOS = parseInt(entradaNumPlatos.value);

  // Deshabilitamos botones y reiniciamos contadores
  botonIniciar.disabled = true;
  botonReiniciar.disabled = true;

  // Reiniciamos contadores y limpiamos colas
  lavados = 0;
  secados = 0;
  guardados = 0;
  colaLavarASecar.length = 0;
  colaSecarAGuardar.length = 0;

  // Actualizamos las etiquetas para mostrar los contadores
  etqLavados.textContent = `Lavados: ${lavados}`;
  etqSecados.textContent = `Secados: ${secados}`;
  etqGuardados.textContent = `Guardados: ${guardados}`;
  etqTiempo.textContent = `Tiempo: 0.00s`;

  // Guardamos el tiempo de inicio para medir cuánto tarda
  tiempoInicio = performance.now();

  // Iniciamos la actualización del reloj
  iniciarActualizacionTiempo();

  // Ejecutamos las tres funciones en "paralelo"
  await Promise.all([lavador(), secador(), guardador()]);

  // Calculamos y mostramos el tiempo final
  const tiempoFinal = (performance.now() - tiempoInicio) / 1000;
  etqTiempo.textContent = `¡Finalizado en ${tiempoFinal.toFixed(2)}s!`;

  // Paramos las actualizaciones periódicas
  if (intervaloActualizacion) clearInterval(intervaloActualizacion);

  // Habilitamos el botón de reinicio
  botonReiniciar.disabled = false;

  // Guardamos esta ejecución en el historial
  const nuevaEjecucion = `Ejecución ${
    historialEjecuciones.length + 1
  }: ${NUMERO_PLATOS} platos en ${tiempoFinal.toFixed(2)}s`;
  historialEjecuciones.push(nuevaEjecucion);
  actualizarHistorial();
}

// Esta función actualiza el tiempo transcurrido
function iniciarActualizacionTiempo() {
  if (intervaloActualizacion) clearInterval(intervaloActualizacion);

  intervaloActualizacion = setInterval(() => {
    const tiempoActual = (performance.now() - tiempoInicio) / 1000;
    etqTiempo.textContent = `Tiempo: ${tiempoActual.toFixed(2)}s`;

    // Si ya terminaron todas las etapas, detenemos la actualización
    if (guardados >= NUMERO_PLATOS) {
      clearInterval(intervaloActualizacion);
    }
  }, 200);
}

// Este trabajador se encarga de lavar los platos
async function lavador(): Promise<void> {
  for (let i = 0; i < NUMERO_PLATOS; i++) {
    await dormir(1000); // Tarda 1 segundo en lavar cada plato
    lavados++;
    colaLavarASecar.push(null); // Pasa el plato al secador
    etqLavados.textContent = `Lavados: ${lavados}`;
  }
}

// Este trabajador se encarga de secar los platos
async function secador(): Promise<void> {
  for (let i = 0; i < NUMERO_PLATOS; i++) {
    // Espera a que haya un plato lavado disponible
    while (colaLavarASecar.length === 0) {
      await dormir(100);
    }
    colaLavarASecar.shift();
    await dormir(1200); // Tarda 1.2 segundos en secar cada plato
    secados++;
    colaSecarAGuardar.push(null); // Pasa el plato al guardador
    etqSecados.textContent = `Secados: ${secados}`;
  }
}

// Este trabajador se encarga de guardar los platos
async function guardador(): Promise<void> {
  for (let i = 0; i < NUMERO_PLATOS; i++) {
    // Espera a que haya un plato seco disponible
    while (colaSecarAGuardar.length === 0) {
      await dormir(100);
    }
    colaSecarAGuardar.shift();
    await dormir(800); // Tarda 0.8 segundos en guardar cada plato
    guardados++;
    etqGuardados.textContent = `Guardados: ${guardados}`;
  }
}

// Esta función hace que el programa espere un tiempo
function dormir(ms: number): Promise<void> {
  return new Promise((resolver) => setTimeout(resolver, ms));
}

// Esta función limpia la simulación para empezar de nuevo
function reiniciarSimulacion() {
  // Reiniciamos contadores visualmente
  etqLavados.textContent = `Lavados: 0`;
  etqSecados.textContent = `Secados: 0`;
  etqGuardados.textContent = `Guardados: 0`;
  etqTiempo.textContent = `Tiempo: 0.00s`;

  // Habilitamos el botón de inicio
  botonIniciar.disabled = false;
  botonReiniciar.disabled = true;
}

function actualizarHistorial() {
  contenedorHistorial.innerHTML = '';
  historialEjecuciones.forEach((ejecucion) => {
    const elemento = document.createElement('div');
    elemento.textContent = ejecucion;
    elemento.style.marginBottom = '5px';
    contenedorHistorial.appendChild(elemento);
  });
}