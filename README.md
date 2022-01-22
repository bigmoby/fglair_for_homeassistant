# FGLiar integration for homeassistant

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
[![License][license-shield]](LICENSE.md)

![Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

[![Donate](https://img.shields.io/badge/donate-BuyMeCoffee-yellow.svg)](https://www.buymeacoffee.com/bigmoby)

This is a platform to support Fujitsu General Airconditioners under Climate component of Home Assistant. The Python supporting library for accessing the FGLair API is located at: https://github.com/bigmoby/pyfujitseu/

### Sample UI:

![UI_SCREENSHOT1](Capture.PNG)
![UI_SCREENSHOT2](Capture2.PNG)

### Usage:
1. create this directory path `/config/custom_components/fujitsu_general_heatpump/` if it does not already exist.


2. Download the `climate.py` `manifest.json' and '__init__.py` from the repo and place it in the  directory mentioned in previous step. 

So the end result would look like: 
`/config/custom_components/fujitsu_general_heatpump/climate.py`
`/config/custom_components/fujitsu_general_heatpump/manifest.json`
`/config/custom_components/fujitsu_general_heatpump/__init__.py`

3. add the below lines to your `configuration.yaml` file and replace it with your FGLair app username/password:
```
climate:
   - platform: fujitsu_general_heatpump
     username: <your FGLair username>
     password: <your FGLair password> 
     region: [eu, cn, us] (optional, default: us)
     tokenpath: (optional, default: 'token.txt')       
```

Full Example:
```
climate:
  - platform: fujitsu_general_heatpump
    username: !secret FGLAIR_USER
    password: !secret FGLAIR_PASS
    region: 'eu'
    tokenpath: 'token.txt'
```

4. Restart Home Assistant in order for the new component to show and all of your A/Cs in your account should appear in HASS.

### Known issues and missing features:


- [X] Logging needs to be implemented
- [ ] The “powerful” functionality is implemented through aux_heat button in UI
- [ ] There are some other functionalities in the A/C which currently is not implemented.
- [ ] Possibility to add external temperature sensor

[releases-shield]: https://img.shields.io/github/release/bigmoby/fglair_for_homeassistant.svg
[releases]: https://github.com/bigmoby/fglair_for_homeassistant/releases
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[license-shield]: https://img.shields.io/github/license/bigmoby/fglair_for_homeassistant
[maintenance-shield]: https://img.shields.io/maintenance/yes/2022.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/bigmoby/fglair_for_homeassistant.svg
[commits]: https://img.shields.io/github/commits/bigmoby/fglair_for_homeassistant