import React from 'react';
import ReactDOM from 'react-dom/client';
import Queen3DViewer from './App.jsx';

// 🔹 Test manuale (puoi cambiare N e regine)
const n = 5;
const queenPositions = [
  [0, 0, 0],
  [1, 2, 3],
  [3, 4, 1],
  [4, 1, 2],
];

// 🔹 Monta React nel div #viewer (contenuto nel tuo index.html Flask)
const container = document.getElementById('viewer');
if (container) {
  ReactDOM.createRoot(container).render(
    <React.StrictMode>
      <Queen3DViewer n={n} queenPositions={queenPositions} />
    </React.StrictMode>
  );
}
