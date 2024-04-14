#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File              : build_image.py
# Date              : 2024-02-20 19:24:43
# Last Modified by  : Christophe Vermeren
# Last Modified time: 2024-04-14 09:59:12
#
# Author:           : Christophe Vermeren <lore.phoenix@gmail.com>
#


import inspect
import os
import pathlib
import re
import socket
import subprocess
import sys
import time

# ----------------------------------------------------------------------------
#    _____ _
#   / ____| |
#  | |    | | __ _ ___ ___
#  | |    | |/ _` / __/ __|
#  | |____| | (_| \__ \__ \
#   \_____|_|\__,_|___/___/
# ----------------------------------------------------------------------------


class Verbosity:
    ''' class Verbosity
        Provide a colorfull output to make it better visible
    '''

    # Public class attribute
    verbose = 0

    # Private class attribute
    # Python doesn't have any mechanism that effectively restricts access to
    # any instance variable or method. Python prescribes a convention of
    # prefixing the name of the variable/method with a single or double
    # underscore to emulate the behavior of protected and private access
    # specifiers.
    # The double underscore __ prefixed to a variable makes it private.
    # Private variables
    __red = '\033[31m'
    __green = '\033[32m'
    __blue = '\033[34m'
    __cyan = '\033[36m'
    __yellow = '\033[93m'
    __pink = '\033[95m'
    __reset = '\033[0m'

    def __init__(self, **kwargs) -> None:
        ''' Constructor
            Is a reserved method in Python classes.
            This method called when an object is created from the class and
            it allow the class to initialize the attributes of a class
        '''

        if (sys.platform == "win32"):
            import colorama
            colorama.init()

        self.error = False  # instance public attribute
        self.force = False

        # The super (Verbosity, self) call is equivalent to the parameterless
        # super() call. The first parameter refers to the subclass Verbosity,
        # while the second parameter refers to a Verbosity object which, in
        # this case, is self.
        super(Verbosity, self).__init__()
        self.__dict__.update(**kwargs)  # To assign automatically

    ''' End of def __init__(self, **kwargs) -> None: '''

    # ######################################
    # D E C L A R I N G    S P E C I A L
    # C L A S S   M E T H O D S
    # ######################################
    def __del__(self) -> None:
        ''' Finalizer
             It is called when an object is garbage collected which happens at
             some point after all references to the object have been deleted.
        '''
        try:
            self.v_debug("Running " + __class__.__name__ + " finalizer")
        except TypeError:
            pass
    ''' End of __del__(self) '''

    def __repr__(self):
        ''' Python __repr__() function returns the object representation.
            It could be any valid python expression such as tuple, dictionary,
            string etc.
            This method is called when repr() function is invoked on the
            object, in that case, __repr__() function must return a String
            otherwise error will be thrown.
        '''
        return {
            'error': self.error,
            'verbose': self.verbose}
    ''' End of def __repr__(self) '''

    def __str__(self):
        ''' This method returns the string representation of the object.
            This method is called when print() or str() function is invoked on
            an object.
        '''
        return str(self.__class__) + ": " + str(self.__dict__)
    ''' End of def __str__(self) '''

    # ######################################
    # D E C L A R I N G    P R I V A T E
    # C L A S S   M E T H O D S
    # ######################################

    # ######################################
    # D E C L A R I N G    P U B L I C
    # C L A S S   M E T H O D S
    # ######################################
    def v_debug(self, message, override=False) -> None:
        ''' Display a debug message

            Args:
                message (str): a text message to display
                override (bool): override self.verbose to level higher than 3
        '''

        # Initiate local variables
        severity = f"{self.__blue}[{self.__pink}DEBUG{self.__blue}] "
        severity += self.__reset

        # Regular express to match the string "[START FUNC.]" or "[END FUNC.]"
        regex = r".*(\[(START|END)\s(FUNC\.|CLASS\sMETH.)\]).*"

        if re.match(regex, message):
            if self.verbose > 3:

                if re.match(r".*(START).*", message):
                    print(f"\n{severity}{self.__pink} {message} "
                          + f"{self.__reset}")
                elif re.match(r".*(END).*", message):
                    print(f"{severity}{self.__pink} {message} "
                          + f"{self.__reset}\n\n")
        elif self.verbose > 2 and override is False:
            print(f"{severity}{self.__pink}{self.__reset}{message}")
        elif self.verbose > 3 and override is True:
            print(f"{severity}{self.__pink}{self.__reset}{message}")

        # Cleanup local variable
        del message
        del override
        del regex
        del severity
    ''' End of def v_debug(self, message, pos=None) -> None '''

    def v_error(self, message) -> None:
        ''' Display an error message

            Args:
                message: a text message to display '''

        self.error = True
        print(f"{self.__blue}[{self.__red}ERROR{self.__blue}] {self.__reset} "
              + f"{message}")

        # Cleanup local variable
        del message
        sys.exit(0)
    ''' End of def v_error(self, message) -> None '''

    def v_info(self, message) -> None:
        ''' Display an informational message

            Args:
                message: a text message to display '''
        if self.verbose > 1:
            print(f"{self.__blue}[{self.__cyan}INFO{self.__blue}] "
                  + f"{self.__reset}{message}")

        # Cleanup local variable
        del message
    ''' End of def v_info(self, message) -> None '''

    def v_ok(self, message) -> None:
        ''' Display an OK message

            Args:
                message: a text message to display '''
        if self.verbose > 0:
            print(f"{self.__blue}[{self.__green}OK{self.__blue}] "
                  + f"{self.__reset}{message}")

        # Cleanup local variable
        del message
    ''' End of def v_ok(self, message) -> None '''

    def v_warning(self, message) -> None:
        ''' Display a warning message

            Args:
                message: a text message to display '''
        print(f"{self.__blue}[{self.__yellow}WARN{self.__blue}] "
              + f"{self.__reset}{message}")

        # Cleanup local variable
        del message
    ''' End of def v_warning(self, message) -> None '''

    def where_am_i(self, message=None) -> str:
        ''' Where am I

                Args:
                    message: a text message to display '''

        # Initialize local variable
        msg = ""

        if message is None:
            for x in range(1, len(inspect.stack()) - 1):
                msg += f" {os.path.split(inspect.stack()[x][1])[1]}"
                msg += f"({inspect.stack()[x][3]}::"
                msg += f"{str(inspect.stack()[x][2])}),"

            msg = msg[:-1]
            msg += " ::-------"
            return msg

        elif message.upper() == "START":
            msg = "--------:: [START CLASS METH.]"
            for x in range(1, len(inspect.stack()) - 1):
                msg += f" {os.path.split(inspect.stack()[x][1])[1]}"
                msg += f"({inspect.stack()[x][3]}::"
                msg += f"{str(inspect.stack()[x][2])}),"

            msg = msg[:-1]
            msg += " ::-------"
            return msg

        elif message.upper() == "END":
            msg = "--------:: [END CLASS METH.]"
            for x in range(1, len(inspect.stack()) - 1):
                msg += f" {os.path.split(inspect.stack()[x][1])[1]}"
                msg += f"({inspect.stack()[x][3]}::"
                msg += f"{str(inspect.stack()[x][2])}),"

            msg = msg[:-1]
            msg += " ::-------"
            return msg
    ''' End of def where_am_i(message=None) -> str '''


''' End of class Verbosity: '''


# ----------------------------------------------------------------------------
#    __                  _   _
#   / _|                | | (_)
#  | |_ _   _ _ __   ___| |_ _  ___  _ __
#  |  _| | | | '_ \ / __| __| |/ _ \| '_ \
#  | | | |_| | | | | (__| |_| | (_) | | | |
#  |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|
# ----------------------------------------------------------------------------
def download_file(**kwargs) -> tuple[bool, str]:
    ''' Download image from ...

        Args:
            **kwargs (dict): passing parameters '''

    import requests

    if kwargs['force']:
        try:
            pathlib.Path(kwargs['image']).unlink(missing_ok=True)
        except FileNotFoundError:
            pass
    elif pathlib.Path(kwargs['image']).is_file():
        return False, F"File '{kwargs['image']}' already exist."

    response = requests.get(kwargs['url'], stream=True)

    if response.ok:
        with open(kwargs['image'], "wb") as handle:
            from tqdm import tqdm
            for data in tqdm(response.iter_content(chunk_size=1024)):
                handle.write(data)

        if pathlib.Path(kwargs['image']).is_file():
            return False, f"File '{kwargs['image']}' downloaded."
    else:
        return True, response.raise_for_status()


''' End of def download_file(**kwargs) -> tuple[bool, str] '''


def get_url_paths(html, pattern_string):
    ''' Get URL path file structure

        Args:
            html (str): URL link
            pattern_string (str): pattern to find '''

    import random
    import requests

    # Initialize local variables
    my_headers = [
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64)",
        "Opera/9.25 (Windows NT 5.1; U; en)",
        "Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5)",
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101"
    ]
    headers = {'User-Agent': random.choice(my_headers)}

    response = requests.get(html, headers=headers)
    if response.ok:
        pattern = re.compile(pattern_string, re.S)
        downloadurl = re.findall(pattern, str(response.text))
        return downloadurl
    else:
        return response.raise_for_status()


''' End of def get_url_paths(html, pattern_string) '''


def import_package(module) -> bool:
    ''' Import attempt of package

        Args:
            module (str): name of package '''

    try:
        globals()[module] = __import__(module)
    except ModuleNotFoundError:
        return False
    else:
        return True


''' End of def import_module(module) -> bool '''


def install_package(module) -> bool:
    ''' Install package using pip

        Args:
            module (str): name of package '''

    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', module],
            stderr=subprocess.PIPE, shell=False)
    except subprocess.CalledProcessError as e:
        print(e)
        return False
    return True


''' End of def install_package(module) -> bool '''


def is_tool(console, name) -> None:
    ''' Check if application exist

        Args:
            console (verbosity): passing a class object
            name (str): name of application '''
    try:
        subprocess.check_call(name,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE,
                              shell=False,
                              timeout=None
                              )
    except FileNotFoundError:
        console.v_error(f"No such file or directory: '{name[0]}'"
                        + "\n\t Download & install software from "
                        + "https://www.qemu.org/download/ ")


''' End of def is_tool(console, name) -> None '''


def main():
    ''' Python Main Function is the beginning of any Python program. When we
            run a program, the interpreter runs the code sequentially and will
            not run the main function if imported as a module, but the Main
            Function gets executed only when it is run as a Python program.
        '''

    # Initialise default variables
    error = False
    localtime = time.asctime(time.localtime(time.time()))
    packages_to_import = ['bs4', 'colorama',
                          'argparse', 'random', 'requests', 'tqdm']
    required_applications = ['qemu-img', 'qemu-system-x86_64']

    for package in packages_to_import:

        if import_package(package):
            globals()[package] = __import__(package)
        else:
            if install_package(package):
                globals()[package] = __import__(package)
            else:
                error = True
    ''' End of for package in packages_to_import '''

    if error:
        # There is an issue / error / problem and that is why the program
        # is exiting.
        sys.exit(1)

    if (sys.platform == "win32"):
        # Start filtering ANSI escape sequences out of any text sent to stdout
        # or stderr, and will replace them with equivalent Win32 calls.
        colorama.init()

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", required=False, action="store_true",
                        default=False,
                        help="list of available Linux distributions")
    parser.add_argument("-d", "--distro", action="store", default="archlinux",
                        help="name of Linux distribution")
    parser.add_argument("-f", "--force", action="store_true",
                        help="remove iso & image, if exist")
    parser.add_argument("-s", "--size", action="store", default="3G",
                        help="cloud image size (default=3G)")
    parser.add_argument("-v", "--verbose", action="count",
                        help="increase output verbosity")
    parser.add_argument("--memory", action="store", default=2048,
                        help="set memory in MB(default=2048)")

    args = parser.parse_args()

    force = args.force if args.force else False
    size = args.size if args.size else "3G"
    verbose = args.verbose if args.verbose else 0
    linux_distro = args.distro.lower() if args.distro else None

    cp = Verbosity(**{'force': force, 'verbose': verbose})
    cp.v_ok(f"Running file '{os.path.basename(__file__)}' from "
            + f"{socket.gethostname()} on {localtime}")

    # Validate passed arguments
    if args.list:
        print("Available Linux distributions to choose from:")
        for distro in DISTRO_OS:
            print(f"  - {distro}")

        # A clean exit without any errors / problems
        sys.exit(0)
    ''' End of if args.list '''

    if linux_distro not in DISTRO_OS.keys():
        cp.v_error("The value behind the argument '--distro' isn't part of "
                   + "the available Linux distributions.\n       Please use "
                   + "the argument -l/--list to view of the available Linux "
                   + "distributions.")
    else:
        cp.v_info(f"--distro {linux_distro} listed under available Linux "
                  + "distributions")

    # Loop through list of required application and verify if they are
    # available on the running system. If not, exit.
    for app in required_applications:
        is_tool(cp, [app, '--version'])

    result = get_url_paths(
        DISTRO_OS[linux_distro]['url'], DISTRO_OS[linux_distro]['url_pattern'])

    filtered_values = list(
        filter(
            lambda v: re.match(DISTRO_OS[linux_distro]['filter_value'], v),
            result))

    # filtered_values is a list but to a new string variable
    if len(filtered_values) == 0:
        cp.v_error("Unable to find an image with the following string "
                   + f"pattern '{DISTRO_OS[linux_distro]['filter_value']}"
                   + "'.")
    else:
        filtered_values.sort(reverse=True)
        html = filtered_values[0]

        if not re.search(r"^https://", html):
            # If string doesn't start with https:// then add url
            html = DISTRO_OS[linux_distro]['url'] + html
    ''' End of if len(filtered_values) == 0 '''

    # Delete variables
    del filtered_values
    del result

    iso_image = html.split("/")[-1]
    version_image = re.compile(
        r"(([0-9]+\.[0-9]+\.[0-9]+)|([0-9]+\.[0-9]+)|([0-9]+T))"
    ).search(iso_image).group(0)

    cloud_image = f"{linux_distro}-cloud-{version_image}-x86_64.img"
    cp.v_info(f"CD/DVD ISO image: {iso_image}")
    cp.v_info(f"Linux distribution version: {version_image}")
    cp.v_info(f"Cloud image name: {cloud_image}")

    # Download ISO image
    error, message = download_file(
        **{'force': force, 'image': iso_image, 'url': html})
    if error:
        cp.v_error(message)
    else:
        cp.v_ok(message)

    # Remove any pre-existing cloud image
    pathlib.Path(cloud_image).unlink(missing_ok=True)

    # Create a block device image
    try:
        subprocess.run(
            f"qemu-img create -f raw {cloud_image} {size}",
            check=True,
            encoding='utf-8',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            shell=True,
            timeout=30
        )
    except Exception as e:
        cp.v_error(e)
    else:
        if pathlib.Path(cloud_image).is_file():
            cp.v_ok(f"A block device image '{cloud_image} has been created.")
        else:
            cp.v_error("Unable to create a block device image with the name "
                       + f"'{cloud_image}'.")

    # QEMU PC System emulator
    cmd_linux = f'''qemu-system-x86_64 -cpu kvm64 \
-smp 2 \
-m {args.memory} \
-k fr_be \
-machine q35 \
-cdrom {iso_image} \
-drive file={cloud_image},if=virtio,media=disk,format=raw,cache=none \
-device virtio-scsi-pci,id=virtio \
-enable-kvm \
-device virtio-serial-pci \
-device virtserialport,chardev=spicechannel0,name=com.redhat.spice.0 \
-chardev spicevmc,id=spicechannel0,name=vdagent \
-nic user,model=virtio-net-pci,hostfwd=tcp::8022-:22 \
-vga qxl \
-boot c
'''

    cmd_windows = f'''qemu-system-x86_64 -cpu kvm64 \
-smp 2 \
-m {args.memory} \
-k fr_be \
-machine q35 \
-cdrom {iso_image} \
-drive file={cloud_image},if=virtio,media=disk,format=raw,cache=none \
-device virtio-scsi-pci,id=virtio \
-device virtio-serial-pci \
-nic user,model=virtio-net-pci,hostfwd=tcp::8022-:22 \
-vga qxl \
-boot c
'''
    try:
        if (sys.platform == "win32"):
            subprocess.run(
                cmd_windows,
                check=True,
                encoding='utf-8',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                shell=True,
                timeout=None
            )
        else:
            subprocess.run(
                cmd_linux,
                check=True,
                encoding='utf-8',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                shell=True,
                timeout=None
            )

    except Exception as e:
        cp.v_error(e)


# ----------------------------------------------------------------------------
#                   _
#                  (_)
#   _ __ ___   __ _ _ _ __
#  | '_ ` _ \ / _` | | '_ \
#  | | | | | | (_| | | | | |
#  |_| |_| |_|\__,_|_|_| |_|
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    DISTRO_OS = {
        'archlinux': {
            'filter_value': 'archlinux-[0-9]+.[0-9]+.[0-9]+-.*.iso$',
            'url': 'https://archlinux.cu.be/iso/latest/',
            'url_pattern': 'href=\"(.*?)\"'
        },
        'manjaro': {
            'filter_value': '.*/(manjaro-xfce-.*.iso)$',
            'url': 'https://manjaro.org/download/',
            'url_pattern': '<a id=\"btn-mi\" href=\"(.*?)\"'
        }
    }
    main()
