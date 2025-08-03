# Publishing Guide for TaskPriority MCP Server

This guide explains how to publish your MCP server to different platforms so users worldwide can install it easily.

## 1. Publishing to PyPI (Python Package Index)

### Prerequisites
- Create account at https://pypi.org
- Install build tools: `pip install build twine`

### Steps

1. **Update version** in `setup.py` and `pyproject.toml`:
   ```python
   version="1.0.0"  # Increment for each release
   ```

2. **Build the package**:
   ```bash
   # Clean previous builds
   rm -rf dist/ build/ *.egg-info
   
   # Build source and wheel distributions
   python -m build
   ```

3. **Test with TestPyPI first** (optional but recommended):
   ```bash
   # Upload to test repository
   python -m twine upload --repository testpypi dist/*
   
   # Test installation
   pip install --index-url https://test.pypi.org/simple/ taskpriority-mcp
   ```

4. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

5. **Verify installation**:
   ```bash
   pip install taskpriority-mcp
   taskpriority-mcp --version
   ```

### Result
Users can now install with: `pip install taskpriority-mcp`

## 2. Publishing to GitHub

### Steps

1. **Ensure your repository is public** on GitHub

2. **Create a release**:
   ```bash
   # Tag the version
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

3. **Create GitHub Release**:
   - Go to https://github.com/yourusername/mcp-priority/releases
   - Click "Create a new release"
   - Choose your tag (v1.0.0)
   - Add release notes
   - Upload the wheel and source files from `dist/`

4. **Update setup.py** with correct GitHub URL:
   ```python
   url="https://github.com/yourusername/mcp-priority",
   ```

### Result
Users can now install with: `pip install git+https://github.com/yourusername/mcp-priority.git`

## 3. Creating NPM Package (for npx)

### Create NPM Wrapper

1. **Create `npm-wrapper` directory**:
   ```bash
   mkdir npm-wrapper
   cd npm-wrapper
   ```

2. **Create `package.json`**:
   ```json
   {
     "name": "taskpriority-mcp",
     "version": "1.0.0",
     "description": "TaskPriority MCP Server for Claude Desktop",
     "bin": {
       "taskpriority-mcp": "./bin/taskpriority-mcp.js"
     },
     "scripts": {
       "postinstall": "node scripts/install.js"
     },
     "keywords": ["mcp", "claude", "taskpriority"],
     "author": "TaskPriority Team",
     "license": "MIT",
     "repository": {
       "type": "git",
       "url": "https://github.com/yourusername/mcp-priority.git"
     },
     "engines": {
       "node": ">=14.0.0"
     },
     "dependencies": {
       "node-fetch": "^3.0.0"
     }
   }
   ```

3. **Create `bin/taskpriority-mcp.js`**:
   ```javascript
   #!/usr/bin/env node
   
   const { spawn } = require('child_process');
   const path = require('path');
   const os = require('os');
   
   // Check if Python is installed
   const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
   
   // Get the Python package location
   const packagePath = path.join(os.homedir(), '.taskpriority-mcp');
   
   // Spawn the Python process
   const args = ['-m', 'taskpriority_mcp', ...process.argv.slice(2)];
   const child = spawn(pythonCmd, args, {
     stdio: 'inherit',
     env: { ...process.env, PYTHONPATH: packagePath }
   });
   
   child.on('error', (err) => {
     console.error('Failed to start TaskPriority MCP Server:', err.message);
     console.error('Make sure Python 3.10+ is installed');
     process.exit(1);
   });
   
   child.on('exit', (code) => {
     process.exit(code);
   });
   ```

4. **Create `scripts/install.js`**:
   ```javascript
   const { execSync } = require('child_process');
   const os = require('os');
   const path = require('path');
   
   console.log('Installing TaskPriority MCP Server Python package...');
   
   try {
     const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
     const installPath = path.join(os.homedir(), '.taskpriority-mcp');
     
     // Install the Python package
     execSync(`${pythonCmd} -m pip install --target="${installPath}" taskpriority-mcp`, {
       stdio: 'inherit'
     });
     
     console.log('✓ TaskPriority MCP Server installed successfully!');
   } catch (error) {
     console.error('Failed to install Python package:', error.message);
     process.exit(1);
   }
   ```

5. **Publish to NPM**:
   ```bash
   # Login to npm
   npm login
   
   # Publish
   npm publish
   ```

### Result
Users can now use: `npx taskpriority-mcp`

## 4. Creating Docker Image

### Create Dockerfile

1. **Create `Dockerfile`** in project root:
   ```dockerfile
   FROM python:3.10-slim
   
   # Set working directory
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements first for better caching
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy the rest of the application
   COPY src/ ./src/
   COPY setup.py .
   COPY pyproject.toml .
   COPY README.md .
   
   # Install the package
   RUN pip install --no-cache-dir -e .
   
   # Create non-root user
   RUN useradd -m -u 1000 mcp && chown -R mcp:mcp /app
   USER mcp
   
   # Set environment variables
   ENV PYTHONUNBUFFERED=1
   
   # Run the server
   ENTRYPOINT ["taskpriority-mcp"]
   ```

2. **Create `.dockerignore`**:
   ```
   __pycache__
   *.pyc
   *.pyo
   *.pyd
   .git
   .env
   venv/
   env/
   .pytest_cache/
   .coverage
   htmlcov/
   dist/
   build/
   *.egg-info/
   ```

3. **Build the image**:
   ```bash
   docker build -t taskpriority/mcp-server:latest .
   docker build -t taskpriority/mcp-server:1.0.0 .
   ```

4. **Test locally**:
   ```bash
   docker run --rm -it \
     -e TASKPRIORITY_API_KEY=tp_live_test_key \
     taskpriority/mcp-server:latest
   ```

5. **Push to Docker Hub**:
   ```bash
   # Login to Docker Hub
   docker login
   
   # Push images
   docker push taskpriority/mcp-server:latest
   docker push taskpriority/mcp-server:1.0.0
   ```

### Result
Users can now use: `docker run taskpriority/mcp-server`

## 5. GitHub Actions for Automated Publishing

Create `.github/workflows/publish.yml`:

```yaml
name: Publish Package

on:
  release:
    types: [created]

jobs:
  publish-pypi:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*

  publish-docker:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          taskpriority/mcp-server:latest
          taskpriority/mcp-server:${{ github.event.release.tag_name }}
```

## Summary

After completing these steps:

1. **PyPI**: Users run `pip install taskpriority-mcp`
2. **GitHub**: Users run `pip install git+https://github.com/yourusername/mcp-priority.git`
3. **NPM**: Users run `npx taskpriority-mcp`
4. **Docker**: Users run `docker run taskpriority/mcp-server`

Each method provides a different way for users to install and run your MCP server, catering to different preferences and environments!