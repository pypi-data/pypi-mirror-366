import os
import numpy as np
from pathlib import Path
from typing import Tuple

class CrystalStructureGenerator:
    """
    Genera una estructura BCC o FCC replicada y alineada al mismo centro
    que la caja del archivo de defecto (self.path_defect). Escribe un dump LAMMPS.
    """
    def __init__(self, config: dict, out_dir: Path):
        self.config = config
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # Obtener ruta del dump de defecto
        defect_cfg = None
        if 'defect' in config:
            defect_cfg = config['defect']
        elif 'CONFIG' in config and isinstance(config['CONFIG'], list) and config['CONFIG']:
            first = config['CONFIG'][0]
            if 'defect' in first:
                defect_cfg = first['defect']
        if defect_cfg is None:
            raise ValueError("No se encontró la clave 'defect' en la configuración")
        path_str = defect_cfg[0] if isinstance(defect_cfg, list) else defect_cfg
        self.path_defect = Path(path_str)

        # Parámetros de la red a generar
        self.structure_type = config['generate_relax'][0]
        self.lattice = float(config['generate_relax'][1])
        rx, ry, rz = map(int, config['generate_relax'][2:5])
        self.reps = (rx, ry, rz)

        # Leer límites de caja y centro del defect
        self._read_defect_box()

    def _read_defect_box(self):
        if not self.path_defect.exists():
            raise FileNotFoundError(f"No se encontró: {self.path_defect}")
        lines = self.path_defect.read_text().splitlines()
        idx = next((i for i, l in enumerate(lines)
                    if l.strip().startswith('ITEM: BOX BOUNDS')), None)
        if idx is None or idx + 3 > len(lines):
            raise ValueError("No se encontró BOX BOUNDS de 3 líneas en el dump")
        bounds = []
        for line in lines[idx+1:idx+4]:
            lo, hi = map(float, line.split()[:2])
            bounds.extend([lo, hi])
        self.box_limits = tuple(bounds)
        xlo, xhi, ylo, yhi, zlo, zhi = self.box_limits
        self.box_center = np.array([(xlo + xhi)/2,
                                    (ylo + yhi)/2,
                                    (zlo + zhi)/2])

    def generate(self) -> Path:
        """
        Construye la réplica de la red, la alinea al mismo centro
        que la muestra de defecto y escribe el dump resultante.
        """
        coords, _dims = self._build_replica(self.reps)
        # Calcular centro de los puntos generados
        coords_center = coords.mean(axis=0)
        # Alinear al centro de la caja del defecto
        coords_aligned = coords - coords_center + self.box_center

        # Usar los mismos límites de caja del defecto
        xlo, xhi, ylo, yhi, zlo, zhi = self.box_limits
        box = (xlo, xhi, ylo, yhi, zlo, zhi)

        out_file = self.out_dir / 'relax_structure.dump'
        self._write_dump(coords_aligned, box, out_file)
        return out_file

    def _build_replica(self, reps: Tuple[int, int, int]) -> Tuple[np.ndarray, np.ndarray]:
        # Base de la celda según estructura
        if self.structure_type.lower() == 'fcc':
            base = np.array([[0,0,0], [0.5,0.5,0], [0.5,0,0.5], [0,0.5,0.5]]) * self.lattice
        elif self.structure_type.lower() == 'bcc':
            base = np.array([[0,0,0], [0.5,0.5,0.5]]) * self.lattice
        else:
            raise ValueError(f"Tipo no soportado: {self.structure_type}")
        reps_arr = np.array(reps)
        dims = reps_arr * self.lattice

        coords = []
        for i in range(reps[0]):
            for j in range(reps[1]):
                for k in range(reps[2]):
                    origin = np.array([i, j, k]) * self.lattice
                    for p in base:
                        coords.append(origin + p)
        coords = np.array(coords)
        # Aplicar periodicidad en celda ideal
        coords = np.mod(coords, dims)
        # Eliminar duplicados redondeando
        unique = np.unique(np.round(coords, 6), axis=0)
        return unique, dims

    def _write_dump(self, coords: np.ndarray, box: Tuple[float, float, float, float, float, float], out_file: Path):
        xlo, xhi, ylo, yhi, zlo, zhi = box
        with out_file.open('w') as f:
            f.write("ITEM: TIMESTEP\n0\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{len(coords)}\n")
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(f"{xlo} {xhi}\n")
            f.write(f"{ylo} {yhi}\n")
            f.write(f"{zlo} {zhi}\n")
            f.write("ITEM: ATOMS id type x y z\n")
            for idx, (x, y, z) in enumerate(coords, start=1):
                f.write(f"{idx} 1 {x:.6f} {y:.6f} {z:.6f}\n")
