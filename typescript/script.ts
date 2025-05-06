let NUMERO_PLATOS = 5;
let lavados = 0;
let secados = 0;
let guardados = 0;
const historialEjecuciones: string[] = [];
const registrosLog: string[] = [];
const colaLavarASecar: Array<null> = [];
const colaSecarAGuardar: Array<null> = [];

// Referencias al htmll
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
const contenedorLog = document.getElementById('log') as HTMLDivElement;

let tiempoInicio: number = 0;
let intervaloActualizacion: number | undefined;

botonIniciar.addEventListener('click', iniciarSimulacion);
botonReiniciar.addEventListener('click', reiniciarSimulacion);

function padInicio(texto: string, longitud: number, relleno: string): string {
  while (texto.length < longitud) {
    texto = relleno + texto;
  }
  return texto;
}

function agregarLog(hilo: string, mensaje: string): void {
  const ahora = new Date();
  const timestamp = `${padInicio(
    ahora.getHours().toString(),
    2,
    '0'
  )}:${padInicio(ahora.getMinutes().toString(), 2, '0')}:${padInicio(
    ahora.getSeconds().toString(),
    2,
    '0'
  )}.${padInicio(ahora.getMilliseconds().toString(), 3, '0')}`;

  const logEntry = document.createElement('div');
  logEntry.classList.add('log-entry');

  const timestampSpan = document.createElement('span');
  timestampSpan.classList.add('timestamp');
  timestampSpan.textContent = `[${timestamp}]`;

  const hiloSpan = document.createElement('span');
  hiloSpan.classList.add(`thread-${hilo.toLowerCase()}`);
  hiloSpan.textContent = ` ${hilo}: `;

  const mensajeSpan = document.createElement('span');
  mensajeSpan.textContent = mensaje;

  logEntry.appendChild(timestampSpan);
  logEntry.appendChild(hiloSpan);
  logEntry.appendChild(mensajeSpan);
  contenedorLog.appendChild(logEntry);
  contenedorLog.scrollTop = contenedorLog.scrollHeight;

  registrosLog.push(`[${timestamp}] ${hilo}: ${mensaje}`);
}

// funcion principalll
async function iniciarSimulacion() {
  NUMERO_PLATOS = parseInt(entradaNumPlatos.value);

  botonIniciar.disabled = true;
  botonReiniciar.disabled = true;

  contenedorLog.innerHTML = '';
  registrosLog.length = 0;

  agregarLog('Sistema', `Iniciando simulación con ${NUMERO_PLATOS} platos`);

  // se reinician contadores y limpian colas
  lavados = 0;
  secados = 0;
  guardados = 0;
  colaLavarASecar.length = 0;
  colaSecarAGuardar.length = 0;

  agregarLog('Sistema', 'Colas vacías y listas para comenzar');

  etqLavados.textContent = `Lavados: ${lavados}`;
  etqSecados.textContent = `Secados: ${secados}`;
  etqGuardados.textContent = `Guardados: ${guardados}`;
  etqTiempo.textContent = `Tiempo: 0.00s`;

  // Guardar el tiempo de inicio
  tiempoInicio = performance.now();

  iniciarActualizacionTiempo();

  agregarLog('Sistema', 'Iniciando tareas...');

  // ejecucion de las tres funciones en paralelo
  await Promise.all([lavador(), secador(), guardador()]);

  // timepo final
  const tiempoFinal = (performance.now() - tiempoInicio) / 1000;
  etqTiempo.textContent = `¡Finalizado en ${tiempoFinal.toFixed(2)}s!`;

  if (intervaloActualizacion) clearInterval(intervaloActualizacion);

  agregarLog(
    'Sistema',
    `SIMULACIÓN COMPLETADA en ${tiempoFinal.toFixed(
      2
    )}s - Todos los platos procesados`
  );

  botonReiniciar.disabled = false;

  const nuevaEjecucion = `Ejecución ${
    historialEjecuciones.length + 1
  }: ${NUMERO_PLATOS} platos en ${tiempoFinal.toFixed(2)}s`;
  historialEjecuciones.push(nuevaEjecucion);
  actualizarHistorial();
}

function iniciarActualizacionTiempo() {
  if (intervaloActualizacion) clearInterval(intervaloActualizacion);

  intervaloActualizacion = setInterval(() => {
    const tiempoActual = (performance.now() - tiempoInicio) / 1000;
    etqTiempo.textContent = `Tiempo: ${tiempoActual.toFixed(2)}s`;

    if (guardados >= NUMERO_PLATOS) {
      clearInterval(intervaloActualizacion);
    }
  }, 200);
}

async function lavador(): Promise<void> {
  agregarLog('Lavador', `Iniciado - Lavará ${NUMERO_PLATOS} platos`);

  for (let i = 0; i < NUMERO_PLATOS; i++) {
    agregarLog('Lavador', `Lavando plato #${i + 1}...`);
    await dormir(1000);
    lavados++;
    colaLavarASecar.push(null);
    etqLavados.textContent = `Lavados: ${lavados}`;
    agregarLog('Lavador', `Plato #${i + 1} lavado y enviado a secado`);
  }

  agregarLog('Lavador', `Completado - ${lavados} platos lavados`);
}

async function secador(): Promise<void> {
  agregarLog('Secador', `Iniciado - Esperando platos para secar`);

  for (let i = 0; i < NUMERO_PLATOS; i++) {
    // Espera a que haya un plato lavado disponible
    agregarLog('Secador', `Esperando plato #${i + 1} para secar...`);
    while (colaLavarASecar.length === 0) {
      await dormir(100);
    }
    colaLavarASecar.shift();
    agregarLog('Secador', `Plato #${i + 1} recibido, secando...`);
    await dormir(1000);
    secados++;
    colaSecarAGuardar.push(null);
    etqSecados.textContent = `Secados: ${secados}`;
    agregarLog('Secador', `Plato #${i + 1} secado y enviado a guardar`);
  }

  agregarLog('Secador', `Completado - ${secados} platos secados`);
}

async function guardador(): Promise<void> {
  agregarLog('Guardador', `Iniciado - Esperando platos para guardar`);

  for (let i = 0; i < NUMERO_PLATOS; i++) {
    agregarLog('Guardador', `Esperando plato #${i + 1} para guardar...`);
    while (colaSecarAGuardar.length === 0) {
      await dormir(100);
    }
    colaSecarAGuardar.shift();
    agregarLog('Guardador', `Plato #${i + 1} recibido, guardando...`);
    await dormir(800);
    guardados++;
    etqGuardados.textContent = `Guardados: ${guardados}`;
    agregarLog('Guardador', `Plato #${i + 1} guardado correctamente`);
  }

  agregarLog('Guardador', `Completado - ${guardados} platos guardados`);
}

// Esta función hace que el programa espere un tiempo
function dormir(ms: number): Promise<void> {
  return new Promise((resolver) => setTimeout(resolver, ms));
}

function reiniciarSimulacion() {
  etqLavados.textContent = `Lavados: 0`;
  etqSecados.textContent = `Secados: 0`;
  etqGuardados.textContent = `Guardados: 0`;
  etqTiempo.textContent = `Tiempo: 0.00s`;

  botonIniciar.disabled = false;
  botonReiniciar.disabled = true;

  agregarLog(
    'Sistema',
    'Simulación reiniciada - Sistema listo para una nueva ejecución'
  );
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
