# Test Assets Directory

This directory contains sample avatar files for testing the Avatar Everywhere CLI.

## Expected Files

Place your test avatar files in this directory:

- `avatar01.glb` - Sample GLB avatar file from Sandbox/VoxEdit
- `avatar02.vox` - Sample VOX avatar file from MagicaVoxel

## File Requirements

### GLB Files

- Must be valid glTF 2.0 binary format
- Should contain mesh geometry and materials
- Optional: skeletal animation data
- Export from VoxEdit or Sandbox

### VOX Files

- Must be valid MagicaVoxel .vox format
- Should contain voxel data with color information
- Export from MagicaVoxel

## Testing Commands

```bash
# Test GLB conversion
python main.py convert test_assets/avatar01.glb --skip-verify

# Test VOX conversion
python main.py convert test_assets/avatar02.vox --skip-verify

# Analyze file information
python main.py info test_assets/avatar01.glb
```

## Notes

- Test files are excluded from version control via .gitignore
- Place your own avatar files here for testing
- Files should be reasonably sized (< 50MB) for testing
