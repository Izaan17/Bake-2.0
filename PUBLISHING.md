# Publishing Updates for Bake

This guide explains how to publish updates for the Bake command manager.

## Method 1: GitHub Releases (Recommended)

### Step 1: Prepare Your Release

1. **Update Version Number**
   ```bash
   # Edit constants.py and update VERSION
   VERSION = "1.1.0"  # Use semantic versioning
   ```

2. **Update CHANGELOG** (optional but recommended)
   ```bash
   # Create or update CHANGELOG.md
   echo "## [1.1.0] - $(date +%Y-%m-%d)" >> CHANGELOG.md
   echo "### Added" >> CHANGELOG.md
   echo "- Update system with GitHub integration" >> CHANGELOG.md
   echo "- Health check command" >> CHANGELOG.md
   echo "- Enhanced error handling" >> CHANGELOG.md
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: Add update system and health check (v1.1.0)"
   git push origin main
   ```

### Step 2: Create GitHub Release

1. **Go to GitHub Repository**
   - Visit: https://github.com/Izaan17/Bake-2.0
   - Click "Releases" → "Create a new release"

2. **Fill Release Details**
   - **Tag version**: `v1.1.0` (must start with 'v')
   - **Release title**: `Bake v1.1.0 - Update System & Health Check`
   - **Description**: 
     ```markdown
     ## What's New in v1.1.0
     
     ### 🚀 New Features
     - **Update System**: Automatic updates from GitHub releases
     - **Health Check**: `bake health` command for diagnostics
     - **Enhanced Validation**: Better command name and script validation
     - **Improved Error Handling**: More robust error recovery
     
     ### 🔧 Improvements
     - Better shell detection and PATH management
     - Enhanced logging system
     - Improved installation validation
     - More comprehensive help documentation
     
     ### 🐛 Bug Fixes
     - Fixed various edge cases in command management
     - Improved error messages and user feedback
     
     ## How to Update
     ```bash
     bake update
     ```
     ```

3. **Attach Files** (optional)
   - You can attach `bake.py` as a release asset
   - Or just rely on the main branch download

4. **Publish Release**
   - Click "Publish release"

### Step 3: Test the Update System

1. **Test Update Check**
   ```bash
   # This should now detect the new version
   bake list
   ```

2. **Test Update Process**
   ```bash
   # This should update to the new version
   bake update
   ```

## Method 2: PyPI Distribution (For pip installs)

### Step 1: Prepare for PyPI

1. **Update setup.py version**
   ```python
   version="1.1.0",  # Must match constants.py
   ```

2. **Build Package**
   ```bash
   pip install build twine
   python -m build
   ```

3. **Upload to PyPI**
   ```bash
   # Test upload first
   python -m twine upload --repository testpypi dist/*
   
   # Real upload
   python -m twine upload dist/*
   ```

### Step 2: Update PyPI Package

Users can then update via:
```bash
pip install --upgrade bake-command-manager
bake --install  # Reinstall to get latest
```

## Method 3: Manual Distribution

### For Direct Downloads

1. **Create Distribution Package**
   ```bash
   # Create a zip file with all necessary files
   zip -r bake-v1.1.0.zip bake.py constants.py printer.py requirements.txt README.md setup.py
   ```

2. **Share the Package**
   - Upload to GitHub releases
   - Share download link
   - Users can extract and run `python bake.py --install`

## Version Numbering Guidelines

Use [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backward compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backward compatible

## Release Checklist

- [ ] Update version in `constants.py`
- [ ] Update version in `setup.py` (if using PyPI)
- [ ] Update CHANGELOG.md
- [ ] Test the update system locally
- [ ] Commit and push changes
- [ ] Create GitHub release
- [ ] Test update from previous version
- [ ] Announce the release (optional)

## Testing Updates

### Test Update System Locally

1. **Simulate Old Version**
   ```bash
   # Temporarily change version to test
   sed -i 's/VERSION = "1.1.0"/VERSION = "1.0.0"/' constants.py
   ```

2. **Test Update Check**
   ```bash
   bake list  # Should show update notification
   ```

3. **Test Update Process**
   ```bash
   bake update  # Should update to 1.1.0
   ```

4. **Restore Version**
   ```bash
   sed -i 's/VERSION = "1.0.0"/VERSION = "1.1.0"/' constants.py
   ```

## Automated Release (Advanced)

You can set up GitHub Actions for automated releases:

1. **Create `.github/workflows/release.yml`**
2. **Trigger on version tags**
3. **Automatically create releases**
4. **Build and upload packages**

This is more advanced but provides fully automated releases.
