import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Minimize2, Maximize2, Zap, Play, Pause, Activity } from 'lucide-react';

interface MicroKineticsHUDProps {
  temperature: number;
  cSiRatio: number;
}

interface AtomParticle {
  mesh: THREE.Mesh;
  type: 'Si' | 'O' | 'C' | 'CO';
  velocity: THREE.Vector3;
  reacted: boolean;
}

export const MicroKineticsHUD: React.FC<MicroKineticsHUDProps> = ({
  temperature,
  cSiRatio,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const [isMinimized, setIsMinimized] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [thermalMultiplier, setThermalMultiplier] = useState<number>(1.2);
  const [reactionStats, setReactionStats] = useState({
    sio2Count: 14,
    cCount: 28,
    coEvolved: 18,
    siCondensed: 9,
  });

  // Dynamic references so animation loop doesn't restart on prop updates
  const tempRef = useRef(temperature);
  tempRef.current = temperature;

  const pausedRef = useRef(isPaused);
  pausedRef.current = isPaused;

  const multiplierRef = useRef(thermalMultiplier);
  multiplierRef.current = thermalMultiplier;

  const statsRef = useRef({
    coEvolved: 18,
    siCondensed: 9,
  });

  useEffect(() => {
    if (isMinimized || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth || 340;
    const height = container.clientHeight || 210;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#FAF7F0'); // Warm porcelain

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, 16);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'low-power' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    rendererRef.current = renderer;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Warm ambient and directional lighting
    const amb = new THREE.AmbientLight(0xfff8e7, 1.2);
    scene.add(amb);
    const dir = new THREE.DirectionalLight(0xffecd2, 1.4);
    dir.position.set(5, 8, 10);
    scene.add(dir);

    // Bounding reaction volume wireframe (warm bronze cage)
    const boxGeo = new THREE.BoxGeometry(11, 7, 6);
    const boxEdges = new THREE.EdgesGeometry(boxGeo);
    const boxMat = new THREE.LineBasicMaterial({ color: 0xd4c5b0, transparent: true, opacity: 0.7 });
    const wireframeBox = new THREE.LineSegments(boxEdges, boxMat);
    scene.add(wireframeBox);

    // Materials for atoms (reused across instances)
    const siMat = new THREE.MeshStandardMaterial({
      color: 0x00838f,
      roughness: 0.3,
      metalness: 0.6,
    });
    const oMat = new THREE.MeshStandardMaterial({
      color: 0xd84315,
      roughness: 0.4,
      metalness: 0.2,
    });
    const cMat = new THREE.MeshStandardMaterial({
      color: 0x37474f,
      roughness: 0.8,
      metalness: 0.4,
    });
    const coMat = new THREE.MeshStandardMaterial({
      color: 0xe65100,
      emissive: 0xffa000,
      emissiveIntensity: 0.4,
      roughness: 0.3,
    });

    const siGeo = new THREE.SphereGeometry(0.55, 14, 14);
    const oGeo = new THREE.SphereGeometry(0.38, 12, 12);
    const cGeo = new THREE.SphereGeometry(0.48, 12, 12);

    const atoms: AtomParticle[] = [];

    // Spawn Silicon atoms
    for (let i = 0; i < 8; i++) {
      const mesh = new THREE.Mesh(siGeo, siMat);
      mesh.position.set((Math.random() - 0.5) * 8, (Math.random() - 0.5) * 4 - 0.8, (Math.random() - 0.5) * 4);
      scene.add(mesh);
      atoms.push({
        mesh,
        type: 'Si',
        velocity: new THREE.Vector3((Math.random() - 0.5) * 0.04, (Math.random() - 0.5) * 0.03, (Math.random() - 0.5) * 0.04),
        reacted: false,
      });
    }

    // Spawn Oxygen atoms
    for (let i = 0; i < 16; i++) {
      const mesh = new THREE.Mesh(oGeo, oMat);
      mesh.position.set((Math.random() - 0.5) * 8, (Math.random() - 0.5) * 4, (Math.random() - 0.5) * 4);
      scene.add(mesh);
      atoms.push({
        mesh,
        type: 'O',
        velocity: new THREE.Vector3((Math.random() - 0.5) * 0.05, (Math.random() - 0.5) * 0.05, (Math.random() - 0.5) * 0.05),
        reacted: false,
      });
    }

    // Spawn Carbon reducing agents
    for (let i = 0; i < 16; i++) {
      const mesh = new THREE.Mesh(cGeo, cMat);
      mesh.position.set((Math.random() - 0.5) * 8, (Math.random() - 0.5) * 4, (Math.random() - 0.5) * 4);
      scene.add(mesh);
      atoms.push({
        mesh,
        type: 'C',
        velocity: new THREE.Vector3((Math.random() - 0.5) * 0.04, (Math.random() - 0.5) * 0.04, (Math.random() - 0.5) * 0.04),
        reacted: false,
      });
    }

    // Static Pre-allocated Dynamic Bond Lines buffer (Zero GC allocation per frame!)
    const MAX_BONDS = 32;
    const bondPositions = new Float32Array(MAX_BONDS * 2 * 3);
    const bondGeo = new THREE.BufferGeometry();
    const bondPosAttr = new THREE.BufferAttribute(bondPositions, 3);
    bondPosAttr.setUsage(THREE.DynamicDrawUsage);
    bondGeo.setAttribute('position', bondPosAttr);
    const bondMat = new THREE.LineBasicMaterial({
      color: 0xffb74d,
      transparent: true,
      opacity: 0.65,
    });
    const bondSegments = new THREE.LineSegments(bondGeo, bondMat);
    scene.add(bondSegments);

    let animId: number;
    let lastTime = performance.now();
    let lastStatSync = performance.now();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      if (pausedRef.current) return;

      const now = performance.now();
      const delta = Math.min((now - lastTime) * 0.001, 0.08);
      lastTime = now;

      const curTemp = tempRef.current;
      const speed = multiplierRef.current * (curTemp > 1850 ? 1.4 : 0.8);

      // Physics: Brownian motion inside reaction cage
      atoms.forEach((atom) => {
        atom.mesh.position.addScaledVector(atom.velocity, speed * 25 * delta);

        const halfX = 4.8;
        const halfY = 3.0;
        const halfZ = 2.4;

        if (Math.abs(atom.mesh.position.x) > halfX) {
          atom.velocity.x *= -1;
          atom.mesh.position.x = Math.sign(atom.mesh.position.x) * halfX;
        }
        if (Math.abs(atom.mesh.position.y) > halfY) {
          atom.velocity.y *= -1;
          atom.mesh.position.y = Math.sign(atom.mesh.position.y) * halfY;
        }
        if (Math.abs(atom.mesh.position.z) > halfZ) {
          atom.velocity.z *= -1;
          atom.mesh.position.z = Math.sign(atom.mesh.position.z) * halfZ;
        }

        // CO evolution: Gaseous CO ascends
        if (atom.type === 'CO') {
          atom.velocity.y = Math.abs(atom.velocity.y) * 0.8 + 0.02;
          if (atom.mesh.position.y >= halfY - 0.2) {
            atom.mesh.position.y = -halfY + 0.5;
          }
        }

        // Si condensation: Pure Si drifts downward
        if (atom.type === 'Si' && atom.reacted) {
          atom.velocity.y = -Math.abs(atom.velocity.y) * 0.4 - 0.01;
        }
      });

      // Update bonds in pre-allocated buffer
      let bondCount = 0;
      if (curTemp >= 1800) {
        for (let i = 0; i < atoms.length && bondCount < MAX_BONDS; i++) {
          for (let j = i + 1; j < atoms.length && bondCount < MAX_BONDS; j++) {
            const a = atoms[i];
            const b = atoms[j];
            const dist = a.mesh.position.distanceTo(b.mesh.position);

            if (dist < 1.6 && !a.reacted && !b.reacted) {
              const idx = bondCount * 6;
              bondPositions[idx] = a.mesh.position.x;
              bondPositions[idx + 1] = a.mesh.position.y;
              bondPositions[idx + 2] = a.mesh.position.z;
              bondPositions[idx + 3] = b.mesh.position.x;
              bondPositions[idx + 4] = b.mesh.position.y;
              bondPositions[idx + 5] = b.mesh.position.z;
              bondCount++;
            }

            // Chemical reaction trigger
            if (dist < 0.85 && ((a.type === 'O' && b.type === 'C') || (a.type === 'C' && b.type === 'O'))) {
              const oAtom = a.type === 'O' ? a : b;
              const cAtom = a.type === 'C' ? a : b;

              if (!oAtom.reacted && !cAtom.reacted) {
                oAtom.reacted = true;
                cAtom.reacted = true;
                cAtom.type = 'CO';
                cAtom.mesh.material = coMat;
                oAtom.mesh.scale.set(0.6, 0.6, 0.6);

                const nearestSi = atoms.find((at) => at.type === 'Si' && !at.reacted);
                if (nearestSi) {
                  nearestSi.reacted = true;
                  (nearestSi.mesh.material as THREE.MeshStandardMaterial).emissive = new THREE.Color(0x00bcd4);
                  (nearestSi.mesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.5;
                }

                statsRef.current.coEvolved += 1;
                statsRef.current.siCondensed += 1;
              }
            }
          }
        }
      }

      // Update bond draw range without recreating geometries
      bondGeo.setDrawRange(0, bondCount * 2);
      bondPosAttr.needsUpdate = true;

      // Throttled sync of stats to React state (every 1000ms instead of 60fps)
      if (now - lastStatSync > 1000) {
        setReactionStats((prev) => ({
          ...prev,
          coEvolved: statsRef.current.coEvolved,
          siCondensed: statsRef.current.siCondensed,
        }));
        lastStatSync = now;
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!containerRef.current || !rendererRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      rendererRef.current.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animId);
      if (rendererRef.current) {
        rendererRef.current.dispose();
        rendererRef.current.forceContextLoss();
        if (container.contains(rendererRef.current.domElement)) {
          container.removeChild(rendererRef.current.domElement);
        }
        rendererRef.current = null;
      }
      siGeo.dispose();
      oGeo.dispose();
      cGeo.dispose();
      boxGeo.dispose();
      boxEdges.dispose();
      bondGeo.dispose();
      siMat.dispose();
      oMat.dispose();
      cMat.dispose();
      coMat.dispose();
      bondMat.dispose();
      boxMat.dispose();
    };
  }, [isMinimized]);

  return (
    <div
      className={`absolute bottom-3 right-3 z-20 bg-[#FAF7F0] border border-[#DDCFB4] rounded-xl shadow-md transition-all duration-300 overflow-hidden ${
        isMinimized ? 'w-64 h-11' : 'w-84 sm:w-96'
      }`}
    >
      {/* HUD Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[#DDCFB4] bg-[#F4EFE2]/90">
        <div className="flex items-center gap-1.5 overflow-hidden">
          <Activity className="w-3.5 h-3.5 text-[#D84315] shrink-0" />
          <span className="text-[11px] font-bold text-[#2C211B] truncate tracking-tight">
            Micro-Kinetics: SiO₂ + 2C → Si + 2CO
          </span>
        </div>

        <div className="flex items-center gap-1 shrink-0">
          {!isMinimized && (
            <>
              <button
                onClick={() => setIsPaused(!isPaused)}
                title={isPaused ? 'Resume reaction' : 'Pause reaction'}
                className="p-1 text-[#6E5D53] hover:text-[#2C211B] rounded hover:bg-[#EAE2D2] transition-colors"
              >
                {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
              </button>
              <button
                onClick={() => setThermalMultiplier(thermalMultiplier === 1.2 ? 2.2 : 1.2)}
                title="Boost thermal agitation"
                className={`p-1 rounded transition-colors ${
                  thermalMultiplier > 1.5 ? 'text-[#D84315] bg-[#EAE2D2]' : 'text-[#6E5D53] hover:text-[#2C211B]'
                }`}
              >
                <Zap className="w-3 h-3" />
              </button>
            </>
          )}
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 text-[#6E5D53] hover:text-[#2C211B] rounded hover:bg-[#EAE2D2] transition-colors"
          >
            {isMinimized ? <Maximize2 className="w-3 h-3" /> : <Minimize2 className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Sub-canvas for 3D Molecular Simulation */}
          <div ref={containerRef} className="w-full h-44 bg-[#FAF7F0] relative overflow-hidden" />

          {/* Atomic Legend & Stoichiometric Lock Gauge */}
          <div className="p-2.5 bg-[#FAF7F0] border-t border-[#DDCFB4]/80 text-[11px] space-y-2">
            {/* Atom type pills */}
            <div className="flex items-center justify-between text-[10px] text-[#5D4037]">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#00838F]" />
                Silicon (Si)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#D84315]" />
                Oxygen (O)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#37474F]" />
                Carbon (C)
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-[#E65100]" />
                CO Gas (↑)
              </span>
            </div>

            {/* Stoichiometric lock bar */}
            <div>
              <div className="flex items-center justify-between text-[10px] text-[#6E5D53] mb-1">
                <span>Stoichiometric Lock (C/Si)</span>
                <span className="font-mono font-bold text-[#2C211B]">
                  {cSiRatio.toFixed(3)} <span className="text-[#2E7D32] font-semibold">(Ideal 2.000)</span>
                </span>
              </div>
              <div className="w-full bg-[#E8E1CE] h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-[#D84315] via-[#2E7D32] to-[#FFB300] h-full transition-all duration-300"
                  style={{
                    width: `${Math.min(100, Math.max(0, (cSiRatio / 2.05) * 100))}%`,
                  }}
                />
              </div>
              <div className="flex justify-between text-[9px] text-[#8D7B68] mt-0.5">
                <span>Slagging (&lt;1.96)</span>
                <span className="font-semibold text-[#2E7D32]">Optimal Target: 1.996</span>
                <span>Carbidization (&gt;2.04)</span>
              </div>
            </div>

            {/* Micro Reaction Kinetics Metrics */}
            <div className="grid grid-cols-2 gap-1.5 pt-1 border-t border-[#EAE2D2] text-[10px]">
              <div className="bg-[#F5EFE3] px-2 py-1 rounded border border-[#E0D5BE]">
                <span className="text-[#6E5D53]">CO Gas Evolved:</span>{' '}
                <strong className="font-mono text-[#D84315]">{reactionStats.coEvolved} mol</strong>
              </div>
              <div className="bg-[#F5EFE3] px-2 py-1 rounded border border-[#E0D5BE]">
                <span className="text-[#6E5D53]">Si Metal Lattice:</span>{' '}
                <strong className="font-mono text-[#00838F]">{reactionStats.siCondensed} mol</strong>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
