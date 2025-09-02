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

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Installation

1. Clone or download this repository
2. Make sure Python 3.6+ is installed
3. The script is ready to use - no additional installation required

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
- `--no-materials`: Skip material definitions
- `-v, --verbose`: Verbose output showing parsing statistics
- `-W, --width`: Image width for POV-Ray rendering (default: 800)
- `-H, --height`: Image height for POV-Ray rendering (default: 600)
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

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the converter.

## License

This project is open source. Feel free to use and modify as needed.

## Related Tools

For more advanced OBJ to POV-Ray conversion, you might also consider:
- [PoseRay](https://www.povray.org/resources/links/3d_programs/Conversion_Utilities/)
- [Obj2Pov by Joss Whittle](https://github.com/JossWhittle/Obj2Pov)
- [Wavefront_To_Pov](https://github.com/NeuralCortex/Wavefront_To_Pov)
