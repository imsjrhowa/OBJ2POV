#!/usr/bin/env python3
"""
OBJ to POV-Ray Converter

This tool converts Wavefront OBJ files to POV-Ray format.
Supports vertices, faces, normals, texture coordinates, and materials.
"""

import argparse
import os
import sys
import struct
from typing import List, Tuple, Optional, Dict, Any
import re
from tqdm import tqdm


class OBJParser:
    """Parser for Wavefront OBJ files."""
    
    def __init__(self):
        self.vertices: List[Tuple[float, float, float]] = []
        self.normals: List[Tuple[float, float, float]] = []
        self.texture_coords: List[Tuple[float, float]] = []
        self.faces: List[List[Tuple[int, int, int]]] = []  # (vertex, texture, normal) indices
        self.materials: Dict[str, Dict[str, Any]] = {}
        self.current_material: Optional[str] = None
        self.objects: List[str] = []
        self.current_object: Optional[str] = None
        
    def parse_file(self, filename: str, show_progress: bool = True) -> None:
        """Parse an OBJ file."""
        try:
            # First pass: count lines for progress bar
            total_lines = 0
            if show_progress:
                with open(filename, 'r', encoding='utf-8') as f:
                    total_lines = sum(1 for _ in f)
            
            # Second pass: parse with progress bar
            with open(filename, 'r', encoding='utf-8') as f:
                if show_progress and total_lines > 1000:  # Only show progress for large files
                    progress_bar = tqdm(f, total=total_lines, desc="Parsing OBJ", unit="lines")
                else:
                    progress_bar = f
                
                for line_num, line in enumerate(progress_bar, 1):
                    self._parse_line(line.strip(), line_num)
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filename}")
        except Exception as e:
            raise Exception(f"Error parsing file {filename}: {e}")
    
    def _parse_line(self, line: str, line_num: int) -> None:
        """Parse a single line from the OBJ file."""
        if not line or line.startswith('#'):
            return
            
        parts = line.split()
        if not parts:
            return
            
        command = parts[0].lower()
        
        try:
            if command == 'v':  # Vertex
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    self.vertices.append((x, y, z))
                    
            elif command == 'vn':  # Normal
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    self.normals.append((x, y, z))
                    
            elif command == 'vt':  # Texture coordinate
                if len(parts) >= 3:
                    u, v = float(parts[1]), float(parts[2])
                    self.texture_coords.append((u, v))
                    
            elif command == 'f':  # Face
                if len(parts) >= 4:
                    face_indices = []
                    for part in parts[1:]:
                        # Parse vertex/texture/normal indices
                        indices = part.split('/')
                        vertex_idx = int(indices[0]) - 1  # OBJ uses 1-based indexing
                        texture_idx = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else -1
                        normal_idx = int(indices[2]) - 1 if len(indices) > 2 and indices[2] else -1
                        face_indices.append((vertex_idx, texture_idx, normal_idx))
                    self.faces.append(face_indices)
                    
            elif command == 'o':  # Object name
                if len(parts) >= 2:
                    self.current_object = parts[1]
                    self.objects.append(self.current_object)
                    
            elif command == 'usemtl':  # Use material
                if len(parts) >= 2:
                    self.current_material = parts[1]
                    
        except (ValueError, IndexError) as e:
            print(f"Warning: Error parsing line {line_num}: {line} - {e}", file=sys.stderr)


class STLParser:
    """Parser for STL (STereoLithography) files."""
    
    def __init__(self):
        self.vertices: List[Tuple[float, float, float]] = []
        self.normals: List[Tuple[float, float, float]] = []
        self.texture_coords: List[Tuple[float, float]] = []  # STL files don't have texture coords
        self.faces: List[List[Tuple[int, int, int]]] = []  # (vertex, -1, normal) indices
        self.vertex_map: Dict[Tuple[float, float, float], int] = {}
        self.vertex_count = 0
        
    def parse_file(self, filename: str, show_progress: bool = True) -> None:
        """Parse an STL file (both ASCII and binary formats)."""
        try:
            with open(filename, 'rb') as f:
                # Read first 80 bytes to check if it's ASCII or binary
                header = f.read(80)
                f.seek(0)
                
                # Check if it's ASCII STL (starts with "solid")
                if header.startswith(b'solid'):
                    self._parse_ascii_stl(f, show_progress)
                else:
                    self._parse_binary_stl(f, show_progress)
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filename}")
        except Exception as e:
            raise Exception(f"Error parsing STL file {filename}: {e}")
    
    def _parse_ascii_stl(self, f, show_progress: bool = True) -> None:
        """Parse ASCII STL format."""
        content = f.read().decode('utf-8', errors='ignore')
        lines = content.split('\n')
        
        current_vertices = []
        current_normal = None
        
        # Count facets for progress bar
        facet_count = 0
        if show_progress:
            facet_count = content.count('facet normal')
        
        # Use progress bar for large files
        if show_progress and facet_count > 1000:
            lines_iter = tqdm(lines, desc="Parsing ASCII STL", unit="lines")
        else:
            lines_iter = lines
        
        for line in lines_iter:
            line = line.strip()
            parts = line.split()
            
            if not parts:
                continue
                
            if parts[0] == 'facet' and parts[1] == 'normal':
                # Parse normal vector
                if len(parts) >= 5:
                    nx, ny, nz = float(parts[2]), float(parts[3]), float(parts[4])
                    current_normal = (nx, ny, nz)
                    self.normals.append(current_normal)
                    
            elif parts[0] == 'vertex':
                # Parse vertex
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertex = (x, y, z)
                    current_vertices.append(vertex)
                    
            elif parts[0] == 'endfacet':
                # End of facet - create face
                if len(current_vertices) == 3 and current_normal is not None:
                    face_indices = []
                    for vertex in current_vertices:
                        vertex_idx = self._get_or_add_vertex(vertex)
                        face_indices.append((vertex_idx, -1, len(self.normals) - 1))
                    self.faces.append(face_indices)
                    
                current_vertices = []
                current_normal = None
    
    def _parse_binary_stl(self, f, show_progress: bool = True) -> None:
        """Parse binary STL format."""
        # Skip header (80 bytes)
        f.seek(80)
        
        # Read number of triangles (4 bytes, little-endian unsigned int)
        num_triangles = struct.unpack('<I', f.read(4))[0]
        
        # Use progress bar for large files
        if show_progress and num_triangles > 1000:
            triangle_iter = tqdm(range(num_triangles), desc="Parsing Binary STL", unit="triangles")
        else:
            triangle_iter = range(num_triangles)
        
        for _ in triangle_iter:
            # Read normal vector (3 floats, 4 bytes each)
            normal_data = f.read(12)
            nx, ny, nz = struct.unpack('<fff', normal_data)
            self.normals.append((nx, ny, nz))
            
            # Read 3 vertices (3 floats each, 4 bytes each)
            vertices = []
            for _ in range(3):
                vertex_data = f.read(12)
                x, y, z = struct.unpack('<fff', vertex_data)
                vertices.append((x, y, z))
            
            # Create face
            face_indices = []
            for vertex in vertices:
                vertex_idx = self._get_or_add_vertex(vertex)
                face_indices.append((vertex_idx, -1, len(self.normals) - 1))
            self.faces.append(face_indices)
            
            # Skip attribute byte count (2 bytes)
            f.read(2)
    
    def _get_or_add_vertex(self, vertex: Tuple[float, float, float]) -> int:
        """Get existing vertex index or add new vertex."""
        if vertex in self.vertex_map:
            return self.vertex_map[vertex]
        else:
            self.vertices.append(vertex)
            self.vertex_map[vertex] = self.vertex_count
            self.vertex_count += 1
            return self.vertex_count - 1


class POVGenerator:
    """Generator for POV-Ray files."""
    
    def __init__(self, parser, image_width=800, image_height=600, flip_x=False):
        self.parser = parser
        self.image_width = image_width
        self.image_height = image_height
        self.flip_x = flip_x
        
    def generate_pov(self, output_filename: str, include_materials: bool = True, show_progress: bool = True) -> None:
        """Generate POV-Ray file from parsed OBJ data."""
        with open(output_filename, 'w', encoding='utf-8') as f:
            self._write_header(f)
            
            if include_materials:
                self._write_materials(f)
                
            self._write_mesh(f, show_progress)
            
            self._write_footer(f)
    
    def _write_header(self, f) -> None:
        """Write POV-Ray file header."""
        f.write("// Generated by OBJ2POV converter\n")
        f.write("// Converted from OBJ file\n\n")
        f.write("#version 3.7;\n\n")
        f.write("// Image settings for square pixels\n")
        f.write(f"// Render with: povray +W{self.image_width} +H{self.image_height} filename.pov\n")
        f.write(f"#declare ImageWidth = {self.image_width};\n")
        f.write(f"#declare ImageHeight = {self.image_height};\n\n")
        f.write("// Global settings\n")
        f.write("global_settings {\n")
        f.write("    assumed_gamma 1.0\n")
        f.write("}\n\n")
        
        # Write default bronze texture
        self._write_default_texture(f)
        
    def _write_default_texture(self, f) -> None:
        """Write default bronze texture definition."""
        f.write("// Default bronze texture\n")
        f.write("#declare BronzeTexture = texture {\n")
        f.write("    pigment {\n")
        f.write("        color rgb <0.8, 0.5, 0.2>\n")
        f.write("    }\n")
        f.write("    normal {\n")
        f.write("        bumps 0.3\n")
        f.write("        scale 0.1\n")
        f.write("    }\n")
        f.write("    finish {\n")
        f.write("        ambient 0.1\n")
        f.write("        diffuse 0.7\n")
        f.write("        specular 0.4\n")
        f.write("        roughness 0.05\n")
        f.write("        reflection 0.3\n")
        f.write("        metallic\n")
        f.write("    }\n")
        f.write("}\n\n")
        
    def _write_materials(self, f) -> None:
        """Write material definitions."""
        f.write("// Material definitions\n")
        f.write("#default {\n")
        f.write("    texture { BronzeTexture }\n")
        f.write("}\n\n")
        
    def _write_mesh(self, f, show_progress: bool = True) -> None:
        """Write mesh2 object."""
        if not self.parser.vertices or not self.parser.faces:
            f.write("// No geometry found in OBJ file\n")
            return
            
        f.write("// Main mesh object\n")
        f.write("mesh2 {\n")
        
        # Write vertex vectors
        f.write("    vertex_vectors {\n")
        f.write(f"        {len(self.parser.vertices)},\n")
        
        # Use progress bar for large vertex counts
        if show_progress and len(self.parser.vertices) > 10000:
            vertex_iter = tqdm(enumerate(self.parser.vertices), total=len(self.parser.vertices), 
                             desc="Writing vertices", unit="vertices", leave=False)
        else:
            vertex_iter = enumerate(self.parser.vertices)
            
        for i, (x, y, z) in vertex_iter:
            # Apply X coordinate flip if requested
            if self.flip_x:
                x = -x
            f.write(f"        <{x:.6f}, {y:.6f}, {z:.6f}>")
            if i < len(self.parser.vertices) - 1:
                f.write(",")
            f.write("\n")
        f.write("    }\n\n")
        
        # Write normal vectors if available
        if self.parser.normals:
            f.write("    normal_vectors {\n")
            f.write(f"        {len(self.parser.normals)},\n")
            
            # Use progress bar for large normal counts
            if show_progress and len(self.parser.normals) > 10000:
                normal_iter = tqdm(enumerate(self.parser.normals), total=len(self.parser.normals), 
                                 desc="Writing normals", unit="normals", leave=False)
            else:
                normal_iter = enumerate(self.parser.normals)
                
            for i, (x, y, z) in normal_iter:
                # POV-Ray doesn't allow zero-length normals, use <1, 0, 0> as default
                if x == 0.0 and y == 0.0 and z == 0.0:
                    x, y, z = 1.0, 0.0, 0.0
                # Apply X coordinate flip to normals if requested
                if self.flip_x:
                    x = -x
                f.write(f"        <{x:.6f}, {y:.6f}, {z:.6f}>")
                if i < len(self.parser.normals) - 1:
                    f.write(",")
                f.write("\n")
            f.write("    }\n\n")
        
        # Write texture coordinates if available
        if self.parser.texture_coords:
            f.write("    uv_vectors {\n")
            f.write(f"        {len(self.parser.texture_coords)},\n")
            
            # Use progress bar for large texture coordinate counts
            if show_progress and len(self.parser.texture_coords) > 10000:
                uv_iter = tqdm(enumerate(self.parser.texture_coords), total=len(self.parser.texture_coords), 
                             desc="Writing UV coordinates", unit="UVs", leave=False)
            else:
                uv_iter = enumerate(self.parser.texture_coords)
                
            for i, (u, v) in uv_iter:
                f.write(f"        <{u:.6f}, {v:.6f}>")
                if i < len(self.parser.texture_coords) - 1:
                    f.write(",")
                f.write("\n")
            f.write("    }\n\n")
        
        # Write face indices
        f.write("    face_indices {\n")
        
        # Count total triangles after triangulation
        total_triangles = 0
        for face in self.parser.faces:
            if len(face) >= 3:
                # For STL files, faces are already triangles, so no triangulation needed
                if hasattr(self.parser, 'vertex_map'):  # This indicates it's an STL parser
                    total_triangles += 1  # Each face is already a triangle
                else:
                    total_triangles += len(face) - 2  # Each face with n vertices becomes n-2 triangles
        
        f.write(f"        {total_triangles},\n")
        
        # Use progress bar for large triangle counts
        if show_progress and total_triangles > 10000:
            face_iter = tqdm(enumerate(self.parser.faces), total=len(self.parser.faces), 
                           desc="Writing face indices", unit="faces", leave=False)
        else:
            face_iter = enumerate(self.parser.faces)
        
        triangle_count = 0
        for i, face in face_iter:
            if len(face) >= 3:
                # For STL files, faces are already triangles
                if hasattr(self.parser, 'vertex_map'):  # This indicates it's an STL parser
                    v1 = face[0][0]
                    v2 = face[1][0]
                    v3 = face[2][0]
                    f.write(f"        <{v1}, {v2}, {v3}>")
                    triangle_count += 1
                    if triangle_count < total_triangles:
                        f.write(",")
                    f.write("\n")
                else:
                    # Convert to triangle fan if face has more than 3 vertices (OBJ files)
                    for j in range(1, len(face) - 1):
                        v1 = face[0][0]
                        v2 = face[j][0]
                        v3 = face[j + 1][0]
                        f.write(f"        <{v1}, {v2}, {v3}>")
                        triangle_count += 1
                        if triangle_count < total_triangles:
                            f.write(",")
                        f.write("\n")
        f.write("    }\n")
        
        # Write normal indices if normals are available
        if self.parser.normals:
            f.write("\n    normal_indices {\n")
            f.write(f"        {total_triangles},\n")
            
            # Use progress bar for large triangle counts
            if show_progress and total_triangles > 10000:
                normal_face_iter = tqdm(enumerate(self.parser.faces), total=len(self.parser.faces), 
                                      desc="Writing normal indices", unit="faces", leave=False)
            else:
                normal_face_iter = enumerate(self.parser.faces)
            
            triangle_count = 0
            for i, face in normal_face_iter:
                if len(face) >= 3:
                    # For STL files, faces are already triangles
                    if hasattr(self.parser, 'vertex_map'):  # This indicates it's an STL parser
                        n1 = face[0][2] if face[0][2] >= 0 else 0
                        n2 = face[1][2] if face[1][2] >= 0 else 0
                        n3 = face[2][2] if face[2][2] >= 0 else 0
                        f.write(f"        <{n1}, {n2}, {n3}>")
                        triangle_count += 1
                        if triangle_count < total_triangles:
                            f.write(",")
                        f.write("\n")
                    else:
                        # Convert to triangle fan if face has more than 3 vertices (OBJ files)
                        for j in range(1, len(face) - 1):
                            n1 = face[0][2] if face[0][2] >= 0 else 0
                            n2 = face[j][2] if face[j][2] >= 0 else 0
                            n3 = face[j + 1][2] if face[j + 1][2] >= 0 else 0
                            f.write(f"        <{n1}, {n2}, {n3}>")
                            triangle_count += 1
                            if triangle_count < total_triangles:
                                f.write(",")
                            f.write("\n")
            f.write("    }\n")
        
        # Write UV indices if texture coordinates are available
        if self.parser.texture_coords:
            f.write("\n    uv_indices {\n")
            f.write(f"        {total_triangles},\n")
            
            # Use progress bar for large triangle counts
            if show_progress and total_triangles > 10000:
                uv_face_iter = tqdm(enumerate(self.parser.faces), total=len(self.parser.faces), 
                                  desc="Writing UV indices", unit="faces", leave=False)
            else:
                uv_face_iter = enumerate(self.parser.faces)
            
            triangle_count = 0
            for i, face in uv_face_iter:
                if len(face) >= 3:
                    # For STL files, faces are already triangles
                    if hasattr(self.parser, 'vertex_map'):  # This indicates it's an STL parser
                        uv1 = face[0][1] if face[0][1] >= 0 else 0
                        uv2 = face[1][1] if face[1][1] >= 0 else 0
                        uv3 = face[2][1] if face[2][1] >= 0 else 0
                        f.write(f"        <{uv1}, {uv2}, {uv3}>")
                        triangle_count += 1
                        if triangle_count < total_triangles:
                            f.write(",")
                        f.write("\n")
                    else:
                        # Convert to triangle fan if face has more than 3 vertices (OBJ files)
                        for j in range(1, len(face) - 1):
                            uv1 = face[0][1] if face[0][1] >= 0 else 0
                            uv2 = face[j][1] if face[j][1] >= 0 else 0
                            uv3 = face[j + 1][1] if face[j + 1][1] >= 0 else 0
                            f.write(f"        <{uv1}, {uv2}, {uv3}>")
                            triangle_count += 1
                            if triangle_count < total_triangles:
                                f.write(",")
                            f.write("\n")
            f.write("    }\n")
        
        f.write("}\n\n")
        
    def _calculate_camera_setup(self):
        """Calculate optimal camera position and FOV to frame the entire object."""
        if not self.parser.vertices:
            # Default setup if no vertices
            return (0, 0, -10), (0, 0, 0), 35.0, 15.0
        
        # Calculate bounding box, applying X flip if requested
        vertices_for_bounds = self.parser.vertices
        if self.flip_x:
            vertices_for_bounds = [(-v[0], v[1], v[2]) for v in self.parser.vertices]
        
        min_x = min(v[0] for v in vertices_for_bounds)
        max_x = max(v[0] for v in vertices_for_bounds)
        min_y = min(v[1] for v in vertices_for_bounds)
        max_y = max(v[1] for v in vertices_for_bounds)
        min_z = min(v[2] for v in vertices_for_bounds)
        max_z = max(v[2] for v in vertices_for_bounds)
        
        # Calculate object center
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_z = (min_z + max_z) / 2
        
        # Calculate object dimensions
        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z
        
        # Calculate the maximum dimension (diagonal of bounding box)
        max_dimension = (width**2 + height**2 + depth**2)**0.5
        
        # Calculate distance needed to fit object in frame
        # Using field of view of 35 degrees (half-angle = 17.5 degrees)
        fov_half_angle_rad = 17.5 * 3.14159265359 / 180  # Convert to radians
        
        # Distance = (max_dimension / 2) / tan(fov_half_angle)
        # Add some padding (20% extra)
        distance = (max_dimension / 2) / (fov_half_angle_rad) * 1.2
        
        # Position camera along the diagonal for best view
        # Use a nice 3/4 view angle
        camera_x = center_x + distance * 0.5
        camera_y = center_y + distance * 0.3
        camera_z = center_z + distance * 0.8
        
        # Calculate light distance (1.5x camera distance for good lighting)
        light_distance = distance * 1.5
        
        return (camera_x, camera_y, camera_z), (center_x, center_y, center_z), 35.0, light_distance
        
    def _write_footer(self, f) -> None:
        """Write POV-Ray file footer."""
        f.write("// Camera and lighting setup\n")
        
        # Calculate bounding box and camera position
        camera_pos, look_at, fov, light_distance = self._calculate_camera_setup()
        
        f.write("camera {\n")
        f.write(f"    location <{camera_pos[0]:.3f}, {camera_pos[1]:.3f}, {camera_pos[2]:.3f}>\n")
        f.write(f"    look_at <{look_at[0]:.3f}, {look_at[1]:.3f}, {look_at[2]:.3f}>\n")
        f.write(f"    angle {fov:.1f}\n")
        f.write("    right x*ImageWidth/ImageHeight  // Correct aspect ratio for square pixels\n")
        f.write("    up y\n")
        f.write("}\n\n")
        
        # Position lights relative to the object
        f.write("light_source {\n")
        f.write(f"    <{camera_pos[0] + light_distance * 0.5:.3f}, {camera_pos[1] + light_distance * 0.5:.3f}, {camera_pos[2] - light_distance * 0.5:.3f}>\n")
        f.write("    color rgb <1, 1, 1>\n")
        f.write("}\n\n")
        
        f.write("light_source {\n")
        f.write(f"    <{camera_pos[0] - light_distance * 0.3:.3f}, {camera_pos[1] - light_distance * 0.3:.3f}, {camera_pos[2] - light_distance * 0.3:.3f}>\n")
        f.write("    color rgb <0.5, 0.5, 0.5>\n")
        f.write("}\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Convert OBJ and STL files to POV-Ray format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python obj2pov.py model.obj
  python obj2pov.py model.stl
  python obj2pov.py model.obj -o output.pov
  python obj2pov.py model.stl --no-materials
  python obj2pov.py model.obj -W 1024 -H 768
  python obj2pov.py model.stl -W 1600 -H 1200
  python obj2pov.py model.stl --flip-x
        """
    )
    
    parser.add_argument('input_file', help='Input OBJ or STL file')
    parser.add_argument('-o', '--output', help='Output POV file (default: input_file.pov)')
    parser.add_argument('--no-materials', action='store_true', 
                       help='Skip material definitions')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-W', '--width', type=int, default=800,
                       help='Image width for POV-Ray rendering (default: 800)')
    parser.add_argument('-H', '--height', type=int, default=600,
                       help='Image height for POV-Ray rendering (default: 600)')
    parser.add_argument('--flip-x', action='store_true',
                       help='Flip X coordinates to fix mirrored text/geometry')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(args.input_file)[0]
        output_file = f"{base_name}.pov"
    
    try:
        # Determine file type and create appropriate parser
        file_ext = os.path.splitext(args.input_file)[1].lower()
        
        if file_ext == '.obj':
            if args.verbose:
                print(f"Parsing OBJ file: {args.input_file}")
            parser = OBJParser()
            parser.parse_file(args.input_file, show_progress=args.verbose)
            
        elif file_ext == '.stl':
            if args.verbose:
                print(f"Parsing STL file: {args.input_file}")
            parser = STLParser()
            parser.parse_file(args.input_file, show_progress=args.verbose)
            
        else:
            print(f"Error: Unsupported file format '{file_ext}'. Supported formats: .obj, .stl", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"Found {len(parser.vertices)} vertices")
            print(f"Found {len(parser.faces)} faces")
            print(f"Found {len(parser.normals)} normals")
            if hasattr(parser, 'texture_coords'):
                print(f"Found {len(parser.texture_coords)} texture coordinates")
        
        # Generate POV-Ray file
        pov_generator = POVGenerator(parser, args.width, args.height, args.flip_x)
        pov_generator.generate_pov(output_file, include_materials=not args.no_materials, show_progress=args.verbose)
        
        print(f"Successfully converted '{args.input_file}' to '{output_file}'")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
