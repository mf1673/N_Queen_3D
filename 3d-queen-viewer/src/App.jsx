import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

export default function Queen3DViewer({ n, queenPositions = [] }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    // --- Create scene, camera and renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b0b0b);

    const width = mount.clientWidth;
    const height = mount.clientHeight;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(n * 1.6, n * 1.2, n * 1.6);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio || 1);
    mount.appendChild(renderer.domElement);

    // --- Scene lights
    const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 0.9);
    hemi.position.set(0, n * 2, 0);
    scene.add(hemi);
    const dir = new THREE.DirectionalLight(0xffffff, 0.6);
    dir.position.set(n, n * 2, n);
    scene.add(dir);

    // --- Orbit controls for rotating the view
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.rotateSpeed = 0.6;

    // --- Objects main gruop
    const group = new THREE.Group();
    scene.add(group);

    // --- Create the semitransparent 3D grid
    const cellSize = 0.9;
    const gridMat = new THREE.MeshStandardMaterial({
      color: 0x999999,
      transparent: true,
      opacity: 0.07,
      metalness: 0.1,
      roughness: 0.6,
      depthWrite: false,
    });

    const cubeGeo = new THREE.BoxGeometry(cellSize, cellSize, cellSize);
    const totalCells = n * n * n;
    const gridInstanced = new THREE.InstancedMesh(cubeGeo, gridMat, totalCells);
    gridInstanced.instanceMatrix.setUsage(THREE.DynamicDrawUsage);

    let id = 0;
    for (let x = 0; x < n; x++) {
      for (let y = 0; y < n; y++) {
        for (let z = 0; z < n; z++) {
          const matrix = new THREE.Matrix4();
          const px = x - (n - 1) / 2;
          const py = y - (n - 1) / 2;
          const pz = z - (n - 1) / 2;
          matrix.makeTranslation(px, py, pz);
          gridInstanced.setMatrixAt(id, matrix);
          id++;
        }
      }
    }
    group.add(gridInstanced);

    // --- Outline of the main cube
    const bbox = new THREE.BoxGeometry(n, n, n);
    const edges = new THREE.EdgesGeometry(bbox);
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x666666 }));
    group.add(line);

    // --- Create red queens
    const queenGeo = new THREE.BoxGeometry(cellSize * 0.9, cellSize * 0.9, cellSize * 0.9);
    const queenMat = new THREE.MeshStandardMaterial({ color: 0xff3333, metalness: 0.2, roughness: 0.4 });

    // --- Here the queens are placed according to the solver result
    const queenInstanced = new THREE.InstancedMesh(queenGeo, queenMat, queenPositions.length);
    const tmpMat = new THREE.Matrix4();

    queenPositions.forEach(([x, y, z], i) => {
      const px = x - (n - 1) / 2;
      const py = y - (n - 1) / 2;
      const pz = z - (n - 1) / 2;
      tmpMat.makeTranslation(px, py, pz);
      queenInstanced.setMatrixAt(i, tmpMat);
    });

    group.add(queenInstanced);

    // --- Window resize management
    const onResize = () => {
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', onResize);

    // --- Loop animation
    let rafId;
    const animate = () => {
      controls.update();
      renderer.render(scene, camera);
      rafId = requestAnimationFrame(animate);
    };
    animate();

    // --- Cleanup
    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', onResize);
      controls.dispose();
      renderer.dispose();
      gridInstanced.geometry.dispose();
      gridInstanced.material.dispose();
      queenInstanced.geometry.dispose();
      queenInstanced.material.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, [n, queenPositions]);

  return <div ref={mountRef} style={{width: '575px', height: '575px'}} />;
}
