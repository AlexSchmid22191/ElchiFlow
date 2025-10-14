import argparse
import time
from pathlib import Path

from platformdirs import user_data_dir
from serial import SerialException

import ElchiSetBase as Esb
from src.Drivers.Aera import ROD4
from src.Drivers.ElchWorks import Ventolino
from src.Drivers.TestDevices import TestMFC
from src.ElchiSet.ElchiSetBase import delayed_exit

device_types = {'Ventolino': Ventolino, 'Area ROD-4': ROD4, 'Test': TestMFC}


def validate_config(config: dict) -> None:
    if 'device' not in config:
        delayed_exit('Missing device section in config file!', 1)

    required = {'type', 'port'}
    missing = required - config['device'].keys()
    if missing:
        Esb.delayed_exit(f'Missing entries in config file: {missing}!', 1)

    if config['device']['type'] not in device_types:
        Esb.delayed_exit(f'Invalid device type encountered: {config["device"]["type"]}!\n'
                         f' Valid device types: {", ".join(device_types.keys())}', 1)

    for key in config:
        if key == 'device':
            continue
        elif not isinstance(key, int) or key < 1:
            delayed_exit(f'Invalid preset key encounterd: {key}! Valid presetes are positive integers!')
        else:
            for inner_key, inner_value in config[key].items():
                if inner_key not in [1, 2, 3, 4]:
                    delayed_exit(f'Invalid channel encounterd in preset {key}: {inner_key}!'
                                 f' Valid channels are: 1, 2, 3 and 4!')
                if not isinstance(inner_value, (int, float)) or inner_value < 0 or inner_value > 100:
                    delayed_exit(f'Invalid value encountered in preset {key} channel {inner_key}: {inner_value}!'
                                 f' Valid values are: 0 to 100')

    print('Config validation successful!')


def execute_preset(preset: dict, device_type, port) -> None:
    device = None
    try:
        device = device_types[device_type](port)
    except SerialException:
        delayed_exit(f'Error connecting {device} at {port}!')
    else:
        print('Device connection successful!')

    for channel, value in preset.items():
        try:
            device.set_flow(int(channel), value)
        except SerialException as e:
            delayed_exit(f'Communication errorm when setting flow on channel {channel}: {e}')
        else:
            print(f'Set channel {channel} to {value} %')


def main():
    print('Hi! This is ElchiGas!')

    parser = argparse.ArgumentParser(
        description='ElchiGas is a CLI application for adjusting mass flow controller via a Vewntolino or ROD-4'
                    ' control device!',
        fromfile_prefix_chars='+')

    parser.add_argument('preset', type=float, help='Preset number to load from configuration file!')

    args = parser.parse_args()

    print('I read the following command line arguments:')
    for k, v in vars(args).items():
        print(f"{k}: {v}")

    data_dir = Path(user_data_dir('ElchiGas', 'ElchWorks', roaming=True))
    data_dir.mkdir(parents=True, exist_ok=True)
    config = Esb.load_config(data_dir / 'config.yaml')
    validate_config(config)

    preset = None
    try:
        preset = config[int(args.preset)]
    except KeyError:
        delayed_exit(f'Preset {args.preset} not found in configuration file!', 1)

    execute_preset(preset, config['device']['type'], config['device']['port'])
    print('Done, exiting in 5 seconds!')
    for i in range(5):
        print(f'{5 - i} ...')
        time.sleep(1)


if __name__ == '__main__':
    main()
