# Attractor Tools

**Attractor-tools** is a Python module for animating the **Simon fractal** using efficient rendering. It provides a clean API to generate frames, assinging colormaps, and export visualizations as videos.

---

## ✨ Features
- Animate the Simon fractal with customizable parameters
- NumPy, Numba and Multiprocessing for performance

---

## 📦 Installation
Clone the repo and install in editable mode for development:

```bash
git clone https://github.com/beasty79/attractor_api.git
cd attractor
pip install -e .
```

## Example usage
```python
from attractor import sinspace, Performance_Renderer, ColorMap

def main():
    # Create an array of values following a sinewave (period = 1)
    # works jsut the same as np.linspace(start, end, n)
    # similar function are cosspace, bpmspace
    a = sinspace(0, 1, 100)

    # Initialize the main renderer
    renderer = Performance_Renderer(
        a=a,
        b=1.5,
        colormap=ColorMap("viridis"),
        frames=len(a),
    )

    # Important: mark 'a' as non-static (varies per frame)
    renderer.set_static("a", False)

    # Start rendering to a video file using 4 threads
    renderer.start_render_process("./your_file_path/your_filename.mp4", threads=4, chunksize=4)

if __name__ == "__main__":
    main()
```

# Attractor Visualization API

## Overview

This package provides tools for generating and rendering dynamic attractor visualizations using customizable color maps and performance-optimized rendering techniques.


## API
- **render_frame**
  Core function to compute attractor frame data.

- **Performance_Renderer**
  High-performance renderer supporting multi-threaded frame generation and video output.

## Utility Functions

- **ColorMap**
  Utility class to create and manage color maps with optional inversion.

- **sinspace / cosspace**
  Generate smooth sine- or cosine-shaped value sequences over a specified range.

- **bpmspace**
  Create time-based sequences synced to beats per minute (BPM) for rhythmic animations.

- **map_area**
  Batch process and render attractor animations over a grid of parameters.

- **apply_colormap**
  Apply a color map to attractor data to produce a colored image.