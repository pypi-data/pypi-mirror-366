# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **machofile**, a pure Python module for parsing Mach-O binary files (the executable format used by macOS, iOS, watchOS, and tvOS). It's inspired by Ero Carrera's pefile module and aims to provide comprehensive Mach-O analysis capabilities without external dependencies.

## Development Commands

### Running the Tool
The main module serves as both a Python library and a CLI tool:

```bash
# Run as CLI with all analysis options
python3 machofile.py -a -f /path/to/binary

# Run specific analysis types
python3 machofile.py -g -f /path/to/binary        # General info
python3 machofile.py -hdr -f /path/to/binary      # Header info  
python3 machofile.py -l -f /path/to/binary        # Load commands
python3 machofile.py -seg -f /path/to/binary      # Segments
python3 machofile.py -d -f /path/to/binary        # Dylib info
python3 machofile.py -sim -f /path/to/binary      # Similarity hashes
python3 machofile.py -sig -f /path/to/binary      # Code signature
python3 machofile.py -ep -f /path/to/binary       # Entry point
python3 machofile.py -i -f /path/to/binary        # Imports
python3 machofile.py -e -f /path/to/binary        # Exports
```

### Testing
Use the test samples in `test_data/` directory for development and validation:
```bash
python3 machofile.py -a -f test_data/curl
```

## Code Architecture

### Core Class Structure
- **MachO**: Main class that handles all parsing operations
  - Initialized with either `file_path` or `data` parameter
  - Call `parse()` method to begin parsing process
  - Contains all parsed data as instance attributes

### Key Parsing Methods
- `parse()`: Main entry point that orchestrates all parsing
- `parse_all_load_commands()`: Processes Mach-O load commands
- `parse_code_signature()`: Handles code signing information and certificates
- `parse_export_trie()`: Parses export trie for symbol information

### Data Extraction Methods
- `get_general_info()`: File metadata (hashes, size, etc.)
- `get_macho_header()`: Mach-O header structure
- `get_imported_functions()`: Functions imported from dylibs
- `get_exported_symbols()`: Exported symbols and functions
- `get_similarity_hashes()`: Various hashes for similarity analysis (dylib_hash, import_hash, export_hash, symhash)

### Key Features Supported
- Both 32-bit and 64-bit Mach-O files, as well as FAT/Universal binaries
- All major load command types (LC_SEGMENT*, LC_DYLIB*, LC_SYMTAB, etc.)
- Code signature parsing including certificates and entitlements
- Import/export analysis with hash generation
- Segment entropy calculation
- UUID and version information extraction

### Instance Attributes (set after parsing)
- `header`: Mach-O header information
- `load_commands`: List of load command structures
- `segments`: File segment information
- `dylib_commands`: Dynamic library commands
- `imported_functions`: Dictionary of imported functions by dylib
- `exported_symbols`: Dictionary of exported symbols
- `code_signature_info`: Code signing and certificate information

### File Structure
The entire module is contained in a single file (`machofile.py`) with:
- Extensive Mach-O structure definitions and constants at the top
- Main `MachO` class implementation
- CLI argument parsing and output formatting at the bottom
- No external dependencies beyond Python standard library

### Development Notes
- The module is completely self-contained with no external dependencies
- Endianness independent and works across platforms
- Currently tested primarily on x86/x86_64 architectures
- Archive folder contains the old CLI-only version for reference