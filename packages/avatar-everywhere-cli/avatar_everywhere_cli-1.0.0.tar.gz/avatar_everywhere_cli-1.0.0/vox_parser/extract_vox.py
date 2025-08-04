"""
VOX File Parser
Extracts voxel data from MagicaVoxel .vox files for avatar conversion
"""

import struct
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)

class VoxelData:
    """Represents voxel data extracted from a .vox file"""
    
    def __init__(self):
        self.size = (0, 0, 0)  # x, y, z dimensions
        self.voxels = []  # List of (x, y, z, color_index) tuples
        self.palette = []  # List of RGBA color values
        self.materials = []  # Material properties
        
    def to_mesh_data(self):
        """Convert voxel data to mesh vertices and faces"""
        vertices = []
        faces = []
        vertex_index = 0
        
        # Generate cube for each voxel
        for x, y, z, color_idx in self.voxels:
            if color_idx == 0:  # Skip empty voxels
                continue
                
            # Create cube vertices (8 vertices per voxel)
            cube_vertices = [
                (x, y, z),
                (x+1, y, z),
                (x+1, y+1, z),
                (x, y+1, z),
                (x, y, z+1),
                (x+1, y, z+1),
                (x+1, y+1, z+1),
                (x, y+1, z+1)
            ]
            
            vertices.extend(cube_vertices)
            
            # Create cube faces (12 triangles per cube)
            cube_faces = [
                # Bottom face
                [vertex_index, vertex_index+1, vertex_index+2],
                [vertex_index, vertex_index+2, vertex_index+3],
                # Top face
                [vertex_index+4, vertex_index+7, vertex_index+6],
                [vertex_index+4, vertex_index+6, vertex_index+5],
                # Front face
                [vertex_index, vertex_index+4, vertex_index+5],
                [vertex_index, vertex_index+5, vertex_index+1],
                # Back face
                [vertex_index+2, vertex_index+6, vertex_index+7],
                [vertex_index+2, vertex_index+7, vertex_index+3],
                # Left face
                [vertex_index, vertex_index+3, vertex_index+7],
                [vertex_index, vertex_index+7, vertex_index+4],
                # Right face
                [vertex_index+1, vertex_index+5, vertex_index+6],
                [vertex_index+1, vertex_index+6, vertex_index+2]
            ]
            
            faces.extend(cube_faces)
            vertex_index += 8
        
        return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.uint32)

class VoxParser:
    """Parser for MagicaVoxel .vox files"""
    
    def __init__(self):
        self.default_palette = self._generate_default_palette()
    
    def parse(self, file_path: Path) -> Optional[VoxelData]:
        """Parse a .vox file and return voxel data"""
        try:
            logger.info(f"Parsing VOX file: {file_path}")
            with open(file_path, 'rb') as f:
                return self._parse_vox_data(f)
        except Exception as e:
            logger.error(f"Error parsing VOX file: {e}")
            return None
    
    def _parse_vox_data(self, file) -> VoxelData:
        """Parse the binary VOX file format"""
        voxel_data = VoxelData()
        
        # Read file header
        magic = file.read(4)
        if magic != b'VOX ':
            raise ValueError("Invalid VOX file format")
        
        version = struct.unpack('<I', file.read(4))[0]
        logger.info(f"VOX version: {version}")
        
        # Parse main chunk
        self._parse_chunk(file, voxel_data)
        
        # Use default palette if none was found
        if not voxel_data.palette:
            voxel_data.palette = self.default_palette
        
        return voxel_data
    
    def _parse_chunk(self, file, voxel_data: VoxelData):
        """Parse a chunk in the VOX file"""
        while True:
            try:
                # Read chunk header
                chunk_id = file.read(4)
                if len(chunk_id) < 4:
                    break
                
                chunk_size = struct.unpack('<I', file.read(4))[0]
                child_chunks_size = struct.unpack('<I', file.read(4))[0]
                
                logger.debug(f"Chunk: {chunk_id.decode('ascii', errors='ignore')}, Size: {chunk_size}")
                
                if chunk_id == b'MAIN':
                    # Main chunk - contains child chunks
                    self._parse_chunk(file, voxel_data)
                
                elif chunk_id == b'SIZE':
                    # Size chunk - defines voxel grid dimensions
                    x = struct.unpack('<I', file.read(4))[0]
                    y = struct.unpack('<I', file.read(4))[0]
                    z = struct.unpack('<I', file.read(4))[0]
                    voxel_data.size = (x, y, z)
                    logger.info(f"Voxel grid size: {x} x {y} x {z}")
                
                elif chunk_id == b'XYZI':
                    # Voxel data chunk
                    num_voxels = struct.unpack('<I', file.read(4))[0]
                    logger.info(f"Number of voxels: {num_voxels}")
                    
                    for _ in range(num_voxels):
                        x = struct.unpack('<B', file.read(1))[0]
                        y = struct.unpack('<B', file.read(1))[0]  
                        z = struct.unpack('<B', file.read(1))[0]
                        color_idx = struct.unpack('<B', file.read(1))[0]
                        voxel_data.voxels.append((x, y, z, color_idx))
                
                elif chunk_id == b'RGBA':
                    # Palette chunk
                    palette = []
                    for _ in range(256):
                        r = struct.unpack('<B', file.read(1))[0]
                        g = struct.unpack('<B', file.read(1))[0]
                        b = struct.unpack('<B', file.read(1))[0]
                        a = struct.unpack('<B', file.read(1))[0]
                        palette.append((r, g, b, a))
                    voxel_data.palette = palette
                    logger.info("Loaded custom palette")
                
                else:
                    # Skip unknown chunk
                    file.seek(chunk_size, 1)
                
                # Parse child chunks if any
                if child_chunks_size > 0:
                    self._parse_chunk(file, voxel_data)
                    
            except struct.error:
                break
            except Exception as e:
                logger.error(f"Error parsing chunk: {e}")
                break
    
    def _generate_default_palette(self) -> List[Tuple[int, int, int, int]]:
        """Generate default MagicaVoxel palette"""
        palette = [(0, 0, 0, 0)]  # Index 0 is transparent
        
        # Generate a basic color palette (simplified)
        for i in range(1, 256):
            # Create a varied color palette
            hue = (i * 137.508) % 360  # Golden angle approximation
            saturation = 0.5 + (i % 50) / 100
            value = 0.3 + (i % 70) / 100
            
            # Convert HSV to RGB
            r, g, b = self._hsv_to_rgb(hue, saturation, value)
            palette.append((int(r * 255), int(g * 255), int(b * 255), 255))
        
        return palette
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[float, float, float]:
        """Convert HSV to RGB color space"""
        h = h / 60.0
        c = v * s
        x = c * (1 - abs((h % 2) - 1))
        m = v - c
        
        if 0 <= h < 1:
            r, g, b = c, x, 0
        elif 1 <= h < 2:
            r, g, b = x, c, 0
        elif 2 <= h < 3:
            r, g, b = 0, c, x
        elif 3 <= h < 4:
            r, g, b = 0, x, c
        elif 4 <= h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return r + m, g + m, b + m

def extract_vox_data(file_path: Path) -> Optional[VoxelData]:
    """Main function to extract data from a VOX file"""
    parser = VoxParser()
    return parser.parse(file_path)

# Example usage and testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python extract_vox.py <file.vox>")
        sys.exit(1)
    
    vox_file = Path(sys.argv[1])
    if not vox_file.exists():
        print(f"File not found: {vox_file}")
        sys.exit(1)
    
    logger.info(f"Parsing VOX file: {vox_file}")
    voxel_data = extract_vox_data(vox_file)
    
    if voxel_data:
        logger.info("Successfully parsed VOX file")
        logger.info(f"Grid size: {voxel_data.size}")
        logger.info(f"Number of voxels: {len(voxel_data.voxels)}")
        logger.info(f"Palette colors: {len(voxel_data.palette)}")
        
        # Convert to mesh
        vertices, faces = voxel_data.to_mesh_data()
        logger.info(f"Generated mesh: {len(vertices)} vertices, {len(faces)} faces")
    else:
        logger.error("Failed to parse VOX file")