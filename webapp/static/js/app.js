(function(){
  // helper
  // funzione di utilità per ottenere un elemento tramite id
  const $ = id => document.getElementById(id)

  // riferimenti agli elementi dei parametri
  const popSize = $('popSize');
  const gens = $('gens');
  const mut = $('mut');
  const permissive = $('permissive');

  const popSizeLabel = $('popSizeLabel');
  const gensLabel = $('gensLabel');
  const mutLabel = $('mutLabel');

  // aggiorna le etichette dei parametri quando cambiano i valori
  popSize.addEventListener('input', () => popSizeLabel.innerText = popSize.value);
  gens.addEventListener('input', () => gensLabel.innerText = gens.value);
  mut.addEventListener('input', () => mutLabel.innerText = mut.value);

  const startBtn = $('startBtn');
  const stopBtn = $('stopBtn');
  let currentRunId = null;
  let polling = null;
  let playInterval = null;

  // NUOVO: intervallo di riproduzione predefinito in ms
  const playIntervalDefault = 800;

  // Rimuovi toggle AST/UI: mostra sempre l'automa.
  // memorizza l'ultimo contesto di history/fetchResults
  let lastHistory = null;
  let lastGenSelect = null;

  // NUOVO: indici delle generazioni che hanno un automa nuovo/differente (rispetto alla history)
  let filteredGenerationIndices = [];
  // NUOVO: serializzazione dell'ultimo automa mostrato per evitare rendering duplicati
  let lastShownAutomatonSerialized = null;

  // aggiorna la lista dei migliori individui
  function updateTop(list) {
    const ul = $('topList');
    ul.innerHTML = '';
    if(!list) return;
    list.forEach((item, i) => {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      li.textContent = `${i+1}. ${item.regex} (${item.voto.toFixed(3)})`;
      ul.appendChild(li);
    });
  }

  // gestore click per avvio evoluzione
  startBtn.addEventListener('click', async () => {
    const body = {
      dimensione_popolazione: popSize.value,
      generazioni: gens.value,
      probabilita_mutazione: mut.value,
      top_n_display: 10,
      permissive_crossover: permissive.checked
    };
    // Directory di default usate dal server ('tracce_buone', 'tracce_cattive')
    // Usa dataset_id se caricato
    startBtn.disabled = true;
    const runInfoEl = $('runInfo');
    const datasetId = runInfoEl && runInfoEl.dataset && runInfoEl.dataset.datasetId ? runInfoEl.dataset.datasetId : null;
    if (datasetId) body.dataset_id = datasetId;
    const r = await fetch('/start', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    const data = await r.json();
    if (!data.run_id) {
      alert('Errore nell\'avvio dell\'esecuzione');
      startBtn.disabled = false;
      return;
    }
    currentRunId = data.run_id;
    // Non mostrare l'ID run; mostra solo stato generico
    $('runInfo').innerHTML = `<p class="text-white">Esecuzione avviata...</p>`;
    stopBtn.disabled = false;
    // avvia polling
    polling = setInterval(async () => {
      const resp = await fetch(`/status/${currentRunId}`);
      const st = await resp.json();
      const history = st.history || [];
      const latest = history.length ? history[history.length-1]: null;
      if (latest && latest.top10) updateTop(latest.top10);

      // LIVE: preferisci st.live_automaton (fresco) altrimenti latest.automaton
      const liveAut = st.live_automaton || (latest && latest.automaton ? latest.automaton : null);
      if (liveAut) {
        const serialized = JSON.stringify(liveAut);
        if (serialized !== lastShownAutomatonSerialized) {
          try {
            renderAutomatonGraph(liveAut, { live: true });
            lastShownAutomatonSerialized = serialized;
          } catch (e) {
            console.warn('Errore nel rendering dell\'automa live:', e);
          }
        }
      }

      const statusMap = { queued: 'in coda', running: 'in esecuzione', finished: 'terminato', stopped: 'interrotto', error: 'errore' };
      const statusText = statusMap[st.status] || st.status;
      $('runInfo').innerHTML = `<p>Stato: ${statusText} — generazioni raccolte: ${history.length}</p>`;
      if (st.status === 'finished' || st.status === 'error') {
        clearInterval(polling);
        $('runInfo').innerHTML = `<p>Stato: ${statusText}. Clicca Ottieni risultati.</p><button id='resultsBtn' class='btn btn-success mt-2'>Ottieni risultati</button>`;
        const resBtnEl = $('resultsBtn');
        if (resBtnEl) resBtnEl.addEventListener('click', () => fetchResults(currentRunId));
        const dlBtnEl = $('downloadBtn');
        if (dlBtnEl) dlBtnEl.addEventListener('click', () => { window.location.href = `/download/${currentRunId}`; });
        startBtn.disabled = false;
        stopBtn.disabled = true;
      }
    }, 1500);

  });

  // Caricamento dataset
  const uploadBtn = $('uploadBtn');
  const uploadStatus = $('uploadStatus');
  uploadBtn.addEventListener('click', async () => {
    const gf = document.getElementById('goodFiles').files;
    const bf = document.getElementById('badFiles').files;
    if ((!gf || gf.length===0) && (!bf || bf.length===0)) {
      alert('Nessun file selezionato');
      return;
    }
    const fd = new FormData();
    for (let i=0;i<gf.length;i++) fd.append('good_files', gf[i]);
    for (let i=0;i<bf.length;i++) fd.append('bad_files', bf[i]);
    uploadBtn.disabled = true;
    uploadStatus.innerText = 'Caricamento in corso...';
    // Reset colori stato
    uploadStatus.classList.remove('text-success', 'text-danger');

    const r = await fetch('/upload_dataset', {method:'POST', body: fd});
    const data = await r.json();
    if (data.dataset_id) {
      uploadStatus.innerText = 'Dataset caricato con successo!';
      uploadStatus.classList.remove('text-danger');
      uploadStatus.classList.add('text-success');

      // imposta dataset id per le successive esecuzioni (nascosto)
      $('runInfo').dataset.datasetId = data.dataset_id;
      // Mostra breve messaggio di successo in runInfo (bianco)
      $('runInfo').innerHTML = `<p class="text-white">Avvia l'evoluzione!</p>`;
      // Rimosso codice di disabilitazione input directory (input rimossi)
    } else {
      // Fallimento: mostra testo rosso di errore
      uploadStatus.innerText = 'Caricamento fallito';
      uploadStatus.classList.remove('text-success');
      uploadStatus.classList.add('text-danger');
    }
    uploadBtn.disabled = false;
  });

  // NUOVO: bottone per generare dataset
  const generateDatasetBtn = document.getElementById('generateDatasetBtn');
  generateDatasetBtn.addEventListener('click', async () => {
    generateDatasetBtn.disabled = true;
    const generateStatus = document.getElementById('generateStatus');
    generateStatus.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Generazione in corso...';
    // rimuovi utility colore qui; CSS forza bianco
    generateStatus.className = 'small mt-2';
    
    try {
      const resp = await fetch('/generate_dataset', {method: 'POST'});
      const data = await resp.json();
      
      if (data.error) {
        generateStatus.innerHTML = `<span class="text-danger">Errore: ${data.error}</span>`;
        generateStatus.className = 'small mt-2 text-danger';
        generateDatasetBtn.disabled = false;
        return;
      }
      
      // Mostra il pattern generato
      const patternEl = document.getElementById('generatedPattern');
      const patternCode = document.getElementById('patternCode');
      const patternStats = document.getElementById('patternStats');
      
      patternCode.textContent = data.pattern;
      patternStats.innerHTML = `
        ✓ Tracce BUONE: <strong>${data.good_count}</strong><br>
        ✓ Tracce CATTIVE: <strong>${data.bad_count}</strong>
      `;
      patternEl.style.display = 'block';
      
      // Messaggio di successo in bianco (anche CSS lo forza)
      generateStatus.innerHTML = `<span class="text-white">✓ Dataset generato con successo!</span>`;
      generateStatus.className = 'small mt-2 text-white';
      
      // Imposta dataset_id per le successive esecuzioni e mostra info bianca
      $('runInfo').dataset.datasetId = data.dataset_id;
      $('runInfo').innerHTML = `<p class="text-white">Dataset pronto! Configura i parametri e avvia l'evoluzione.</p>`;
      
      generateDatasetBtn.disabled = false;
    } catch (e) {
      generateStatus.innerHTML = `<span class="text-danger">Errore di connessione: ${e.message}</span>`;
      generateStatus.className = 'small mt-2 text-danger';
      generateDatasetBtn.disabled = false;
    }
  });

  // gestore click per stop evoluzione
  stopBtn.addEventListener('click', () => {
    if (!currentRunId) return;
    fetch(`/stop/${currentRunId}`, {method:'POST'}).then(() => {
      if (polling) clearInterval(polling);
      $('runInfo').innerHTML = '<p>Interruzione in corso...</p>';
      startBtn.disabled = false;
      stopBtn.disabled = true;
    });
  });

  // funzione per ottenere i risultati di una run
  async function fetchResults(runId) {
    const r = await fetch(`/results/${runId}`);
    const data = await r.json();
    if (data.status !== 'finished') {
      alert('Esecuzione non ancora terminata');
      return;
    }
    // Costruisci grafico fitness per generazione (top-1)
    const history = data.history || [];
    lastHistory = history; // salva per play
    const labels = history.map(h => h.generation);
    const top1 = history.map(h => (h.top10 && h.top10.length? h.top10[0].voto: 0));

    const ctx = document.getElementById('fitnessChart').getContext('2d');
    if (window.__chart) window.__chart.destroy();
    // Grafico responsivo rispetto al contenitore
    window.__chart = new Chart(ctx, {
      type:'line',
      data:{ labels, datasets:[{label:'Best Fitness', data:top1, borderColor:'green', fill:false}]},
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, suggestedMax: 1 }
        }
      }
    });

    // Sezione rappresentazione grafica automi rimossa
    $('resultsSection').style.display = 'block';
  }

  // renderAstGraph lasciata qui ma non usata di default (utile per debug)

  // Funzione rappresentazione grafica automi rimossa

  // NUOVO: imposta font predefinito Chart.js (coerente con Inter)
  if (typeof Chart !== 'undefined' && Chart.defaults) {
    Chart.defaults.font.family = "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";
    Chart.defaults.font.size = 12;
  }

})();