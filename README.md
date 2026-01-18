# LiMon: Line Monitoring

3rd year ENSEEIHT Project

# Group L3

Aya
Thomas
Gauthier
Farouk
Anton

# Project Architecture

![LiMon Architecture](./architecture.png)

# Build & Run

## Raspberry Pi

Navigate to the `rpi` directory:
```bash
cd rpi
```

Run the installation script to set up the virtual environment and install dependencies:
```bash
chmod +x install.sh
./install.sh
```

Run the application:
```bash
chmod +x run.sh
./run.sh
```

# Notes

- Ensure that your Raspberry Pi has a camera module connected and enabled.
- Adjust MQTT broker settings in `main.py` as needed.


# Credits

- Uses the model [YapaLab/yolo-face v11](https://github.com/YapaLab/yolo-face) using Ultralytics YOLO for face detection.