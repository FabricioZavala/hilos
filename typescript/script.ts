const NUM_DISHES = 5;

let washed = 0;
let dried  = 0;
let stored = 0;

// Colas simples
const qWashToDry: Array<null> = [];
const qDryToStore: Array<null> = [];

const lblWashed  = document.getElementById("washed") as HTMLDivElement;
const lblDried   = document.getElementById("dried")  as HTMLDivElement;
const lblStored  = document.getElementById("stored") as HTMLDivElement;
const lblElapsed = document.getElementById("elapsed") as HTMLDivElement;
const btnStart   = document.getElementById("startBtn") as HTMLButtonElement;

btnStart.addEventListener("click", async () => {
  btnStart.disabled = true;
  const startTime = performance.now();

  // Ejecuta las tres funciones en “paralelo”
  await Promise.all([washer(), dryer(), storer()]);

  const elapsed = (performance.now() - startTime) / 1000;
  lblElapsed.textContent = `¡Finalizado en ${elapsed.toFixed(2)}s!`;
  btnStart.disabled = false;
});

async function washer(): Promise<void> {
  for (let i = 0; i < NUM_DISHES; i++) {
    await sleep(1000);           // simula lavar plato
    washed++;
    qWashToDry.push(null);       // encola
    lblWashed.textContent = `Lavados: ${washed}`;
  }
}

async function dryer(): Promise<void> {
  for (let i = 0; i < NUM_DISHES; i++) {
    // espera a que haya algo en la cola
    while (qWashToDry.length === 0) {
      await sleep(100);
    }
    qWashToDry.shift();
    await sleep(1000);           // simula secar plato
    dried++;
    qDryToStore.push(null);
    lblDried.textContent = `Secados:  ${dried}`;
  }
}

async function storer(): Promise<void> {
  for (let i = 0; i < NUM_DISHES; i++) {
    while (qDryToStore.length === 0) {
      await sleep(100);
    }
    qDryToStore.shift();
    await sleep(1000);           // simula guardar plato
    stored++;
    lblStored.textContent = `Guardados: ${stored}`;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise(res => setTimeout(res, ms));
}
