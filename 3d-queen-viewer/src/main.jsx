import React from 'react';
import ReactDOM from 'react-dom/client';
import Queen3DViewer from './App.jsx';

// 🔹 Qui scegli manualmente dimensione e regine per test
const n = 4;
const queenPositions = [
  [0, 0, 0],
  [1, 2, 3],
  [2, 4, 1],
  [3, 1, 6],
];

// 🔹 React render nel div #viewer del tuo index.html Flask
const container = document.getElementById('viewer');
if (container) {
  const root = ReactDOM.createRoot(container);
  root.render(<Queen3DViewer n={n} queenPositions={queenPositions} />);
}
