# OBJ2POV - OBJ and STL to POV-Ray Converter

A Python tool that converts Wavefront OBJ and STL files to POV-Ray format for use with the Persistence of Vision Raytracer.

## Features

- ✅ Parses OBJ files with vertices, faces, normals, and texture coordinates
- ✅ Parses STL files (both ASCII and binary formats)
- ✅ Generates POV-Ray mesh2 objects
- ✅ Supports multiple objects in a single OBJ file
- ✅ Basic material support
- ✅ Command-line interface with options
- ✅ Error handling and validation
- ✅ Verbose output mode
- ✅ Progress bars for large files (using tqdm)

## Requirements

- Python 3.6 or higher
- External dependencies: `tqdm` (for progress bars)

## Installation

1. Clone or download this repository
2. Make sure Python 3.6+ is installed
3. Install dependencies: `pip install -r requirements.txt`
4. The script is ready to use

## Usage

### Basic Usage

```bash
python obj2pov.py input.obj
python obj2pov.py input.stl
```

This will create `input.pov` in the same directory.

### Advanced Usage

```bash
# Specify output file
python obj2pov.py model.obj -o output.pov
python obj2pov.py model.stl -o output.pov

# Skip material definitions
python obj2pov.py model.obj --no-materials
python obj2pov.py model.stl --no-materials

# Verbose output
python obj2pov.py model.obj -v
python obj2pov.py model.stl -v

# Get help
python obj2pov.py -h
```

### Command Line Options

- `input_file`: Input OBJ or STL file (required)
- `-o, --output`: Output POV file (default: input_file.pov)
- `--no-materials`: Skip material definitions (removes default bronze texture)
- `-v, --verbose`: Verbose output showing parsing statistics and progress bars
- `-W, --width`: Image width for POV-Ray rendering (default: 800)
- `-H, --height`: Image height for POV-Ray rendering (default: 600)
- `--flip-x`: Flip X coordinates to fix mirrored text/geometry
- `-h, --help`: Show help message

## Examples

### Example 1: Convert a cube (STL format)

```bash
python obj2pov.py samples/example_cube_ascii.stl
```

This creates `samples/example_cube_ascii.pov` with a complete POV-Ray scene including:
- Camera setup
- Lighting
- Mesh2 object with the cube geometry

### Example 2: Convert OBJ file

```bash
python obj2pov.py samples/example_triangle.obj
```

### Example 3: Convert with custom output

```bash
python obj2pov.py samples/example_triangle.obj -o triangle_scene.pov
python obj2pov.py samples/example_triangle_ascii.stl -o triangle_stl_scene.pov
```

### Example 4: Convert with custom image dimensions

```bash
# High resolution (4:3 aspect ratio)
python obj2pov.py samples/example_cube_ascii.stl -W 1024 -H 768

# Ultra high resolution (4:3 aspect ratio)
python obj2pov.py samples/example_cube_ascii.stl -W 1600 -H 1200

# HD resolution (16:9 aspect ratio)
python obj2pov.py samples/example_cube_ascii.stl -W 1920 -H 1080
```

### Example 5: Fix mirrored text/geometry

```bash
# If text or geometry appears mirrored in the render, use --flip-x
python obj2pov.py model.stl --flip-x
python obj2pov.py model.obj --flip-x -W 1024 -H 768
```

### Example 6: Generate with default bronze texture

```bash
# Default conversion includes beautiful bronze texture
python obj2pov.py samples/example_cube_ascii.stl

# Generate without materials (for custom texturing)
python obj2pov.py samples/example_cube_ascii.stl --no-materials
```

## File Format Support

### OBJ File Format
The converter supports the following OBJ file elements:

- **Vertices** (`v`): 3D coordinates
- **Normals** (`vn`): Surface normals for lighting
- **Texture Coordinates** (`vt`): UV mapping coordinates
- **Faces** (`f`): Polygonal faces (triangulated automatically)
- **Objects** (`o`): Named objects
- **Materials** (`usemtl`): Material references

### STL File Format
The converter supports both STL formats:

- **ASCII STL**: Human-readable text format
- **Binary STL**: Compact binary format
- **Triangular faces**: All STL files contain triangular faces
- **Normals**: Surface normals for each triangle
- **Vertices**: 3D coordinates for each triangle vertex

## POV-Ray Output

The generated POV-Ray files include:

- Complete scene setup with camera and lighting
- Mesh2 objects with vertex vectors, face indices
- Normal vectors (if present in OBJ)
- UV vectors for texture mapping (if present in OBJ)
- Basic material definitions
- Proper POV-Ray syntax and formatting
- **Automatic camera positioning** to frame the entire object
- **Square pixel aspect ratio** to prevent stretching
- **35° field of view** for optimal viewing

## Limitations

- Materials from MTL files are not yet supported (basic materials only)
- Complex OBJ features like curves and surfaces are not supported
- Only triangular and quad faces are supported (higher-order polygons are triangulated)

## File Structure

```
OBJ2POV/
├── obj2pov.py                # Main converter script
├── convert.bat               # Windows batch script
├── requirements.txt          # Dependencies info
├── README.md                # This documentation
└── samples/                 # Example files and test models
    ├── README.md            # Documentation for sample files
    ├── example_triangle.obj  # Example triangle OBJ file
    ├── example_cube_ascii.stl # Example cube STL file (ASCII)
    ├── example_triangle_ascii.stl # Example triangle STL file (ASCII)
    └── *.pov                 # Generated POV-Ray files
```

## Testing

Test the converter with the included example files:

```bash
# Convert OBJ files
python obj2pov.py samples/example_triangle.obj -v

# Convert STL files
python obj2pov.py samples/example_cube_ascii.stl -v
python obj2pov.py samples/example_triangle_ascii.stl -v

# Convert more complex models
python obj2pov.py samples/full_figure.stl -v
python obj2pov.py samples/torus.stl -v
```

## Rendering with POV-Ray

To render the generated POV-Ray files with correct aspect ratio:

```bash
# Render with default dimensions (800x600)
povray +W800 +H600 samples/example_cube_ascii.pov

# Render with custom dimensions (matches the -W and -H options used)
povray +W1024 +H768 samples/example_cube_ascii.pov
povray +W1600 +H1200 samples/example_cube_ascii.pov
povray +W1920 +H1080 samples/example_cube_ascii.pov
```

**Important:** The generated POV-Ray files include the correct render command in the comments. Use the same dimensions that were specified with `-W` and `-H` options to maintain proper aspect ratio and prevent stretching.

## Progress Bars

When using the `-v` (verbose) option, the converter shows progress bars for large files:

- **OBJ files**: Progress bar appears for files with >1000 lines
- **STL files**: Progress bar appears for files with >1000 triangles
- **POV generation**: Progress bars for files with >10,000 vertices, normals, or triangles
  - Writing vertices (>10,000 vertices)
  - Writing normals (>10,000 normals)
  - Writing UV coordinates (>10,000 UVs)
  - Writing face indices (>10,000 triangles)
  - Writing normal indices (>10,000 triangles)
  - Writing UV indices (>10,000 triangles)

Example output:
```
Parsing STL file: large_model.stl
Parsing ASCII STL: 100%|████████████| 50000/50000 [00:02<00:00, 25000.00lines/s]
Writing vertices: 100%|████████████| 25000/25000 [00:01<00:00, 25000.00vertices/s]
Writing normals: 100%|████████████| 25000/25000 [00:01<00:00, 25000.00normals/s]
Writing face indices: 100%|████████████| 50000/50000 [00:02<00:00, 25000.00faces/s]
```

## Coordinate System Issues

### Mirrored Text/Geometry

Sometimes when rendering STL or OBJ files, you may notice that text or geometry appears mirrored (backwards). This is due to differences in coordinate systems between the original 3D modeling software and POV-Ray.

**Solution**: Use the `--flip-x` option to flip the X coordinates:

```bash
python obj2pov.py model.stl --flip-x
```

This will:
- Flip all X coordinates (multiply by -1)
- Flip normal X components to maintain proper lighting
- Adjust camera positioning to keep the object centered
- Fix mirrored text and geometry issues

**When to use `--flip-x`:**
- Text appears backwards in the render
- Geometry looks mirrored
- The model appears to be facing the wrong direction

## Default Bronze Texture

The converter automatically includes a beautiful bronze metal texture for all objects:

### **Features:**
- **Realistic bronze appearance** with warm, metallic coloring
- **Metallic finish** with proper reflection and specular properties
- **Subtle surface texture** with bump mapping for realistic depth
- **Professional look** perfect for statues, sculptures, and architectural elements

### **Texture Properties:**
- **Base color**: Rich bronze (RGB: 0.8, 0.5, 0.2) - warm golden-brown
- **Surface**: Metallic finish with 30% reflection
- **Texture**: Subtle bumps for realistic metal surface
- **Lighting**: Optimized specular highlights and diffuse properties

### **Customization:**
If you want to use your own materials instead of the default bronze texture, use the `--no-materials` option:

```bash
# Generate without default bronze texture
python obj2pov.py model.stl --no-materials
```

This will create a POV file with basic material properties that you can customize manually.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the converter.

## License

This project is open source. Feel free to use and modify as needed.

## Related Tools

For more advanced OBJ to POV-Ray conversion, you might also consider:
- [PoseRay](https://www.povray.org/resources/links/3d_programs/Conversion_Utilities/)
- [Obj2Pov by Joss Whittle](https://github.com/JossWhittle/Obj2Pov)
- [Wavefront_To_Pov](https://github.com/NeuralCortex/Wavefront_To_Pov)
