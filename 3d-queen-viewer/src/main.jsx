import React from 'react';
import ReactDOM from 'react-dom/client';
import Queen3DViewer from './App.jsx';

window.renderQueens = (n, queenPositions) => {
  console.log("[DEBUG] Rendering scena 3D con n =", n, "posizioni =", queenPositions);

  const container = document.getElementById('viewer');
  if (container) {
    // Pulizia: resetta il contenuto precedente prima di re-renderizzare
    container.innerHTML = '';
    const root = ReactDOM.createRoot(container);
    root.render(
      <React.StrictMode>
        <Queen3DViewer n={n} queenPositions={queenPositions} />
      </React.StrictMode>
    );
  } else {
    console.error("[ERRORE] Elemento #viewer non trovato in index.html");
  }
};
