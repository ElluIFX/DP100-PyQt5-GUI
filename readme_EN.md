# Aliantek DP100 Power Supply PC Controller

PyQt5-based PC Controller for Aliantek DP100 Digital Power Supply
> [!NOTE]
> The project is now synchronized with the latest code from my other controllers, introducing many new features and significantly improving rendering performance

![1746780655831](image/readme/1746780655831.png)

**(GUI in English is available if your system language is non-Chinese)**

## Features

> [!IMPORTANT]
> **Currently still in BETA status. If you encounter any issues, please refer to the [Log Collection Method] at the end of the README, record the log, and submit an issue requesting a fix**

### Python3 API

- Support for output/voltage/current settings
- Device status reading
- Real-time reading of output ADC measurements

### PyQt5 GUI

- Basic parameter settings, preset group management, configuration modification
- Data acquisition, plotting, analysis, and saving at up to 100Hz (adjustable)
  - Custom waveform buffer length
  - **Plot buffer now allows free selection of preview range while recording millions of data points**
- PID constant power control
- Parameter scanning (voltage/current)
  - *Drawing scan response curves (for studying load characteristics)*
- Function generator (sine/square/triangle/sawtooth/random waves)
- Operation sequences (execute action sequences once or in loops)
- *Battery simulator (supports custom battery voltage curves/capacity/internal resistance/series connection)*
- *Floating data window*
- Material Design style with two themes
- *i18n support (Chinese/English)*
- Ready-to-use portable executable

### GUI Environment Variables

- MDP_ENABLE_LOG: Enable debug log output (or start with the --debug parameter)
- MDP_FORCE_ENGLISH: Force English UI (or start with the --english parameter)
- MDP_SIM_MODE: Enable simulation mode, allowing testing of UI functions without connecting a device (or start with the --sim parameter)

### Log Collection Method

Start the program with the `--debug` parameter. The program will create a dp100.log log file in its folder. Reproduce the bug, then attach the log file to your issue
![1746781629583](image/readme/1746781629583.png)
