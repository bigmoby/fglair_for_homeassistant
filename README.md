# FGLair&trade; integration for homeassistant

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
[![License][license-shield]](LICENSE.md)

![Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/bigmoby)

![FGLAIR_LOGO](FGLair_logo.png)

This is a platform to support Fujitsu General Airconditioners under Climate component of Home Assistant. The Python supporting library for accessing the FGLair&trade; API is located at: https://github.com/bigmoby/pyfujitsugeneral/

## Sample UI:

![UI_SCREENSHOT1](Capture.PNG)
![UI_SCREENSHOT2](Capture2.PNG)

## Installation
### Manual

1. Create this directory path `custom_components/fglair_heatpump_controller/` if it does not already exist.

2. Download the `climate.py` `manifest.json` and `__init__.py` from the repo and place it in the  directory mentioned in previous step.

So the end result would look like:
`/custom_components/fglair_heatpump_controller/climate.py`
`/custom_components/fglair_heatpump_controller/manifest.json`
`/custom_components/fglair_heatpump_controller/__init__.py`

### HACS
1. Add this repository to HACS:
```
https://github.com/bigmoby/fglair_for_homeassistant
```

2. Search for the `FGLair integration for homeassistant` integration and choose install.

3. Reboot Home Assistant.

### Usage:

Add the below lines to your `configuration.yaml` file and replace it with your FGLair app username/password and region your FGLair account is registered (eu, cn or us):
```
climate:
   - platform: fglair_heatpump_controller
     username: <your FGLair username>
     password: <your FGLair password>
     region: ['eu' | 'cn' | 'us'] (optional, default: 'us')
     tokenpath: (optional, default: 'token.txt')
     temperature_offset: (optional, default: 0)
```

Full Example:
```
climate:
  - platform: fglair_heatpump_controller
    username: !secret FGLAIR_USER
    password: !secret FGLAIR_PASS
    region: 'eu'
    tokenpath: 'token.txt'
    temperature_offset: -2.0
```

1. Restart Home Assistant in order for the new component to show and all of your A/Cs in your account should appear in HASS.

Note for A/C units with horizontal swing support, the horizontal swing and position can be changed but only the vertical position will be shown due to limitations with Home Assistant's climate entity.

## Known issues and missing features:

- [X] Logging needs to be implemented
- [X] The “powerful” functionality is implemented via the preset selections in the UI
- [ ] There are some other functionalities in the A/C which currently is not implemented.
- [ ] Possibility to add external temperature sensor

##
** "FGLair" is a trademark of FUJITSU GENERAL LIMITED.

[releases-shield]: https://img.shields.io/github/release/bigmoby/fglair_for_homeassistant.svg
[releases]: https://github.com/bigmoby/fglair_for_homeassistant/releases
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[license-shield]: https://img.shields.io/github/license/bigmoby/fglair_for_homeassistant
[maintenance-shield]: https://img.shields.io/maintenance/yes/2023.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/bigmoby/fglair_for_homeassistant.svg
[commits]: https://img.shields.io/github/commits/bigmoby/fglair_for_homeassistant
