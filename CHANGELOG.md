# Changelog

All notable changes to the OBJ2POV project will be documented in this file.

## [1.0.0] - 2025-01-02

### Added
- Initial release of OBJ2POV converter
- Support for Wavefront OBJ file format
- Support for STL file format (both ASCII and binary)
- POV-Ray mesh2 object generation
- Automatic camera positioning and FOV calculation
- Custom image dimensions support (-W, -H command-line options)
- Zero-length normal vector fix for POV-Ray compatibility
- Progress bars for large files using tqdm library
- X coordinate flip option (--flip-x) to fix mirrored text/geometry
- Default bronze texture with metallic finish and realistic surface properties
- Comprehensive documentation and examples
- Windows batch script for easy conversion
- Square pixel aspect ratio support
- Material and texture coordinate support
- Command-line interface with verbose output
- Error handling and validation

### Features
- Converts OBJ files with vertices, faces, normals, and texture coordinates
- Converts STL files with triangular faces and normals
- Generates complete POV-Ray scenes with camera and lighting
- Supports multiple objects in a single OBJ file
- Automatic triangulation of N-gon faces
- Proper POV-Ray syntax and formatting
- 35° field of view for optimal viewing
- Automatic bounding box calculation for camera positioning

### Technical Details
- Python 3.6+ compatible
- External dependency: tqdm for progress bars
- Supports both ASCII and binary STL parsing
- Handles vertex deduplication for STL files
- Proper UV vector format for POV-Ray
- Complete mesh2 object structure with all required sections
- Progress bars for files with >1000 lines/triangles/vertices
