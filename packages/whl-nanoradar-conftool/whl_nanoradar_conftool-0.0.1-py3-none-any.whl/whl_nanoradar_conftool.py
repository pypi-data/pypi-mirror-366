#!/usr/bin/env python3
"""nano radar configuration tool
"""
import datetime
import json

import can
import click

VERSION = '0.0.1'


class RadarState:
    """RadarState Struct
    """

    def __init__(self, buffer):
        """__init__
        """
        if len(buffer) != 8:
            raise ValueError('Invalid buffer length, expected 8 bytes')
        self.buffer = bytearray(buffer)

    def __str__(self):
        """__str__
        """
        return f'RadarState({self.buffer.hex()})'

    def pretty_json(self):
        """pretty_print
        """
        return json.dumps(
            {
                'nvm_read_status': self.nvm_read_status,
                'nvm_write_status': self.nvm_write_status,
                'max_distance_cfg': self.max_distance_cfg,
                'sensor_id': self.sensor_id,
                'sort_index': self.sort_index,
                'radar_power_cfg': self.radar_power_cfg,
                'motion_rx_state': self.motion_rx_state,
                'send_ext_info_cfg': self.send_ext_info_cfg,
                'send_quality_cfg': self.send_quality_cfg,
                'output_type_cfg': self.output_type_cfg,
                'ctrl_relay_cfg': self.ctrl_relay_cfg,
                'can_baud_rate': self.can_baud_rate,
                'rcs_threshold': self.rcs_threshold,
                'calibration_enabled': self.calibration_enabled,
            },
            indent=4)

    @property
    def nvm_read_status(self):
        """nvm_read_status
        """
        return (self.buffer[0] >> 6) & 0x01

    def parse(self, buffer):
        if len(buffer) != 8:
            raise ValueError('Invalid buffer length, expected 8 bytes')

    @property
    def nvm_write_status(self):
        """nvm_write_status"""
        return (self.buffer[0] >> 7) & 0x01

    @property
    def max_distance_cfg(self):
        """max_distance_cfg
        """
        return ((self.buffer[2] & 0xc0) << 2) | self.buffer[1]

    @property
    def sensor_id(self):
        """sensor_id
        """
        return self.buffer[4] & 0x07

    @property
    def sort_index(self):
        """sort_index
        """
        return (self.buffer[4] >> 4) & 0x07

    @property
    def radar_power_cfg(self):
        """radar_power_cfg"""
        return ((self.buffer[4] >> 5) & 0x04) | (self.buffer[3] & 0x03)

    @property
    def motion_rx_state(self):
        """motion_rx_state
        """
        return (self.buffer[5] >> 6) & 0x04

    @property
    def send_ext_info_cfg(self):
        """send_ext_info_cfg"""
        return (self.buffer[5] >> 5) & 0x01

    @property
    def send_quality_cfg(self):
        """send_quality_cfg"""
        return (self.buffer[5] >> 4) & 0x01

    @property
    def output_type_cfg(self):
        """output_type_cfg
        """
        return (self.buffer[5] >> 2) & 0x03

    @property
    def ctrl_relay_cfg(self):
        """ctrl_relay_cfg
        """
        return (self.buffer[5] >> 1) & 0x01

    @property
    def can_baud_rate(self):
        """can_baud_rate
        """
        return (self.buffer[6] >> 5) & 0x07

    @property
    def rcs_threshold(self):
        """rcs_threshold
        """
        return (self.buffer[7] >> 2) & 0x07

    @property
    def calibration_enabled(self):
        """calibration_enabled
        """
        return (self.buffer[7] >> 6) & 0x04


class RadarConfig:
    """RadarConfig Struct
    """

    def __init__(self):
        """__init__
        """

        self.buffer = bytearray(b'\x00' * 8)

    def __str__(self):
        """__str__
        """
        return f'RadarConfig({self.buffer.hex()})'

    @property
    def store_in_nvm_valid(self):
        """store_in_nvm_valid
        """
        return (self.buffer[0] >> 7) & 0x01

    @store_in_nvm_valid.setter
    def store_in_nvm_valid(self, value):
        """store_in_nvm_valid setter
        """
        if value not in (0, 1):
            raise ValueError('store_in_nvm_valid must be 0 or 1')
        self.buffer[0] = self.buffer[0] | (value << 7)

    @property
    def store_nvm(self):
        """store_nvm
        """
        return (self.buffer[5] >> 7) & 0x01

    @store_nvm.setter
    def store_nvm(self, value):
        """store_nvm setter
        """
        if value not in (0, 1):
            raise ValueError('store_nvm must be 0 or 1')
        self.buffer[5] = self.buffer[5] | (value << 7)

    @property
    def sensor_id_valid(self):
        """sensor_id_valid
        """
        return (self.buffer[0] >> 1) & 0x01

    @sensor_id_valid.setter
    def sensor_id_valid(self, value):
        """sensor_id_valid setter
        """
        if value not in (0, 1):
            raise ValueError('sensor_id_valid must be 0 or 1')
        self.buffer[0] = self.buffer[0] | (value << 1)

    @property
    def sensor_id(self):
        """sensor_id
        """
        return self.buffer[4] & 0x07

    @sensor_id.setter
    def sensor_id(self, value):
        """sensor_id setter
        """
        if not (0 <= value <= 7):
            raise ValueError('sensor_id must be in range [0, 7]')
        self.buffer[4] = (self.buffer[4] & 0xf8) | (value & 0x07)


@click.group()
@click.option(
    '-i',
    '--interface',
    default='socketcan',
    type=click.Choice(['socketcan', 'socketcan_native', 'socketcan_ctypes']),
    help='CAN bus interface type',
)
@click.option(
    '-b',
    '--bitrate',
    default=500000,
    type=int,
    help='CAN bus bitrate in bits per second',
)
@click.option(
    '-c',
    '--channel',
    default='can0',
    help='CAN bus channel (e.g., can0, can1)',
)
@click.pass_context
def main(ctx, interface, bitrate, channel):
    """whl-nanoradar-conftool
    """
    ctx.ensure_object(dict)
    ctx.obj['interface'] = interface
    ctx.obj['channel'] = channel
    ctx.obj['bitrate'] = bitrate


@main.command()
@click.option(
    '--message_id',
    default=0x200,
    type=int,
    help='CAN message ID to use for configuration',
)
@click.option(
    '-s',
    '--set',
    'settings',
    nargs=2,
    multiple=True,
    type=(str, int),
    help='Set a configuration option (e.g., --set sensor_id 1)',
)
@click.pass_context
def config(ctx, message_id, settings):
    """
    """
    config = RadarConfig()
    for key, val in settings:
        if hasattr(config, key):
            config.__setattr__(key, val)

    with can.Bus(**ctx.obj) as bus:
        # TODO(all): use dbc and cantools to encode the message
        message = can.Message(arbitration_id=message_id,
                              data=config.buffer,
                              is_extended_id=False)
        bus.send(message)
        print(r'sent configuration message: '
              f'{hex(message_id)}#{config.buffer.hex()}')


@main.command()
@click.option(
    '-t',
    '--timeout',
    default=10,
    help='Timeout for the scan in seconds',
)
@click.pass_context
def scan(ctx, **kwargs):
    """Scan for nano radar devices on the CAN bus."""
    # Placeholder for scanning logic
    begin_time = datetime.datetime.now().timestamp()
    founded_devices = {}
    freq_counter = {}
    with can.Bus(**ctx.obj) as bus:
        finish = False
        while not finish:
            now = datetime.datetime.now().timestamp()
            finish = now - begin_time >= kwargs['timeout']
            if finish:
                break
            message = bus.recv(timeout=1)
            if message is None:
                continue
            # Process the received message
            if message.arbitration_id & 0xf0f == 0x201:
                # received radar configuration message
                # TODO(All): use dbc and cantools to decode the message
                radar_state = RadarState(message.data)
                founded_devices[radar_state.sensor_id] = radar_state
                freq_counter[radar_state.sensor_id] = freq_counter.get(
                    radar_state.sensor_id, 0) + 1
        if not founded_devices:
            click.echo('No nano radar devices found.')
        else:
            print('Found nano radar devices:')
            for sensor_id, state in founded_devices.items():
                count = freq_counter[sensor_id]
                freq = count / kwargs['timeout']
                conjecture_number = round(freq)
                print(f'sensor id: {sensor_id}, '
                      f'conjecture number: {conjecture_number}')
                print(f'{state.pretty_json()}')


if __name__ == '__main__':
    main(obj={})
