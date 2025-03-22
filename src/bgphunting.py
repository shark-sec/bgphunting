import requests
import re
import argparse
from prettytable import PrettyTable
from termcolor import colored
from colorama import Fore, init
import sys

# 初始化 colorama
init(autoreset=True)

# 读取当前目录下的 banner.txt 文件
try:
    with open("banner.txt", "r") as file:
        banner_content = file.read()
    print(Fore.BLUE + banner_content)  # 以蓝色输出
    print(Fore.RED + "        BGPhunting Exposing your organization")
    print("")
    print(Fore.GREEN + "   SHARK Security - Advance Pentest Copyright © 2025")
    print(Fore.WHITE + "     James Taylor " + Fore.GREEN + "<" + Fore.CYAN + "https" + Fore.GREEN + "://" + Fore.YELLOW + "t.me/sharkecuriTy" + Fore.GREEN + ">")
    print("")
except FileNotFoundError:
    print(Fore.RED + "Error: banner.txt file not found. Please make sure the file exists in the current directory.")
    sys.exit(1)
except Exception as e:
    print(Fore.RED + f"Error: An error occurred while reading the file - {e}")
    sys.exit(1)

def get_asns_for_org(org_name):
    """Fetch all ASNs associated with an organization from bgp.he.net."""
    url = f"https://bgp.he.net/search?search%5Bsearch%5D={org_name}&commit=Search"
    response = requests.get(url)

    if response.status_code == 200:
        # Extract ASNs using regex
        asns = re.findall(r"AS\d+", response.text)
        if asns:
            return list(set(asns))  # Return unique ASNs
        else:
            print(f"[INFO]: No ASNs found for organization '{org_name}'.")
            return []
    else:
        print(f"[ERROR]: Failed to fetch ASNs for organization '{org_name}'.")
        return []

def get_ip_ranges_for_asn(asn):
    """Fetch all IP ranges associated with a specific ASN from bgp.he.net."""
    url = f"https://bgp.he.net/{asn}#_prefixes"
    response = requests.get(url)

    if response.status_code == 200:
        # Extract IP ranges using regex
        ip_ranges = re.findall(r"\d{1,3}(?:\.\d{1,3}){3}/\d+", response.text)
        return ip_ranges
    else:
        print(f"{colored('[ERROR]:', 'red')} Failed to fetch IP ranges for ASN '{asn}'.")
        return []

def display_asn_and_ip_ranges(org_name):
    """Display all ASNs and IP ranges associated with an organization."""
    asns = get_asns_for_org(org_name)

    if asns:
        print(f"\n{colored('searching for:', 'green')} {colored(org_name, 'yellow')}\n")

        for asn in asns:
            # Print the ASN number first
            print(colored(f"ASN: {asn}", "red"))

            # Create a table for each ASN and its IP ranges
            table = PrettyTable()
            table.field_names = [colored("ASN", "green"), colored("IP Addresses", "blue")]

            # Fetch the IP ranges for the ASN
            ip_ranges = get_ip_ranges_for_asn(asn)

            if ip_ranges:
                for ip in ip_ranges:
                    table.add_row([colored(asn, "red"), colored(ip, "yellow")])
            else:
                table.add_row([colored(asn, "red"), colored("No IP ranges found", "red")])

            print(table)
    else:
        print(f"{colored('[INFO]:', 'yellow')} No ASNs found for organization '{org_name}'.")

class CustomHelpFormatter(argparse.HelpFormatter):
    """Custom help formatter to colorize the help message."""
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = f"{Fore.GREEN}Usage: {Fore.RESET}"
        return super().add_usage(usage, actions, groups, prefix)

    def start_section(self, heading):
        if heading == "optional arguments":
            heading = f"{Fore.GREEN}{heading}{Fore.RESET}"
        return super().start_section(heading)

    def _format_action(self, action):
        # Colorize the option strings and help text
        if action.option_strings:
            option_strings = ", ".join(action.option_strings)
            option_strings = f"{Fore.GREEN}{option_strings}{Fore.RESET}"
            help_text = f"{Fore.GREEN}{action.help}{Fore.RESET}"
            return f"  {option_strings.ljust(20)} {help_text}\n"
        return super()._format_action(action)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"{Fore.GREEN}ASN and IP Range Finder for an Organization{Fore.RESET}",
        formatter_class=CustomHelpFormatter,
        usage=argparse.SUPPRESS,  # 禁用默认的 usage 信息
        add_help=False  # 禁用默认的 -h/--help 选项
    )
    parser.add_argument(
        "-h", "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help"
    )
    parser.add_argument(
        "-s", "--search",
        dest="org",
        help="Search for ASNs and IP ranges on BGP for your organization",
        required=True
    )
    return parser.parse_args()

def main():
    if len(sys.argv) == 1:
        # 如果没有输入任何参数，直接退出
        sys.exit(0)
    
    args = parse_arguments()  # 直接调用 parse_arguments() 并获取返回值
    
    try:
        org_name = args.org
        display_asn_and_ip_ranges(org_name)
    except SystemExit as e:
        if e.code == 2:  # 无参数时的退出码
            pass  # 不输出任何内容
        else:
            raise  # 重新抛出其他异常

if __name__ == "__main__":
    main()

