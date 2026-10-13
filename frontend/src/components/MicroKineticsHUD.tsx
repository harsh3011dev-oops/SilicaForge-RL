import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Minimize2, Maximize2, Zap, Play, Pause, RefreshCw, Activity } from 'lucide-react';

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

  const atomsRef = useRef<AtomParticle[]>([]);
  const bondsGroupRef = useRef<THREE.Group | null>(null);

  useEffect(() => {
    if (isMinimized || !containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth || 340;
    const height = container.clientHeight || 210;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#FAF7F0'); // Warm porcelain

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, 16);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    rendererRef.current = renderer;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Warm ambient and key lighting
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

    // Group for dynamic bond lines
    const bondsGroup = new THREE.Group();
    scene.add(bondsGroup);
    bondsGroupRef.current = bondsGroup;

    // Materials for atoms
    // Silicon: Warm Teal / Cyan-slate (#00838F / #0097A7)
    const siMat = new THREE.MeshStandardMaterial({
      color: 0x00838f,
      roughness: 0.3,
      metalness: 0.6,
    });
    // Oxygen: Terracotta Red (#D84315)
    const oMat = new THREE.MeshStandardMaterial({
      color: 0xd84315,
      roughness: 0.4,
      metalness: 0.2,
    });
    // Carbon reducing agent: Warm Graphite Slate (#37474F / #263238)
    const cMat = new THREE.MeshStandardMaterial({
      color: 0x37474f,
      roughness: 0.8,
      metalness: 0.4,
    });
    // Gaseous CO molecule color (warm gold-smoke)
    const coMat = new THREE.MeshStandardMaterial({
      color: 0xe65100,
      emissive: 0xffa000,
      emissiveIntensity: 0.4,
      roughness: 0.3,
    });

    const siGeo = new THREE.SphereGeometry(0.55, 20, 20);
    const oGeo = new THREE.SphereGeometry(0.38, 18, 18);
    const cGeo = new THREE.SphereGeometry(0.48, 18, 18);

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

    // Spawn Oxygen atoms (part of SiO2 quartz molecules)
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

    atomsRef.current = atoms;

    let animId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      if (isPaused) return;

      const delta = clock.getDelta();
      const speed = thermalMultiplier * (temperature > 1850 ? 1.4 : 0.8);

      // Clean old bond lines
      while (bondsGroup.children.length > 0) {
        const obj = bondsGroup.children[0];
        bondsGroup.remove(obj);
      }

      // Physics: Brownian motion & reaction kinetics
      atoms.forEach((atom) => {
        atom.mesh.position.addScaledVector(atom.velocity, speed * 25 * delta);

        // Boundary reflection inside warm reaction chamber
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

        // CO evolution: Gaseous CO naturally ascends toward top flue
        if (atom.type === 'CO') {
          atom.velocity.y = Math.abs(atom.velocity.y) * 0.8 + 0.02;
          if (atom.mesh.position.y >= halfY - 0.2) {
            // Recycled at bottom
            atom.mesh.position.y = -halfY + 0.5;
          }
        }

        // Si condensation: Pure Si drifts downward to form molten liquid lattice at crucible floor
        if (atom.type === 'Si' && atom.reacted) {
          atom.velocity.y = -Math.abs(atom.velocity.y) * 0.4 - 0.01;
        }
      });

      // Atom-to-atom reaction collision checking
      // At reaction temp (>1800°C), C + O collide and form CO, freeing Si to condense!
      if (temperature >= 1800) {
        for (let i = 0; i < atoms.length; i++) {
          for (let j = i + 1; j < atoms.length; j++) {
            const a = atoms[i];
            const b = atoms[j];
            const dist = a.mesh.position.distanceTo(b.mesh.position);

            // Draw covalent/ionic bonds when atoms are close
            if (dist < 1.6 && !a.reacted && !b.reacted) {
              const points = [a.mesh.position, b.mesh.position];
              const bondGeo = new THREE.BufferGeometry().setFromPoints(points);
              const bondMat = new THREE.LineBasicMaterial({
                color: 0xffb74d,
                transparent: true,
                opacity: 0.65,
              });
              const line = new THREE.Line(bondGeo, bondMat);
              bondsGroup.add(line);
            }

            // Chemical reaction trigger
            if (dist < 0.85 && ((a.type === 'O' && b.type === 'C') || (a.type === 'C' && b.type === 'O'))) {
              // Oxygen binds to Carbon -> CO gas
              const oAtom = a.type === 'O' ? a : b;
              const cAtom = a.type === 'C' ? a : b;

              if (!oAtom.reacted && !cAtom.reacted) {
                oAtom.reacted = true;
                cAtom.reacted = true;
                cAtom.type = 'CO';
                cAtom.mesh.material = coMat;
                oAtom.mesh.scale.set(0.6, 0.6, 0.6);

                // Find nearest unreacted Si and mark as condensed
                const nearestSi = atoms.find((at) => at.type === 'Si' && !at.reacted);
                if (nearestSi) {
                  nearestSi.reacted = true;
                  (nearestSi.mesh.material as THREE.MeshStandardMaterial).emissive = new THREE.Color(0x00bcd4);
                  (nearestSi.mesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.5;
                }

                setReactionStats((prev) => ({
                  ...prev,
                  coEvolved: prev.coEvolved + 1,
                  siCondensed: prev.siCondensed + 1,
                }));
              }
            }
          }
        }
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
      if (rendererRef.current && rendererRef.current.domElement) {
        rendererRef.current.dispose();
      }
    };
  }, [isMinimized, isPaused, thermalMultiplier, temperature]);

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
