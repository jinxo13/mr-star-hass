# MR Star Home Assistant Integration [![Quality assurance](https://github.com/mishamyrt/mr-star-hass/actions/workflows/qa.yaml/badge.svg)](https://github.com/mishamyrt/mr-star-hass/actions/workflows/qa.yaml)

Integration for [MR Star Garland](https://github.com/mishamyrt/mr-star-ble) devices.

It uses bluetooth to control the lights.

## Installation

### [hapm](https://github.com/mishamyrt/hapm)

Add this repository to your `hapm.yaml` by running:

```sh
hapm add mishamyrt/mr-star-hass@latest
```

### HACS

Add this repo as HACS [custom repository](https://hacs.xyz/docs/faq/custom_repositories).

```
https://github.com/mishamyrt/mr-star-hass
```

Then find the integration in the list and press "Download".

### Manual

Copy `mr_star_garland` folder from latest release to `/config/custom_components` folder.

## Configuration

This integration uses Config Flow to configure, so to configure you need to:

1. Go to the integrations page
2. Click ‘Add Integration’
3. Find MR Star Garland in the list and select it.
4. Select the device address from the list
