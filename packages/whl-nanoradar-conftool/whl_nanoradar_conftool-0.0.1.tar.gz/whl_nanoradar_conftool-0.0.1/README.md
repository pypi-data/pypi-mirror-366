# whl-nanoradar-conftool

## Installation

```bash
pip install whl-nanoradar-conftool
```

## Usage

### scan devices

```bash
whl-nanoradar-conftool --interface socketscan --channel can1 --bitrate 5000 scan
```

it will print the list of devices found on the CAN bus.

```text
Found nano radar devices:
sensor id: 0, conjecture number: 1
{
    "nvm_read_status": 1,
    "nvm_write_status": 0,
    "max_distance_cfg": 20,
    "sensor_id": 0,
    "sort_index": 1,
    "radar_power_cfg": 0,
    "motion_rx_state": 0,
    "send_ext_info_cfg": 0,
    "send_quality_cfg": 0,
    "output_type_cfg": 1,
    "ctrl_relay_cfg": 0,
    "can_baud_rate": 0,
    "rcs_threshold": 0,
    "calibration_enabled": 0
}
```

### config sensor_id

assume that the current sensor ID is `0`, and you want to set it to `1`.

```bash
whl-nanoradar-conftool --interface socketscan --channel can1 --bitrate 5000 \
    config \
    --message_id $((0x200)) \
    --set sensor_id_valid 1 \
    --set sensor_id 1 \
    --set store_in_nvm_valid 1 \
    --set store_nvm 1
```

after running the command, you can check the sensor id by running the `scan`
command again
