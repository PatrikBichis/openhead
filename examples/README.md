# Examples

Host-side example scripts using the `openhead` Python package. Robot-specific bridges (e.g. ROS 2) are kept out of this repo.

- `demo_video.py`: records the simulated head going through every theme and emotion while speaking (Windows TTS → `face.envelope`), as an mp4 with sound:

  ```bash
  cd python
  uv run --with imageio-ffmpeg python ../examples/demo_video.py -o ../demo/openhead-demo.mp4
  ```
