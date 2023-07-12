import os
import csv
import json
import requests
import argparse
from argparse import RawDescriptionHelpFormatter
import platform

# -------------------------------------------------------------------------------------------
# change directory
if platform.system() == 'Windows':
    os.chdir('C:/Users/hp/Documents/GitHub Repositories/Scraping/cfscanner/')

# -------------------------------------------------------------------------------------------
# section variable
dir_template = 'template'
template_xray = 'xray.json'
template_sing_box = 'sing-box.json'

dir_log = 'log'
dir_result = 'result'
dir_xray_configs = '.configs'

# -------------------------------------------------------------------------------------------
# section function


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def color_text(text: str, rgb: tuple, bold: bool = False):
    """prints a colored text in the terminal using ANSI escape codes based on the rgb values

    Args:
        text (str): the text to be printed
        rgb (tuple): the rgb values of the color
    """
    if bold:
        return f"\033[1m\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[m"
    else:
        return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[m"


def _title(text):
    return color_text(text, (250, 250, 0), bold=True)
    # return color_text(text, (128, 128, 0), bold=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description=color_text(
            'Run core type of v2ray configs',
            rgb=(37, 250, 0),
            # rgb=(76, 122, 164),
            bold=True
        ),
        add_help=False,
        formatter_class=SmartFormatter
    )

    # def formatter(prog): return argparse.HelpFormatter(
    #     prog, width=100, max_help_position=64)
    # parser.formatter_class = formatter

    ############################################################
    # Help options
    help_options = parser.add_argument_group(_title("Help"))
    help_options.add_argument(
        "--help", "-h",
        help="Show this help message and exit",
        action="help",
    )
    help_options.add_argument(
        "--example",
        help="R|Some example: \n"
        "py -m sub_cf_ip --convert 1 --number 3 -H Dusseldorf.kotick.site -b .\\bin\\xray.exe \n"
        "py -m sub_cf_ip --convert 1 --number 3 -H Dusseldorf.kotick.site -ct sing-box -b .\\bin\\sign-box.exe \n"
        "py -m sub_cf_ip --convert 1 --number 3 -H Dusseldorf.kotick.site -b .\\bin\\xray.exe -ip discord.com \n"
        "py -m sub_cf_ip -b .\\bin\\sign-box.exe \n"
        "py -m sub_cf_ip -b .\\bin\\sign-box.exe -cn 2",
    )
    ############################################################
    # Port options
    port_option = parser.add_argument_group(_title("Port options"))
    port_option.add_argument(
        "--socks-port", "-sp",
        help="socks port, default is 10808",
        type=int,
        metavar="",
        default=10808,
        dest="socks_port",
        required=False
    )
    port_option.add_argument(
        "--http-port", "-hp",
        help="socks port, default is 10809",
        type=int,
        metavar="",
        default=10809,
        dest="http_port",
        required=False
    )
    port_option.add_argument(
        "--cutter-port", "-cp",
        help="default is 0, use 22500 ot any port number to turn it on",
        type=int,
        metavar="",
        default=0,
        dest="cutter_port",
        required=False
    )
    ############################################################
    config_option = parser.add_argument_group(_title("Config detail options"))
    config_option.add_argument(
        "--internet-protocol", "-ip",
        help="set your favorite ip on config",
        type=str,
        metavar="",
        dest="ip",
        required=False
    )
    config_option.add_argument(
        "--port", "-p",
        help="set your favorite ip on config",
        type=int,
        metavar="",
        default=443,
        dest="port",
        required=False
    )
    config_option.add_argument(
        "--fingerprint", "-fp",
        help=" fingerprint, default is chrome. all type is : chrome, firefox, safari, ios, android, edge, 360, qq, random, randomized ",
        type=str,
        metavar="",
        default='chrome',
        dest="fingerprint",
        required=False
    )
    config_option.add_argument(
        "--host", "-H",
        help=" location config, default is Lille.kotick.site --- Dusseldorf.kotick.site --- Kansas.kotick.site --- Amsterdam.kotick.site --- Lille.kotick.site --- LosAngeles.kotick.site",
        type=str,
        metavar="",
        default='Lille.kotick.site',
        dest="host",
        required=False
    )
    config_option.add_argument(
        "--UUID", "-uuid",
        help="enter your uuid like: 4EA68717-BD05-486C-A177-247400D35C18",
        type=str,
        metavar="",
        default='',
        dest="uuid",
        required=False
    )
    ############################################################
    sort_option = parser.add_argument_group(_title("Sort options"))
    sort_option.add_argument(
        "--download-sort", "-ds",
        help="default is speed. all type is: speed, latency, jitter",
        type=str,
        metavar="",
        default='speed',
        dest="download_sort",
        required=False
    )
    sort_option.add_argument(
        "--upload-sort", "-us",
        help="default is off. all type is: speed, latency, jitter",
        type=str,
        metavar="",
        default='',
        dest="upload_sort",
        required=False
    )
    sort_option.add_argument(
        "--number", "-n",
        help="default is 5. just 5 configs of desire index is converted to json",
        type=int,
        metavar="",
        default=5,
        dest="number",
        required=False
    )
    ############################################################
    run_option = parser.add_argument_group(_title("Run options"))
    run_option.add_argument(
        "--core-type", "-ct",
        help="default is xray, it use ??? template to make its json configuration. all supported type is 'xray' , 'sing-box' ",
        type=str,
        metavar="",
        default='xray',
        dest="core_type",
        required=False
    )
    run_option.add_argument(
        "--binpath", "-b",
        help="run 1.json by bin",
        type=str,
        metavar="",
        dest="binpath",
        required=False
    )
    ############################################################
    others_option = parser.add_argument_group(_title("Others"))
    others_option.add_argument(
        "--config-number", "-cn",
        help="run number.json by bin. it's must be lower than number argument",
        type=int,
        metavar="",
        default=1,
        dest="config_number",
        required=False
    )
    others_option.add_argument(
        "--convert", "-c",
        help="cnvert last scan ip to json file",
        type=bool,
        metavar="",
        default=0,
        dest="convert",
        required=False
    )

    return parser.parse_args()


def newest(path):
    # find the latest result csv
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


arguments = parse_args()

if arguments.convert:
    latest_csv = newest(dir_result)
    # -------------------------------------------------------------------------------------------
    # section load data and processing it

    # find core template based on OS type
    if arguments.core_type == 'xray':
        path_file = os.path.join(dir_template, template_xray)
    if arguments.core_type == 'sing-box':
        path_file = os.path.join(dir_template, template_sing_box)

    # read json template
    with open(path_file, 'r') as file:
        json_template = json.load(file)

    # find newest uuid
    if arguments.uuid:
        uuid = arguments.uuid
    else:
        try:
            uuid = requests.get(
                'https://raw.githubusercontent.com/RescueNet/TelegramFreeServer/main/others/cloudflare/advanced/uuid', timeout=2).text[:-1]
        except:
            with open(os.path.join('..', 'output', 'rescuenet', 'others', 'cloudflare', 'advanced', 'uuid'), 'r') as file:
                uuid = file.readlines()[0][:-1]

    # -------------------------------------------------------------------------------------------
    # section clean directory

    # delete .configs and log and result directory file
    if dir_xray_configs in os.listdir():
        for item in os.listdir(dir_xray_configs):
            os.remove(os.path.join(dir_xray_configs, item))
    if dir_log in os.listdir():
        for item in os.listdir(dir_log):
            os.remove(os.path.join(dir_log, item))
    if dir_result in os.listdir():
        for item in os.listdir(dir_result):
            if os.path.join(dir_result, item) != latest_csv:
                os.remove(os.path.join(dir_result, item))

    # -------------------------------------------------------------------------------------------
    # section load initial data and processing and making json configuration
    download = {
        'ip': 0,
        'speed': 1,
        'latency': 3,
        'jitter': 5,
    }
    upload = {
        'ip': 0,
        'speed': 2,
        'latency': 4,
        'jitter': 6,
    }
    sort_types = {
        'speed': True,
        'latency': True,
        'jitter': False,
    }

    # read latest result csv
    with open(latest_csv) as file:
        reader = csv.reader(file)
        data = list(reader)

    data = [(properties[0], float(properties[1]), float(properties[2]), float(properties[3]),
            float(properties[4]), float(properties[5]), float(properties[6])) for properties in data[1:]]
    # sort data based on latest result csv
    if arguments.upload_sort:
        sort_type = sort_types.get(arguments.upload_sort, True)
        sort_by = upload.get(arguments.upload_sort, 2)
        ip_sets = sorted(data, key=lambda x: x[sort_by], reverse=sort_type)
    else:
        sort_type = sort_types.get(arguments.download_sort, True)
        sort_by = download.get(arguments.download_sort, 1)
        ip_sets = sorted(data, key=lambda x: x[sort_by], reverse=sort_type)

    # make configurations
    if arguments.core_type == 'xray':
        json_template['inbounds'][0]['port'] = arguments.socks_port
        json_template['inbounds'][1]['port'] = arguments.http_port
        json_template['outbounds'][0]['settings']['vnext'][0]['port'] = arguments.port
        json_template['outbounds'][0]['streamSettings']['tlsSettings']['serverName'] = arguments.host
        json_template['outbounds'][0]['streamSettings']['tlsSettings']['fingerprint'] = arguments.fingerprint
        json_template['outbounds'][0]['streamSettings']['wsSettings']['headers']['Host'] = arguments.host
        json_template['outbounds'][0]['settings']['vnext'][0]['users'][0]['id'] = uuid
        number = 1
        if arguments.cutter_port:
            json_template['outbounds'][0]['settings']['vnext'][0]['address'] = "127.0.0.1"
            json_template['outbounds'][0]['settings']['vnext'][0]['port'] = arguments.cutter_port
            with open(os.path.join('.configs', f'{number}.json'), 'w+') as file:
                json.dump(json_template, file, indent=4)
        else:
            if arguments.ip:
                json_template['outbounds'][0]['settings']['vnext'][0]['address'] = arguments.ip
                with open(os.path.join('.configs', f'{number}.json'), 'w+') as file:
                    json.dump(json_template, file, indent=4)
            else:
                for clean_ip in ip_sets:
                    if number <= arguments.number:
                        json_template['outbounds'][0]['settings']['vnext'][0]['address'] = clean_ip[0]
                        with open(os.path.join('.configs', f'{number}.json'), 'w+') as file:
                            json.dump(json_template, file, indent=4)
                    number += 1

    # make configurations
    if arguments.core_type == 'sing-box':
        json_template['inbounds'][0]['listen_port'] = arguments.socks_port
        json_template['inbounds'][1]['listen_port'] = arguments.http_port
        json_template['outbounds'][0]['server_port'] = arguments.port
        json_template['outbounds'][0]['tls']['server_name'] = arguments.host
        json_template['outbounds'][0]['tls']['utls']['fingerprint'] = 'android'
        json_template['outbounds'][0]['transport']['headers']['Host'] = arguments.host
        json_template['outbounds'][0]['uuid'] = uuid
        number = 1
        if arguments.cutter_port:
            json_template['outbounds'][0]['server'] = "127.0.0.1"
            json_template['outbounds'][0]['server_port'] = arguments.cutter_port
            with open(os.path.join('.configs', f'{number}.json'), 'w+') as file:
                json.dump(json_template, file, indent=4)
        else:
            if arguments.ip:
                json_template['outbounds'][0]['server'] = arguments.ip
                with open(os.path.join('.configs', f'{number}.json'), 'w+') as file:
                    json.dump(json_template, file, indent=4)
            else:
                for clean_ip in ip_sets:
                    if number <= arguments.number:
                        json_template['outbounds'][0]['server'] = clean_ip[0]
                        with open(os.path.join('.configs', f'{number}.json'), 'w+') as file:
                            json.dump(json_template, file, indent=4)
                    number += 1


if arguments.binpath:
    if arguments.config_number:
        os.system(
            f"{arguments.binpath} run -c .configs/{arguments.config_number}.json")
    os.system(f"{arguments.binpath} run -c .configs/1.json")
