import React from 'react';
import ReactDOM from 'react-dom/client';
import Queen3DViewer from './App.jsx';

window.renderQueens = (n, queenPositions) => {
  console.log("[DEBUG] 3D scene rendering with n =", n, "positions =", queenPositions);

  const container = document.getElementById('viewer');
  if (container) {
    // Cleaning: reset the content before ri-render 
    container.innerHTML = '';
    const root = ReactDOM.createRoot(container);
    root.render(
      <React.StrictMode>
        <Queen3DViewer n={n} queenPositions={queenPositions} />
      </React.StrictMode>
    );
  } else {
    console.error("[ERROR] #viewer Element not found in index.html");
  }
};
