# Avatar Everywhere CLI - Portable Sandbox Identity Toolkit

**Milestone 1:** NFT Ownership Verification + Avatar Export to VRM

Convert your Sandbox avatars to VRM format for use across metaverse platforms like Unity, VRChat, and more. Includes blockchain-based ownership verification to ensure you own the avatar NFT before conversion.

## Features

- **NFT Ownership Verification**: Verify Sandbox avatar NFT ownership on Polygon network
- **Avatar Format Conversion**: Convert `.glb` and `.vox` avatar files to VRM 1.0 format
- **Cross-Platform Compatibility**: Output VRM files work with Unity, VRChat, and other VRM-compatible platforms
- **CLI Interface**: Simple command-line tools for batch processing and automation
- **WalletConnect v2 Integration**: Seamless wallet connection for NFT verification
- **Performance Testing**: Automated benchmarking for large file handling
- **Unity Integration**: Comprehensive VRM testing with UniVRM
- **Real Network Testing**: Polygon mainnet NFT verification procedures

## System Requirements

| Component | Version  | Status             |
| --------- | -------- | ------------------ |
| Python    | 3.11+    | Required           |
| Node.js   | 16+      | Required           |
| UniVRM    | 0.121+   | For Unity testing  |
| Unity     | 2022 LTS | For VRM validation |

## Installation

### Option 1: Install via PyPI (Recommended)

```bash
# Install the complete package
pip install avatar-everywhere-cli

# Install with development dependencies
pip install avatar-everywhere-cli[dev]

# Install with performance monitoring
pip install avatar-everywhere-cli[performance]
```

### Option 2: Install via npm

```bash
# Install the Node.js components
npm install avatar-everywhere-cli

# Install globally for CLI access
npm install -g avatar-everywhere-cli
```

### Option 3: Manual Installation

```bash
# Clone repository
git clone https://github.com/Supercoolkayy/avatar-everywhere-cli
cd avatar-everywhere-cli

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Verify installation
python main.py list-requirements
```

### Post-Installation Setup

After installation, you may need to:

1. **Set up WalletConnect** (for NFT verification):

   ```bash
   # Create .env file with your WalletConnect Project ID
   echo "WALLETCONNECT_PROJECT_ID=your_project_id_here" > .env
   ```

2. **Verify installation**:
   ```bash
   # Test the CLI
   avatar-everywhere --help
   # or
   python main.py --help
   ```

## Usage

After installation via PyPI, you can use the CLI in two ways:

```bash
# Using the installed command
avatar-everywhere --help

# Or using the Python module
python main.py --help
```

### NFT Ownership Verification

Verify that you own a Sandbox avatar NFT before converting:

```bash
# Verify ownership with wallet address
python main.py verify \
  --contract 0x1234567890abcdef1234567890abcdef12345678 \
  --token 123 \
  --wallet 0xabcdef1234567890abcdef1234567890abcdef12

# Verify ownership with WalletConnect v2
python main.py verify-wc \
  --contract 0x1234567890abcdef1234567890abcdef12345678 \
  --token 123

# Verify ownership (will prompt for WalletConnect)
python main.py verify --contract 0x... --token 123
```

**Parameters:**

- `--contract, -c`: NFT contract address on Polygon
- `--token, -t`: NFT token ID
- `--wallet, -w`: Wallet address (optional, triggers WalletConnect if not provided)
- `--auto-connect`: Automatically connect wallet (WalletConnect mode)

### Avatar Conversion

Convert Sandbox avatar files to VRM format:

```bash
# Convert with ownership verification
python main.py convert avatar.glb \
  --output my_avatar.vrm \
  --contract 0x1234567890abcdef1234567890abcdef12345678 \
  --token 123

# Convert without verification (testing)
python main.py convert avatar.glb --skip-verify

# Convert VOX file
python main.py convert avatar.vox --output avatar.vrm
```

**Parameters:**

- `input_file`: Path to `.glb` or `.vox` avatar file
- `--output, -o`: Output VRM file path (optional, defaults to input name with .vrm extension)
- `--contract, -c`: NFT contract address for verification
- `--token, -t`: NFT token ID for verification
- `--skip-verify`: Skip NFT ownership verification

### File Analysis

Get information about avatar files:

```bash
# Analyze GLB file
python main.py info avatar.glb

# Analyze VOX file
python main.py info avatar.vox
```

### Performance Testing

Run automated performance benchmarks:

```bash
# Run comprehensive performance tests
python benchmark_performance.py

# Test specific file conversion
python main.py convert test_assets/large_avatar.glb output/large_test.vrm

# Monitor memory usage
python -m memory_profiler main.py convert test_assets/medium_avatar.glb
```

### Unity Integration Testing

Test VRM files in Unity with UniVRM:

```bash
# Follow the Unity integration guide
# See unity_integration_test.md for detailed instructions

# 1. Install UniVRM in Unity
# 2. Import VRM files from output/ directory
# 3. Validate import success and runtime functionality
```

### Real Network Testing

Test NFT verification on Polygon mainnet:

```bash
# Test with real Sandbox NFTs
python main.py verify \
  --contract 0x5cc5e64ab764a0f1e97f23984e20fd4528826c79 \
  --token 12345 \
  --wallet 0x1234567890123456789012345678901234567890

# Test network resilience
python main.py verify \
  --contract 0x5cc5e64ab764a0f1e97f23984e20fd4528826c79 \
  --token 12345 \
  --rpc-url https://rpc-mainnet.maticvigil.com
```

## Examples

### Complete Workflow

```bash
# 1. Verify you own the NFT
python main.py verify \
  --contract 0xa342f5d851e866e18ff98f351f2c6637f4478db5 \
  --token 12345 \
  --wallet 0x742d35cc6634c0532925a3b8d0e97b4b0d2d4aad

# 2. Convert avatar with verification
python main.py convert sandbox_avatar.glb \
  --output my_metaverse_avatar.vrm \
  --contract 0xa342f5d851e866e18ff98f351f2c6637f4478db5 \
  --token 12345

# 3. Check the output file
python main.py info my_metaverse_avatar.vrm
```

### Batch Processing

```bash
# Process multiple avatars
for file in assets/*.glb; do
  python main.py convert "$file" --skip-verify
done
```

## File Structure

```
avatar-everywhere-cli/
├── main.py                 # Main entry point
├── cli.py                  # CLI commands and interface
├── converters/
│   └── sandbox_to_vrm.py   # GLB/VOX to VRM converter
├── wallet/
│   └── verify_owner.js     # NFT ownership verification
├── vox_parser/
│   └── extract_vox.py      # VOX file parser
├── test_assets/
│   ├── sample_avatar.glb   # Sample test files
│   ├── sample_voxel.vox    # Sample test files
│   └── README.md           # Test assets documentation
├── package.json            # Node.js dependencies
├── requirements.txt        # Python dependencies
├── benchmark_performance.py # Performance testing script
├── unity_integration_test.md # Unity testing guide
├── nft_verification_test.md # NFT testing guide
├── performance_testing.md   # Performance testing guide
├── walletconnect_integration.md # WalletConnect guide
├── VALIDATION_SUMMARY.md   # Validation summary
└── README.md              # This file
```

## Development and Distribution

### Building Packages

To build packages for distribution:

```bash
# Build both Python and npm packages
python build_distribution.py

# Build Python package only
python -m build

# Build npm package only
npm run build
```

### Publishing to Package Registries

```bash
# Publish to PyPI
python -m twine upload dist/*

# Publish to npm
npm publish
```

### Local Testing

```bash
# Test Python package locally
pip install dist/*.whl
avatar-everywhere --help

# Test npm package locally
npm pack
npm install avatar-everywhere-cli-1.0.0.tgz
```

## Testing and Validation

The project includes comprehensive testing and validation capabilities:

### Automated Testing

- **Performance Benchmarks**: `benchmark_performance.py` for automated performance testing
- **Memory Monitoring**: Built-in memory usage tracking
- **CPU Profiling**: Performance analysis tools

### Manual Testing Guides

- **Unity Integration**: `unity_integration_test.md` for VRM testing in Unity
- **NFT Verification**: `nft_verification_test.md` for real network testing
- **Performance Testing**: `performance_testing.md` for large file handling
- **WalletConnect**: `walletconnect_integration.md` for wallet integration

### Validation Procedures

- **Unity VRM Testing**: Import and validate VRM files in Unity with UniVRM
- **Real Network Testing**: Test NFT verification on Polygon mainnet
- **Performance Validation**: Test with various file sizes and complexities
- **WalletConnect Testing**: Test wallet connection and verification

## Supported Avatar Formats

### Input Formats

- **GLB**: Binary glTF files exported from VoxEdit or Sandbox
- **VOX**: MagicaVoxel files (experimental support)

### Output Format

- **VRM 1.0**: Ready for Unity, VRChat, and other metaverse platforms

## VRM Compatibility

The generated VRM files include:

- SUCCESS: Mesh geometry and materials
- SUCCESS: Basic humanoid bone mapping
- SUCCESS: VRM 1.0 metadata
- SUCCESS: Material properties (MToon shader)
- WARNING: Limited animation support (basic skeleton only)
- WARNING: Simplified bone detection for voxel avatars

## Troubleshooting

### Common Issues

**"Node.js not found"**

```bash
# Install Node.js (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Node.js (macOS)
brew install node

# Install Node.js (Windows)
# Download from https://nodejs.org
```

**"Contract call failed"**

- Verify the contract address is correct
- Ensure the token ID exists
- Check your internet connection (Polygon RPC access required)

**"VRM file doesn't load in Unity"**

- Install UniVRM 0.121+ in Unity
- Check Unity console for specific errors
- Verify the GLB file is valid before conversion

### Debug Mode

Add `--verbose` to any command for detailed output:

```bash
python main.py convert avatar.glb --verbose
```

## Development

### Running Tests

```bash
# Test with sample files
python main.py convert test_assets/avatar01.glb --skip-verify

# Test NFT verification (requires valid contract/token)
python main.py verify --contract 0x... --token 123
```

### Code Quality

```bash
# Format code
black .
isort .

# Type checking
mypy .
```

## Polygon Network Details

- **Network**: Polygon Mainnet
- **Chain ID**: 137
- **RPC URLs**:
  - https://polygon-rpc.com
  - https://rpc-mainnet.matic.network
  - https://matic-mainnet.chainstacklabs.com

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Issues**: GitHub Issues
- **Documentation**: This README
- **Community**: Discord (link TBD)

---

**Avatar Everywhere** - Bringing your digital identity everywhere you go.
