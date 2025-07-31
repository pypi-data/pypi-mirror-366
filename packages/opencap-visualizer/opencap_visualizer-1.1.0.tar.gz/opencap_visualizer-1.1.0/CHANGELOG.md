# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-07-30

### 🚨 BREAKING CHANGES
- **Package renamed**: `opencap-visualizer-cli` → `opencap-visualizer`
  - Command-line interface remains the same: `opencap-visualizer` and `opencap-viz`
  - Python imports now use: `import opencap_visualizer`

### ✨ Added
- **Python API**: Full programmatic access to video generation functionality
  - `OpenCapVisualizer` class for object-oriented usage  
  - `create_video()` and `create_video_async()` convenience functions
  - Async and sync support for different use cases
  - Comprehensive type hints and documentation
- **Enhanced File Support**: 
  - Standalone .trc files (marker data)
  - Standalone .mot files (force data)
  - Mixed file type combinations (JSON + markers + forces)
- **Better Package Structure**: 
  - Separated CLI and API functionality
  - Clean public API with proper `__all__` exports
  - Enhanced `__init__.py` with usage examples

### 🐛 Fixed
- **Clean Video Output**: Removed unwanted .webm file creation
  - Only creates desired MP4 files
  - Eliminates automatic browser recording that created random .webm files
- **Hosted Version**: Always uses https://opencap-visualizer.onrender.com/
  - No longer tries to connect to localhost
  - Consistent experience across all users
- **Recording Issues**: Fixed commented-out recording start code

### 📖 Improved  
- **Documentation**: Complete rewrite of README with both CLI and Python API examples
- **Package Description**: Updated to reflect dual CLI/API nature
- **Default Camera**: Closer zoom by default (0.8 instead of 1.5)
- **Example Usage**: Updated examples with new zoom settings

### 🔧 Technical
- Extracted core functionality to `api.py` module
- Maintained backward compatibility for CLI usage
- Added comprehensive type annotations
- Enhanced error handling and logging
- Improved file validation and processing logic

## [1.0.1] - 2024-01-XX

### 🐛 Fixed
- Fixed global variable declaration conflict in browser automation
- Improved Session.vue detection for headless mode

### 🔧 Technical
- Added `?headless=true` query parameter for proper app detection
- Enhanced error messages and debugging output

## [1.0.0] - 2024-01-XX

### 🎉 Initial Release

#### ✨ Features
- **Command-line interface** for generating videos from biomechanics data
- **Multiple file support**: JSON files and OpenSim .osim/.mot pairs
- **Subject comparison**: Side-by-side visualization of multiple subjects
- **Anatomical camera views**: anterior, posterior, sagittal, superior, etc.
- **Customizable visuals**: colors, zoom, centering, loops, dimensions
- **Interactive mode**: Browser-based manual exploration
- **Auto-detection**: Deployed app, local dev server, or built files

#### 🛠️ Technical
- **Headless browser automation** with Playwright
- **Vue.js integration** with the OpenCap Visualizer web app  
- **Video recording** with WebM/MP4 format support
- **FFmpeg integration** for optimal video compatibility
- **Comprehensive error handling** and timeout management

#### 📦 Distribution
- **pip installable**: `pip install opencap-visualizer-cli`
- **Cross-platform**: Windows, macOS, Linux support
- **Minimal dependencies**: Playwright, aiohttp
- **No local setup required**: Uses deployed web application

#### 🎯 Use Cases
- **Research**: Generate videos for presentations and publications
- **Clinical**: Visualize patient movement analysis
- **Education**: Create instructional biomechanics content
- **Development**: Automated video generation for testing 