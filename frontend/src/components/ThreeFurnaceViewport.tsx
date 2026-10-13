import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { Eye, RotateCcw, Flame, Layers, Maximize2, Sparkles, Thermometer } from 'lucide-react';
import { FurnaceTelemetry } from '../types/furnace';

interface ThreeFurnaceViewportProps {
  telemetry: FurnaceTelemetry;
  onSelectElectrode?: (index: number) => void;
}

export const ThreeFurnaceViewport: React.FC<ThreeFurnaceViewportProps> = ({
  telemetry,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);

  // Animated object refs
  const electrodesRef = useRef<THREE.Group[]>([]);
  const arcsRef = useRef<THREE.Line[]>([]);
  const arcLightsRef = useRef<THREE.PointLight[]>([]);
  const moltenBathMeshRef = useRef<THREE.Mesh | null>(null);
  const smokeParticlesRef = useRef<THREE.Points | null>(null);
  const smokePosArrayRef = useRef<Float32Array | null>(null);
  const animFrameIdRef = useRef<number | null>(null);

  // View state toggles
  const [cutawayActive, setCutawayActive] = useState<boolean>(true);
  const [thermalMode, setThermalMode] = useState<boolean>(false);
  const [autoRotate, setAutoRotate] = useState<boolean>(false);
  const [activeCamPreset, setActiveCamPreset] = useState<'ISOMETRIC' | 'HEARTH' | 'TOP'>('ISOMETRIC');

  // Brick texture generation helper
  const createFirebrickTexture = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    if (!ctx) return new THREE.Texture();

    ctx.fillStyle = '#C47A47'; // Warm ceramic terracotta alumina
    ctx.fillRect(0, 0, 512, 512);

    // Brick mortar lines
    ctx.strokeStyle = '#8D4925';
    ctx.lineWidth = 4;
    const rows = 16;
    const rowHeight = 512 / rows;
    const cols = 8;
    const colWidth = 512 / cols;

    for (let r = 0; r <= rows; r++) {
      const y = r * rowHeight;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(512, y);
      ctx.stroke();
    }

    for (let r = 0; r < rows; r++) {
      const offset = (r % 2) * (colWidth / 2);
      const y = r * rowHeight;
      for (let c = 0; c <= cols + 1; c++) {
        const x = c * colWidth + offset;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x, y + rowHeight);
        ctx.stroke();
      }
    }

    // Granular ceramic noise
    for (let i = 0; i < 3000; i++) {
      const x = Math.random() * 512;
      const y = Math.random() * 512;
      const tone = Math.random() > 0.5 ? 'rgba(255, 230, 200, 0.15)' : 'rgba(80, 30, 10, 0.2)';
      ctx.fillStyle = tone;
      ctx.fillRect(x, y, 2, 2);
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(4, 2);
    return texture;
  };

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene setup with warm industrial fog
    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#EFE8D8'); // Warm Sand Aged Parchment
    scene.fog = new THREE.FogExp2('#EFE8D8', 0.012);
    sceneRef.current = scene;

    // 2. Camera setup
    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000);
    camera.position.set(38, 26, 38);
    cameraRef.current = camera;

    // 3. Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    rendererRef.current = renderer;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // 4. OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2 + 0.05; // Don't go below ground plane
    controls.minDistance = 15;
    controls.maxDistance = 120;
    controls.target.set(0, 7, 0);
    controlsRef.current = controls;

    // 5. Lighting: Warm foundry studio lighting
    const ambientLight = new THREE.AmbientLight(0xfff5e6, 0.85);
    scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffecd2, 1.8);
    keyLight.position.set(45, 60, 30);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.bias = -0.0005;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xd7ccc8, 0.9);
    fillLight.position.set(-35, 30, -35);
    scene.add(fillLight);

    // Crucible floor warm incandescent uplight
    const hearthCoreLight = new THREE.PointLight(0xff8f00, 3.5, 45, 1.2);
    hearthCoreLight.position.set(0, 3.5, 0);
    scene.add(hearthCoreLight);

    // 6. Ground Pedestal (Warm polished foundry concrete)
    const floorGeo = new THREE.CylinderGeometry(28, 30, 2, 48);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0xe5dcce,
      roughness: 0.85,
      metalness: 0.1,
    });
    const floorMesh = new THREE.Mesh(floorGeo, floorMat);
    floorMesh.position.y = -1;
    floorMesh.receiveShadow = true;
    scene.add(floorMesh);

    // Steel circular railing ring around furnace
    const railingGeo = new THREE.TorusGeometry(22, 0.25, 12, 64);
    const railingMat = new THREE.MeshStandardMaterial({ color: 0x5d4037, roughness: 0.5, metalness: 0.6 });
    const railingMesh = new THREE.Mesh(railingGeo, railingMat);
    railingMesh.rotation.x = Math.PI / 2;
    railingMesh.position.y = 0.2;
    scene.add(railingMesh);

    // 7. Furnace Assembly Group
    const furnaceGroup = new THREE.Group();
    scene.add(furnaceGroup);

    // A. Outer Shell (Cast Iron Bronze Casing)
    // 270 degree cylinder for cutaway effect
    const outerRadius = 14;
    const innerRadius = 12.2;
    const furnaceHeight = 18;
    const thetaLength = cutawayActive ? Math.PI * 1.5 : Math.PI * 2;

    const outerShellGeo = new THREE.CylinderGeometry(
      outerRadius,
      outerRadius,
      furnaceHeight,
      64,
      1,
      true,
      0,
      thetaLength
    );
    const outerShellMat = new THREE.MeshStandardMaterial({
      color: 0x3d312a, // Warm cast iron bronze
      roughness: 0.7,
      metalness: 0.5,
      side: THREE.DoubleSide,
    });
    const outerShell = new THREE.Mesh(outerShellGeo, outerShellMat);
    outerShell.position.y = furnaceHeight / 2;
    outerShell.castShadow = true;
    outerShell.receiveShadow = true;
    furnaceGroup.add(outerShell);

    // Structural steel reinforcing bands (stiffener rings)
    [3, 8, 13, 17.5].forEach((h) => {
      const bandGeo = new THREE.CylinderGeometry(outerRadius + 0.25, outerRadius + 0.25, 0.6, 64, 1, true, 0, thetaLength);
      const bandMat = new THREE.MeshStandardMaterial({ color: 0x6e4e37, roughness: 0.5, metalness: 0.7 });
      const band = new THREE.Mesh(bandGeo, bandMat);
      band.position.y = h;
      furnaceGroup.add(band);
    });

    // B. Inner Refractory Lining (Ceramic Alumina Firebricks)
    const firebrickTex = createFirebrickTexture();
    const innerLiningGeo = new THREE.CylinderGeometry(
      innerRadius,
      innerRadius,
      furnaceHeight - 0.2,
      64,
      1,
      true,
      0,
      thetaLength
    );
    const innerLiningMat = new THREE.MeshStandardMaterial({
      map: firebrickTex,
      roughness: 0.9,
      metalness: 0.05,
      side: THREE.DoubleSide,
    });
    const innerLining = new THREE.Mesh(innerLiningGeo, innerLiningMat);
    innerLining.position.y = furnaceHeight / 2;
    furnaceGroup.add(innerLining);

    // C. Furnace Bottom Hearth Dish (Inverted cone / thick crucible base)
    const hearthBaseGeo = new THREE.CylinderGeometry(innerRadius, innerRadius * 0.9, 3, 48);
    const hearthBaseMat = new THREE.MeshStandardMaterial({
      color: 0x5c3317,
      roughness: 0.95,
    });
    const hearthBase = new THREE.Mesh(hearthBaseGeo, hearthBaseMat);
    hearthBase.position.y = 1.5;
    furnaceGroup.add(hearthBase);

    // D. Molten Liquid Silicon Pool (Crucible Lava Floor)
    const moltenPoolGeo = new THREE.CylinderGeometry(innerRadius - 0.3, innerRadius - 0.4, 1.2, 64, 16);
    const moltenPoolMat = new THREE.MeshStandardMaterial({
      color: 0xff6f00, // Dynamic shifting
      emissive: 0xff8f00,
      emissiveIntensity: 0.9,
      roughness: 0.25,
      metalness: 0.8,
    });
    const moltenPool = new THREE.Mesh(moltenPoolGeo, moltenPoolMat);
    moltenPool.position.y = 3.2;
    furnaceGroup.add(moltenPool);
    moltenBathMeshRef.current = moltenPool;

    // Tapping spout (Tap-hole chute on furnace side)
    const tapSpoutGeo = new THREE.BoxGeometry(4, 1.5, 3);
    const tapSpoutMat = new THREE.MeshStandardMaterial({ color: 0x3d312a, roughness: 0.6 });
    const tapSpout = new THREE.Mesh(tapSpoutGeo, tapSpoutMat);
    tapSpout.position.set(outerRadius + 1.2, 3.2, 0);
    furnaceGroup.add(tapSpout);

    // Molten stream trickling from tap spout
    const moltenStreamGeo = new THREE.CylinderGeometry(0.3, 0.25, 3.5, 12);
    const moltenStreamMat = new THREE.MeshStandardMaterial({
      color: 0xffa000,
      emissive: 0xff6f00,
      emissiveIntensity: 1.2,
      roughness: 0.2,
    });
    const moltenStream = new THREE.Mesh(moltenStreamGeo, moltenStreamMat);
    moltenStream.position.set(outerRadius + 2.8, 1.6, 0);
    moltenStream.rotation.z = -Math.PI / 10;
    furnaceGroup.add(moltenStream);

    // Refractory receiving ladle for molten Si
    const ladleGeo = new THREE.CylinderGeometry(2.5, 2.0, 2.4, 24);
    const ladleMat = new THREE.MeshStandardMaterial({ color: 0x4a3b32, roughness: 0.8 });
    const ladle = new THREE.Mesh(ladleGeo, ladleMat);
    ladle.position.set(outerRadius + 3.8, 0.4, 0);
    furnaceGroup.add(ladle);

    // E. Upper Roof / Hood (Fume Hood & Chimney Duct)
    const hoodGeo = new THREE.ConeGeometry(outerRadius + 0.5, 4.5, 48, 1, true, 0, thetaLength);
    const hoodMat = new THREE.MeshStandardMaterial({
      color: 0x423229,
      roughness: 0.6,
      metalness: 0.4,
      side: THREE.DoubleSide,
    });
    const hood = new THREE.Mesh(hoodGeo, hoodMat);
    hood.position.y = furnaceHeight + 2.25;
    furnaceGroup.add(hood);

    // Chimney Exhaust Duct at top-right
    const chimneyGeo = new THREE.CylinderGeometry(2.2, 2.2, 10, 32);
    const chimneyMat = new THREE.MeshStandardMaterial({
      color: 0x795548,
      roughness: 0.8,
      metalness: 0.2,
    });
    const chimney = new THREE.Mesh(chimneyGeo, chimneyMat);
    chimney.position.set(7, furnaceHeight + 7, -5);
    furnaceGroup.add(chimney);

    // Chimney reinforcement collar
    const collarGeo = new THREE.TorusGeometry(2.35, 0.25, 12, 32);
    const collarMat = new THREE.MeshStandardMaterial({ color: 0x4e342e });
    const collar = new THREE.Mesh(collarGeo, collarMat);
    collar.rotation.x = Math.PI / 2;
    collar.position.set(7, furnaceHeight + 11.8, -5);
    furnaceGroup.add(collar);

    // 8. Three Heavy Graphite Electrodes in Delta Pitch
    const electrodeRadius = 1.35;
    const electrodeLength = 17;
    const electrodePitch = 4.8;
    const angles = [0, (2 * Math.PI) / 3, (4 * Math.PI) / 3];

    electrodesRef.current = [];
    arcsRef.current = [];
    arcLightsRef.current = [];

    angles.forEach((angle, idx) => {
      const elecGroup = new THREE.Group();
      const x = Math.cos(angle) * electrodePitch;
      const z = Math.sin(angle) * electrodePitch;
      elecGroup.position.set(x, 12, z);

      // Graphite Column Body
      const elecColGeo = new THREE.CylinderGeometry(electrodeRadius, electrodeRadius, electrodeLength, 32);
      const elecColMat = new THREE.MeshStandardMaterial({
        color: 0x221f1e, // Warm dark graphite
        roughness: 0.7,
        metalness: 0.35,
      });
      const elecCol = new THREE.Mesh(elecColGeo, elecColMat);
      elecCol.castShadow = true;
      elecGroup.add(elecCol);

      // Electrode Tip (Incandescent bevel where electric arc strikes)
      const tipGeo = new THREE.ConeGeometry(electrodeRadius, 1.4, 32);
      const tipMat = new THREE.MeshStandardMaterial({
        color: 0xff9800,
        emissive: 0xff7043,
        emissiveIntensity: 0.8,
        roughness: 0.4,
      });
      const tip = new THREE.Mesh(tipGeo, tipMat);
      tip.rotation.x = Math.PI;
      tip.position.y = -electrodeLength / 2 - 0.7;
      elecGroup.add(tip);

      // Copper Hydraulic Clamping Ring at top
      const clampGeo = new THREE.CylinderGeometry(electrodeRadius + 0.4, electrodeRadius + 0.4, 2.2, 24);
      const clampMat = new THREE.MeshStandardMaterial({
        color: 0xb87333, // Warm Cast Copper
        metalness: 0.85,
        roughness: 0.3,
      });
      const clamp = new THREE.Mesh(clampGeo, clampMat);
      clamp.position.y = electrodeLength / 2 - 2;
      elecGroup.add(clamp);

      // Flexible Water-Cooled Busbar Cables
      const busbarGeo = new THREE.TorusGeometry(1.8, 0.15, 8, 24, Math.PI);
      const busbarMat = new THREE.MeshStandardMaterial({ color: 0xcd7f32, metalness: 0.7, roughness: 0.4 });
      const busbar = new THREE.Mesh(busbarGeo, busbarMat);
      busbar.rotation.z = Math.PI / 4;
      busbar.position.set(0.6, electrodeLength / 2 - 1, 0);
      elecGroup.add(busbar);

      furnaceGroup.add(elecGroup);
      electrodesRef.current.push(elecGroup);

      // Dynamic Electric Plasma Arc between tip and molten bath
      const arcPoints = [
        new THREE.Vector3(x, 4.0, z),
        new THREE.Vector3(x + 0.2, 3.6, z - 0.1),
        new THREE.Vector3(x - 0.15, 3.4, z + 0.15),
        new THREE.Vector3(x, 3.2, z),
      ];
      const arcGeo = new THREE.BufferGeometry().setFromPoints(arcPoints);
      const arcMat = new THREE.LineBasicMaterial({
        color: 0xfff9c4, // Warm Golden Sunburst / Incandescent Flash
        linewidth: 4,
      });
      const arcLine = new THREE.Line(arcGeo, arcMat);
      furnaceGroup.add(arcLine);
      arcsRef.current.push(arcLine);

      // Arc Point Light
      const arcLight = new THREE.PointLight(0xffca28, 2.8, 12, 1.5);
      arcLight.position.set(x, 3.5, z);
      furnaceGroup.add(arcLight);
      arcLightsRef.current.push(arcLight);
    });

    // 9. 3D Billowing Smoke Particle System for Chimney Off-Gas (Volatile SiO plume)
    const particleCount = 220;
    const smokeGeo = new THREE.BufferGeometry();
    const smokePositions = new Float32Array(particleCount * 3);
    const smokeVelocities: { x: number; y: number; z: number; life: number; maxLife: number }[] = [];

    const chimneyTop = new THREE.Vector3(7, furnaceHeight + 12, -5);

    for (let i = 0; i < particleCount; i++) {
      smokePositions[i * 3] = chimneyTop.x + (Math.random() - 0.5) * 1.5;
      smokePositions[i * 3 + 1] = chimneyTop.y + Math.random() * 8;
      smokePositions[i * 3 + 2] = chimneyTop.z + (Math.random() - 0.5) * 1.5;

      smokeVelocities.push({
        x: (Math.random() - 0.3) * 0.04,
        y: 0.08 + Math.random() * 0.09,
        z: (Math.random() - 0.5) * 0.04,
        life: Math.random() * 100,
        maxLife: 90 + Math.random() * 50,
      });
    }

    smokeGeo.setAttribute('position', new THREE.BufferAttribute(smokePositions, 3));
    smokePosArrayRef.current = smokePositions;

    // Create particle sprite texture
    const pCanvas = document.createElement('canvas');
    pCanvas.width = 64;
    pCanvas.height = 64;
    const pCtx = pCanvas.getContext('2d');
    if (pCtx) {
      const grad = pCtx.createRadialGradient(32, 32, 0, 32, 32, 32);
      grad.addColorStop(0, 'rgba(235, 230, 220, 0.85)');
      grad.addColorStop(0.5, 'rgba(215, 205, 190, 0.45)');
      grad.addColorStop(1, 'rgba(200, 190, 180, 0)');
      pCtx.fillStyle = grad;
      pCtx.fillRect(0, 0, 64, 64);
    }
    const smokeTex = new THREE.CanvasTexture(pCanvas);

    const smokeMat = new THREE.PointsMaterial({
      size: 2.2,
      map: smokeTex,
      transparent: true,
      opacity: 0.55,
      depthWrite: false,
      blending: THREE.NormalBlending,
    });

    const smokeParticles = new THREE.Points(smokeGeo, smokeMat);
    scene.add(smokeParticles);
    smokeParticlesRef.current = smokeParticles;

    // 10. Animation Loop
    let clock = new THREE.Clock();

    const animate = () => {
      animFrameIdRef.current = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Controls update
      controls.autoRotate = autoRotate;
      controls.autoRotateSpeed = 0.8;
      controls.update();

      // Animate Smoke plume based on sio_lost
      if (smokePosArrayRef.current && smokeParticlesRef.current) {
        const positions = smokePosArrayRef.current;
        // Dynamic opacity tied to volatile SiO loss
        const targetOpacity = Math.min(0.85, Math.max(0.18, telemetry.sio_lost * 8));
        smokeMat.opacity = THREE.MathUtils.lerp(smokeMat.opacity, targetOpacity, 0.05);
        smokeMat.size = 2.0 + telemetry.sio_lost * 25;

        for (let i = 0; i < particleCount; i++) {
          const vel = smokeVelocities[i];
          vel.life += 1;

          positions[i * 3] += vel.x + Math.sin(elapsedTime * 1.5 + i) * 0.015;
          positions[i * 3 + 1] += vel.y;
          positions[i * 3 + 2] += vel.z + Math.cos(elapsedTime * 1.2 + i) * 0.015;

          if (vel.life > vel.maxLife || positions[i * 3 + 1] > chimneyTop.y + 14) {
            vel.life = 0;
            positions[i * 3] = chimneyTop.x + (Math.random() - 0.5) * 1.5;
            positions[i * 3 + 1] = chimneyTop.y;
            positions[i * 3 + 2] = chimneyTop.z + (Math.random() - 0.5) * 1.5;
          }
        }
        smokeGeo.attributes.position.needsUpdate = true;
      }

      // Animate Molten Pool liquid shader & ripples
      if (moltenBathMeshRef.current) {
        const temp = telemetry.temperature;
        // Interpolate molten color from Cherry Red (1450C) to Radiant Incandescent Gold (1866C+)
        const normalizedTemp = Math.max(0, Math.min(1, (temp - 1450) / (1950 - 1450)));
        const moltenColor = new THREE.Color();
        if (normalizedTemp < 0.6) {
          // 1450 - 1750C: Cherry red to terracotta
          moltenColor.lerpColors(new THREE.Color('#8B0000'), new THREE.Color('#D84315'), normalizedTemp / 0.6);
        } else {
          // 1750 - 1950C: Terracotta to Radiant Molten Gold
          moltenColor.lerpColors(new THREE.Color('#D84315'), new THREE.Color('#FFB300'), (normalizedTemp - 0.6) / 0.4);
        }

        const mat = moltenBathMeshRef.current.material as THREE.MeshStandardMaterial;
        mat.color.copy(moltenColor);
        mat.emissive.copy(moltenColor);
        mat.emissiveIntensity = 0.65 + Math.sin(elapsedTime * 3) * 0.15;

        // Subtle fluid level breathing
        moltenBathMeshRef.current.position.y = 3.2 + Math.sin(elapsedTime * 1.8) * 0.04;
      }

      // Animate Electrodes translation based on electrode_delta and PPO actions
      const targetDeltaY = (telemetry.electrode_delta || 0) * 0.04;
      electrodesRef.current.forEach((el, i) => {
        const offsetPhase = i * 2.0;
        const targetY = 12 + targetDeltaY + Math.sin(elapsedTime * 0.8 + offsetPhase) * 0.08;
        el.position.y = THREE.MathUtils.lerp(el.position.y, targetY, 0.08);

        // Electric arc jitter
        if (arcsRef.current[i]) {
          const arc = arcsRef.current[i];
          const x = el.position.x;
          const z = el.position.z;
          const tipBottomY = el.position.y - electrodeLength / 2 - 1.4;
          const bathY = 3.2;

          const arcPos = arc.geometry.attributes.position as THREE.BufferAttribute;
          const jitter1 = (Math.random() - 0.5) * 0.35;
          const jitter2 = (Math.random() - 0.5) * 0.35;

          arcPos.setXYZ(0, x, tipBottomY, z);
          arcPos.setXYZ(1, x + jitter1, (tipBottomY + bathY) * 0.65, z + jitter2);
          arcPos.setXYZ(2, x - jitter2, (tipBottomY + bathY) * 0.35, z - jitter1);
          arcPos.setXYZ(3, x, bathY, z);
          arcPos.needsUpdate = true;
        }

        // Arc light flickering
        if (arcLightsRef.current[i]) {
          const light = arcLightsRef.current[i];
          light.intensity = 2.4 + (Math.random() - 0.5) * 1.2;
        }
      });

      renderer.render(scene, camera);
    };

    animate();

    // 11. Resize handling
    const handleResize = () => {
      if (!containerRef.current || !rendererRef.current || !cameraRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      cameraRef.current.aspect = w / h;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animFrameIdRef.current) cancelAnimationFrame(animFrameIdRef.current);
      if (rendererRef.current && rendererRef.current.domElement) {
        rendererRef.current.dispose();
      }
    };
  }, [cutawayActive]);

  // Camera Presets
  const setCameraPreset = (preset: 'ISOMETRIC' | 'HEARTH' | 'TOP') => {
    setActiveCamPreset(preset);
    if (!cameraRef.current || !controlsRef.current) return;

    if (preset === 'ISOMETRIC') {
      cameraRef.current.position.set(38, 26, 38);
      controlsRef.current.target.set(0, 7, 0);
    } else if (preset === 'HEARTH') {
      cameraRef.current.position.set(18, 9, 18);
      controlsRef.current.target.set(0, 4, 0);
    } else if (preset === 'TOP') {
      cameraRef.current.position.set(0, 52, 12);
      controlsRef.current.target.set(0, 8, 0);
    }
    controlsRef.current.update();
  };

  return (
    <div className="relative w-full h-full min-h-[500px] overflow-hidden rounded-xl border border-[#DDCFB4] bg-[#EFE8D8] shadow-sm select-none">
      {/* 3D Canvas Container */}
      <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Top Floating Viewport Control Bar */}
      <div className="absolute top-3 left-3 right-3 flex items-center justify-between pointer-events-none z-10">
        <div className="flex items-center gap-2 pointer-events-auto bg-[#FAF7F0]/95 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#DDCFB4] shadow-xs text-xs text-[#2C211B]">
          <span className="font-semibold text-[#8D4925] flex items-center gap-1.5">
            <Flame className="w-3.5 h-3.5 text-[#D84315]" />
            28.5 MW Submerged Arc Furnace Twin
          </span>
          <span className="text-[#C8B99C]">|</span>
          <span className="text-[#6E5D53]">Refractory: Alumina Firebrick</span>
          <span className="text-[#C8B99C]">|</span>
          <span className="font-mono text-[#D84315] font-medium">Hearth: {telemetry.temperature.toFixed(1)}°C</span>
        </div>

        {/* Viewport Action Controls */}
        <div className="flex items-center gap-1.5 pointer-events-auto bg-[#FAF7F0]/95 backdrop-blur-md p-1 rounded-lg border border-[#DDCFB4] shadow-xs">
          <button
            onClick={() => setCameraPreset('ISOMETRIC')}
            className={`px-2.5 py-1 text-xs font-medium rounded transition-colors whitespace-nowrap ${
              activeCamPreset === 'ISOMETRIC'
                ? 'bg-[#EFE8D8] text-[#2C211B] shadow-xs font-semibold'
                : 'text-[#6E5D53] hover:text-[#2C211B]'
            }`}
          >
            Isometric
          </button>
          <button
            onClick={() => setCameraPreset('HEARTH')}
            className={`px-2.5 py-1 text-xs font-medium rounded transition-colors whitespace-nowrap ${
              activeCamPreset === 'HEARTH'
                ? 'bg-[#EFE8D8] text-[#2C211B] shadow-xs font-semibold'
                : 'text-[#6E5D53] hover:text-[#2C211B]'
            }`}
          >
            Hearth Arc
          </button>
          <button
            onClick={() => setCameraPreset('TOP')}
            className={`px-2.5 py-1 text-xs font-medium rounded transition-colors whitespace-nowrap ${
              activeCamPreset === 'TOP'
                ? 'bg-[#EFE8D8] text-[#2C211B] shadow-xs font-semibold'
                : 'text-[#6E5D53] hover:text-[#2C211B]'
            }`}
          >
            Top Delta
          </button>
          <div className="h-4 w-px bg-[#DDCFB4] mx-1" />
          <button
            onClick={() => setCutawayActive(!cutawayActive)}
            title="Toggle Cutaway Shell"
            className={`p-1.5 rounded text-xs transition-colors ${
              cutawayActive ? 'bg-[#EFE8D8] text-[#8D4925]' : 'text-[#6E5D53] hover:text-[#2C211B]'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setAutoRotate(!autoRotate)}
            title="Toggle Orbit Rotation"
            className={`p-1.5 rounded text-xs transition-colors ${
              autoRotate ? 'bg-[#EFE8D8] text-[#D84315]' : 'text-[#6E5D53] hover:text-[#2C211B]'
            }`}
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Floating 3D Telemetry Overlay HUD Markers */}
      <div className="absolute left-4 bottom-4 pointer-events-none z-10 hidden sm:flex flex-col gap-1.5 text-[11px] text-[#423229]">
        <div className="bg-[#FAF7F0]/90 backdrop-blur-md px-2.5 py-1.5 rounded border border-[#DDCFB4] shadow-xs">
          <div className="text-[10px] uppercase font-semibold text-[#8D4925] tracking-wide">3-Electrode Söderberg Delta</div>
          <div className="font-mono text-[#2C211B] mt-0.5">
            E1: <span className="text-[#D84315] font-semibold">240 mm</span> · E2: 245 mm · E3: 238 mm
          </div>
          <div className="text-[10px] text-[#6E5D53] mt-0.5">
            RL Penetration Delta: <span className="font-mono font-semibold">{telemetry.electrode_delta > 0 ? `+${telemetry.electrode_delta}` : telemetry.electrode_delta} mm/step</span>
          </div>
        </div>

        <div className="bg-[#FAF7F0]/90 backdrop-blur-md px-2.5 py-1.5 rounded border border-[#DDCFB4] shadow-xs flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#FFB300] shadow-[0_0_8px_#FFB300]" />
          <span>Molten Si Pool: <strong className="font-mono text-[#2C211B]">1866.6°C</strong></span>
          <span className="text-[#2E7D32] bg-[#E8F5E9] px-1.5 py-0.2 rounded text-[10px] font-medium">Sweet Spot</span>
        </div>
      </div>

      {/* Orbit Helper Tip */}
      <div className="absolute right-4 top-14 pointer-events-none text-[10px] text-[#8D4925]/80 bg-[#FAF7F0]/80 px-2 py-0.5 rounded border border-[#DDCFB4]/60 hidden md:block">
        Left Click Drag: Rotate · Scroll: Zoom · Right Click: Pan
      </div>
    </div>
  );
};
