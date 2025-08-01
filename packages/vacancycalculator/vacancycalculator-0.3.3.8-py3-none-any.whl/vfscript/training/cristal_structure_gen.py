import os
import numpy as np
from pathlib import Path
from typing import Tuple, Union

class CrystalStructureGenerator:
    """
    Genera una estructura BCC o FCC que cubre completamente la caja del archivo de defecto,
    alineada de modo que tenga el mismo centro. Escribe un dump LAMMPS.
    """
    def __init__(self, config: dict, out_dir: Union[str, Path]):
        self.config = config
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # Leer ruta del dump de defecto
        if 'defect' in config:
            defect = config['defect']
        elif 'CONFIG' in config and isinstance(config['CONFIG'], list) and config['CONFIG']:
            defect = config['CONFIG'][0].get('defect')
        else:
            defect = None
        if not defect:
            raise ValueError("No se encontró la clave 'defect' en la configuración")
        # defect puede ser lista o cadena
        self.path_defect = Path(defect[0] if isinstance(defect, list) else defect)

        # Parámetros de la red
        self.structure_type = config['generate_relax'][0].lower()
        self.lattice = float(config['generate_relax'][1])

        # Leer caja y calcular centro y dimensiones
        self._read_defect_box()

        # Calcular cuántas repeticiones de celda base harán falta
        reps = np.ceil(self.box_dims / self.lattice).astype(int)
        self.reps = tuple(reps.tolist())

    def _read_defect_box(self):
        text = self.path_defect.read_text().splitlines()
        idx = next((i for i, l in enumerate(text) if l.startswith('ITEM: BOX BOUNDS')), None)
        if idx is None:
            raise ValueError("No encontré 'ITEM: BOX BOUNDS' en el dump{})".format(self.path_defect))
        bounds = []
        for line in text[idx+1:idx+4]:
            lo, hi = map(float, line.split()[:2])
            bounds.extend([lo, hi])
        self.box_limits = tuple(bounds)
        xlo, xhi, ylo, yhi, zlo, zhi = bounds
        self.box_center = np.array([(xlo + xhi)/2, (ylo + yhi)/2, (zlo + zhi)/2])
        self.box_dims = np.array([xhi-xlo, yhi-ylo, zhi-zlo])

    def generate(self) -> Path:
        """
        Genera el dump 'relax_structure.dump' con la red perfecta.
        """
        coords, dims = self._build_replica(self.reps)
        # Centrar réplica en origen
        coords_centered = coords - dims/2
        # Alinear al centro de la caja del defecto
        coords_aligned = coords_centered + self.box_center
        # Filtrar puntos dentro de la caja original
        xlo, xhi, ylo, yhi, zlo, zhi = self.box_limits
        mask = (
            (coords_aligned[:,0] >= xlo) & (coords_aligned[:,0] < xhi) &
            (coords_aligned[:,1] >= ylo) & (coords_aligned[:,1] < yhi) &
            (coords_aligned[:,2] >= zlo) & (coords_aligned[:,2] < zhi)
        )
        coords_final = coords_aligned[mask]
        # Escribir dump
        out_file = self.out_dir / 'relax_structure.dump'
        self._write_dump(coords_final, self.box_limits, out_file)
        return out_file

    def _build_replica(self, reps: Tuple[int, int, int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera puntos de la red (FCC o BCC) replicando la celda base reps veces.
        Devuelve (coords, dims), donde dims = reps * lattice.
        """
        if self.structure_type == 'fcc':
            base = np.array([[0,0,0],[0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5]]) * self.lattice
        elif self.structure_type == 'bcc':
            base = np.array([[0,0,0],[0.5,0.5,0.5]]) * self.lattice
        else:
            raise ValueError(f"Estructura desconocida: {self.structure_type}")
        reps_arr = np.array(reps)
        dims = reps_arr * self.lattice
        coords = []
        for i in range(reps[0]):
            for j in range(reps[1]):
                for k in range(reps[2]):
                    origin = np.array([i,j,k]) * self.lattice
                    for p in base:
                        coords.append(origin + p)
        coords = np.array(coords)
        # Aplicar periodicidad en celda generada
        coords = np.mod(coords, dims)
        # Eliminar duplicados por redondeo
        coords_unique = np.unique(np.round(coords,6),axis=0)
        return coords_unique, dims

    def _write_dump(self, coords: np.ndarray, box: Tuple[float,float,float,float,float,float], out_file: Path):
        xlo,xhi,ylo,yhi,zlo,zhi = box
        with out_file.open('w') as f:
            f.write("ITEM: TIMESTEP\n0\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{len(coords)}\n")
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(f"{xlo} {xhi}\n")
            f.write(f"{ylo} {yhi}\n")
            f.write(f"{zlo} {zhi}\n")
            f.write("ITEM: ATOMS id type x y z\n")
            for idx,(x,y,z) in enumerate(coords, start=1):
                f.write(f"{idx} 1 {x:.6f} {y:.6f} {z:.6f}\n")
