# flashing_tools

Graphical windows to configure the motors and electronic modules of a Reachy 2021.

## How to install

1. clone this repo
```bash
git clone https://github.com/pollen-robotics/flashing_tools.git
```
2. install the required depencies
```bash
cd flashing_tools
pip3 install -e .
```
3. install dfu-util if it isn't already the case
```bash
sudo apt-get install -y dfu-util
```

## How to use

* For the flashing motor GUI:
```python
cd flasing_tools
python3 flash_motor.py
```

Select what motor you want to flash and click on "Configure", a progress bar should fill. If the message "Motor configured" appears, you can disconnect the motor.


* For the flashing electronic module GUI:
```python
cd flasing_tools
python3 flash_module.py
```

Select what type of board the electronic module is and click on "Configure". If the message "Configuration succedded" appears, you can disconnect the board.

## Configuring bash files
If you want to make bash files executing the python scripts:

* for the flashing motor script, put in a .sh file:
```bash
#!/bin/bash
your_python_path path_to_flashing_tools/flash_motor.py
```

* for the flashing electronic module script, put in a .sh file:

```bash
#!/bin/bash
your_python_path path_to_flashing_tools/flash_module.py
```

## Create desktop icons (in Ubuntu)

1. Make the bash script executable
```bash
sudo chmod +x your_bash_script.sh
```

2. In Ubuntu files explorer (Nautilus), in the top right icon with three strips click on "Preferences" -> "Behavior" -> "Executable text files" -> "Run them".

3. Move the .sh file in Desktop.