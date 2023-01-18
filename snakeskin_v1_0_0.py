#!/usr/bin/env python

"""snakeskin.py: MsfVenom user interface wrapper

Snakeskin improves the MsfVenom user experience by guiding the user through the generation of customized payloads via a menu-driven user interface. It interacts
with MsfVenom in real time to obtain generic and payload-specific options and their default values. Depending upon the option, the user can add, remove or
modify its value through either freeform data entry or searchable, paginated submenus. Finally, Snakeskin teaches MsfVenom syntax by giving the user the
opportunity to compare the MsfVenom command issued at the command prompt to feedback received from MsfVenom.

This program is free software. You can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""

__author__ = "Devon Meier"
__email__ = "devon@devonmeier.com"
__license__ = "GNU GPLv3"
__status__ = "Production"
__version__ = "1.0.0"
__year__ = "2023"

from getpass import getpass
from itertools import accumulate
from math import ceil
from os.path import isfile
from random import choice
from re import sub
from subprocess import getoutput

def display_menu(options, page, header, footer, search):
    number_of_options = len(options)
    border = "-" * 119
    print("\n" + border + "\nSnakeskin v" + __version__ + " - " + header + "enu\n" + border)

    if number_of_options:

        for scope in [range(group, min(group + 3, number_of_options)) for group in range((page - 1) * 30, min(page * 30, number_of_options), 3)]:

            if type(options[0]) is list:

                print(
                    " ".join(
                        [
                            "[" + str(index_number + 1).rjust(3) + "] " + ellipsis(["", "*"][options[index_number][2]] + options[index_number][0])
                            for index_number
                            in scope
                        ]
                    )
                    + "\n"
                    + " ".join([" " * 6 + ellipsis(options[index_number][1]) for index_number in scope])
                )

            else:
                print(" ".join(["[" + str(index_number + 1).rjust(3) + "] " + ellipsis(options[index_number]) for index_number in scope]))

    else:
        print("No options available.")

    if search:
        print(border + "\n" + search)

    print(border + "\n" + footer + "\n" + border)

def ellipsis(text):
    return sorted([text, text[:30] + "." * 3], key = len)[0].ljust(33)

def main():

    splash = (
        "\n                                    ===============\n"
        "                                 =====================             ============\n"
        "           =========           ===========   ==========          ===========\n"
        "       =================      =========         ========       ==========\n"
        "     =========   =========   ========            ========    ======\n"
        "    ======           ======  ========            ========   ====\n"
        "    =====             ======  ========           ========  ====\n"
        "    =====             ======   ========         ========   ====\n"
        "    ======            ======    =========      ========    ====\n"
        "     ======          =======      ========     =======     =====\n"
        "       ======        ======        =========   ======       ====\n"
        "=        ======     =======          ========  =======     =====\n"
        "==         =====    ======            =======   ===============\n"
        " ==          ====   ======             =======    ===========\n"
        " ==          ====   =======           ========\n"
        "  ===       =====   ========         ========   Snakeskin v{version}\n"
        "   ============       =========   ==========    MsfVenom User Interface Wrapper\n"
        "       =====           ===================      {year} {author}\n"
        "                          =============         {email}\n"
        "\nPress the Enter key to continue..."
    ).format(version = __version__, year = __year__, author = __author__, email = __email__)

    while "=" in splash:
        splash = splash.replace("=", choice([character for character in "~!@#$%^&*()-+[]{};:,.<>?/" if character != splash[splash.index("=") - 1]]), 1)

    getpass(splash)

    menus = {
        "generic": [
            [option[10:26].strip().replace("arch", "architecture"), "", "payload" in option[10:26], option[37:]]
            for option
            in getoutput("msfvenom --help").split("\n")[6:]
            if option[10:26].strip() not in ["list", "list-options", "out", "timeout", "help"]
        ],
        "basic": [],
        "advanced": [],
        "evasion": []
    }

    specific_menus = [menu for menu in menus.keys() if menu != "generic"]

    submenus = {
        "architecture": "[architecture.strip() for architecture in getoutput('msfvenom --list archs').split('\\n')[6:-1]]",
        "encoder": "[encoder.split()[0] for encoder in getoutput('msfvenom --list encoders').split('\\n')[6:-1]]",
        "encrypt": "[encrypt.strip() for encrypt in getoutput('msfvenom --list encrypts').split('\\n')[6:-1]]",
        "format": (
            "sorted([format.strip() for format in getoutput('msfvenom --list formats').split('\\n') if format.strip().replace('-', '').replace('=', '') and "
            "'Name' not in format and '[--format <value>]' not in format])"
        ),
        "payload": "[payload.split()[0] for payload in getoutput('msfvenom --list payloads').split('\\n')[6:-1] if 'generic/' not in payload]",
        "platform": "[platform.strip() for platform in getoutput('msfvenom --list platforms').split('\\n')[6:-1]]"
    }

    menu_current = "generic"
    menu_page = 1
    menu_selection = ""

    while menu_selection != "q":
        menu_options = menus[menu_current]
        menu_number_of_options = len(menu_options)
        menu_number_of_pages = max(1, int(ceil(menu_number_of_options / 30)))

        display_menu(
            menu_options,
            menu_page,
            menu_current.title() + " Options M",
            "Page: [N]ext, [P]revious | Menu: [G]eneric, [B]asic, [A]dvanced, [E]vasion | Miscellaneous: e[X]ecute, [Q]uit.",
            ""
        )

        menu_selection = input("\nSnakeskin (page " + str(menu_page) + " of " + str(menu_number_of_pages) + "): ").lower()

        try:
            menu_selection = int(menu_selection) - 1
        except ValueError:

            if menu_selection == "n":

                if menu_page == menu_number_of_pages:
                    print("\nYou have reached the last page.")
                else:
                    menu_page += 1

            elif menu_selection == "p":

                if menu_page == 1:
                    print("\nYou have reached the first page.")
                else:
                    menu_page -= 1

            elif menu_selection in ["g", "b", "a", "e"]:
                menu_page = 1
                menu_current = next(filter(lambda menu_name: menu_name.startswith(menu_selection), ["generic", "basic", "advanced", "evasion"]))

            elif menu_selection == "x":
                incomplete = ""

                for menu, options in menus.items():
                    missing = [option[0] for option in options if not option[1] and option[2]]

                    if missing:
                        multiple = bool(len(missing) - 1)
                        plural = ["", "s"][multiple]

                        incomplete += (
                            "\n"
                            + menu.title()
                            + " option"
                            + plural
                            + " "
                            + " and".join(", ".join(missing).rsplit(",", 1))
                            + " require"
                            + ["s a", ""][multiple]
                            + " value"
                            + plural
                            + "."
                        )

                if incomplete:
                    print(incomplete)
                else:
                    proceed_selection = ""

                    while proceed_selection not in ["y", "n"]:
                        proceed_selection = input("\nAre you sure you want to proceed with payload generation? ").lower()

                        if proceed_selection == "y":
                            file_selection = ""

                            while not file_selection:
                                file_selection = input("\nEnter a file name: ").strip()

                                if isfile(file_selection):
                                    print("\nThe file '" + file_selection + "' already exists. Please chooose a different file name.")
                                    file_selection = ""

                            generic_arguments = ["--" + option[0].replace("architecture", "arch") + " " + option[1] for option in menus["generic"] if option[1]]

                            specific_arguments = [
                                option[0] + "='" + option[1] + "'"
                                for option
                                in sum([options for menu, options in menus.items() if menu in specific_menus], [])
                                if option[1]
                            ]

                            command = "msfvenom " + " ".join(generic_arguments + specific_arguments) + " -o " + file_selection
                            print("\nIssuing the following command to MsfVenom: \n\n" + command + "\n\nAttempting payload generation. Please wait...")
                            error = [line for line in getoutput(command).split("\n") if "error:" in line.lower()]

                            if error:

                                print(
                                    "\nPayload generation failed. MsfVenom reported the following error"
                                    + ["", "s"][bool(len(error) - 1)]
                                    + ":\n\n"
                                    + "\n".join(error)
                            )

                            else:
                                print("\nPayload successfully generated and saved to file '" + file_selection + ".'")

                        elif proceed_selection != "n":
                            print("\nInvalid selection.")

            elif menu_selection != "q":
                print ("\nInvalid selection.")

        else:

            if menu_selection in range(menu_number_of_options):
                menu_option = menu_options[menu_selection]
                menu_option_name = menu_option[0]

                if menu_option_name in submenus:

                    if type(submenus[menu_option_name]) is str:
                        print("\nGetting " + menu_option_name + "s from MsfVenom...")
                        submenus[menu_option_name] = eval(submenus[menu_option_name])

                    submenu_page = 1
                    submenu_selection = ""
                    submenu_options = submenus[menu_option_name]
                    submenu_displayed_options = submenu_options
                    submenu_number_of_options = len(submenu_displayed_options)
                    submenu_number_of_pages = max(1, int(ceil(submenu_number_of_options / 30)))
                    submenu_search_message = "No search string set. Displaying all available options."

                    while submenu_selection not in ["r", "q"]:

                        display_menu(
                            submenu_displayed_options,
                            submenu_page, 
                            menu_option_name.title() + " Subm",
                            "Page: [N]ext, [P]revious | Other: [S]earch, [C]lear, [R]eturn, [Q]uit.",
                            submenu_search_message
                        )

                        submenu_selection = input("\nSnakeskin (page " + str(submenu_page) + " of " + str(submenu_number_of_pages) + "): ").lower()

                        try:
                            submenu_selection = int(submenu_selection) - 1
                        except ValueError:

                            if submenu_selection == "n":

                                if submenu_page == submenu_number_of_pages:
                                    print("\nYou have reached the last page.")
                                else:
                                    submenu_page += 1

                            elif submenu_selection == "p":

                                if submenu_page == 1:
                                    print("\nYou have reached the first page.")
                                else:
                                    submenu_page -= 1

                            elif submenu_selection == "c":
                                submenu_option_name = menus[menu_current][menu_selection][1]

                                if submenu_option_name:
                                    print("\nValue of " + menu_current + " option " + menu_option_name + " cleared.")

                                    if menu_option_name == "payload":

                                        for menu in specific_menus:

                                            if menus[menu]:
                                                menus[menu] = []
                                                print("\nAll " + menu + " options have been removed due to their payload specificity.")
                                            else:
                                                print("\nPayload " + submenu_option_name + " has no " + menu + " options to remove.")

                                        if [menu for menu in menus["generic"] if menu[1] and menu[0] != "payload"]:
                                            clear_selection = ""

                                            while clear_selection not in ["y", "n"]:
                                                clear_selection = input("\nWould you like to clear the values of all remaining generic options? ").lower()

                                                if clear_selection == "y":
                                                    menus["generic"] = [[menu[0], "", menu[2], menu[3]] for menu in menus["generic"]]
                                                    print("\nValues of all remaining generic options cleared.")
                                                elif clear_selection != "n":
                                                    print("\nInvalid selection.")

                                    menus[menu_current][menu_selection][1] = ""
                                    submenu_selection = "r"
                                else:
                                    print("\nCannot clear the value of " + menu_current + " option " + menu_option_name + ". Value has not been set.")

                            elif submenu_selection == "s":
                                submenu_search_string = input("\nEnter a search string or press the Enter key to display all available options: ").lower()
                                submenu_matched_options = [option for option in submenu_options if submenu_search_string in option]
                                submenu_number_of_options = len(submenu_matched_options)

                                if submenu_number_of_options:

                                    if submenu_search_string:

                                        print(
                                            "\nFound "
                                            + str(submenu_number_of_options)
                                            + " options containing the search string '"
                                            + submenu_search_string
                                            + ".'"
                                        )

                                        submenu_search_message = (
                                            "Displayed options limited to those containing the search string '"
                                            + submenu_search_string
                                            + ".'"
                                        )

                                    else:
                                        submenu_search_message = " Displaying all available options."
                                        print("\nSearch string reset." + submenu_search_message)
                                        submenu_search_message = "No search string set." + submenu_search_message

                                    submenu_displayed_options = submenu_matched_options
                                    submenu_number_of_pages = max(1, int(ceil(submenu_number_of_options / 30)))
                                    submenu_page = 1
                                else:
                                    print("\nNo options matching the search string '" + submenu_search_string + "' found.")

                            elif submenu_selection not in ["r", "q"]:
                                print("\nInvalid selection.")

                        else:

                            if submenu_selection in range(submenu_number_of_options):
                                submenu_option_name = submenu_displayed_options[submenu_selection]
                                menus[menu_current][menu_selection][1] = submenu_option_name
                                print("\nValue of " + menu_current + " option " + menu_option_name + " set.")

                                if menu_option_name == "payload":
                                    print("\nGetting information for payload " + submenu_option_name + " from MsfVenom...")
                                    separator = "Name Current Setting Required Description"

                                    probe = "\n".join(
                                        [
                                            separator
                                            if " ".join(line.split()) == separator
                                            else line.strip()
                                            for line
                                            in getoutput('msfvenom --list-options -p ' + submenu_option_name).split("\n")
                                            if "ptions for payload/" not in line and line.replace(" ", "").replace("=", "")
                                        ]
                                    ).split(separator)

                                    header = probe.pop(0)

                                    sections = {
                                                name: section.split('Description:')[0].strip().split("\n")
                                                for (name, section)
                                                in zip(specific_menus, probe)
                                    }

                                    default_selection = ""

                                    while default_selection not in ["y", "n"]:

                                        default_selection = input(
                                            "\nWould you like to set the values of generic options architecture and platform to the default values for payload "
                                            + menu_option[1]
                                            + "? "
                                        ).lower()

                                        if default_selection == "y":
                                            default_architecture = header.split("Arch: ")[1].split("\n")[0]
                                            default_platform = header.split("Platform: ")[1].split("\n")[0]

                                            if default_architecture == "All" or len(default_architecture.split(", ")) > 1:
                                                print("\nCannot set the value of generic option architecture. Default value is ambiguous.")
                                            else:

                                                menus[menu_current] = [
                                                    [option[0]] + [default_architecture] + option[2:4]
                                                    if option[0] == "architecture"
                                                    else option
                                                    for option
                                                    in menus[menu_current]
                                                ] 

                                                print("\nValue of generic option architecture set to the default value for payload " + menu_option[1] + ".")

                                            if default_platform == "All" or len(default_platform.split(", ")) > 1:
                                                print("\nCannot set the value of generic option platform. Default value is ambiguous.")
                                            else:

                                                menus[menu_current] = [
                                                    [option[0]] + [default_platform] + option[2:4]
                                                    if option[0] == "platform"
                                                    else option
                                                    for option
                                                    in menus[menu_current]
                                                ] 

                                                print("\nValue of generic option platform set to the default value for payload " + menu_option[1] + ".")

                                        elif default_selection != "n":
                                            print("\nInvalid selection.")

                                    for specific_menu in specific_menus:
                                        menus[specific_menu] = []
                                        underline = sections[specific_menu].pop(0)

                                        columns = list(
                                            accumulate(
                                                list(
                                                    map(
                                                        lambda dashes, spaces: dashes + spaces,
                                                        [len(dash_sequence) for dash_sequence in underline.split()][:3],
                                                        [len(space_sequence) for space_sequence in sub("-+", "-", underline).split("-")[1:-1]]
                                                    )
                                                )
                                            )
                                        )

                                        for line in sections[specific_menu]:

                                            menus[specific_menu].append(
                                                [
                                                    line[:columns[0]].strip(),
                                                    line[columns[0]:columns[1]].strip(),
                                                    line[columns[1]:columns[2]].strip() == "yes",
                                                    line[columns[2]:].strip()
                                                ]
                                            )

                                submenu_selection = "r"
                            else:
                                print("\nInvalid selection.")

                    menu_selection = submenu_selection
                else:
                    print("\nDescription of " + menu_current + " option " + menu_option_name + " from MsfVenom: " + menu_option[3])
                    manual = input("\nEnter a value for " + menu_option_name + " or press the Enter key to clear the current value: ")
                    menus[menu_current][menu_selection][1] = manual
                    print("\nValue of " + menu_current + " option " + menu_option_name + " " + ["cleared", "set"][bool(len(manual))] + ".")

            else:
                print("\nInvalid selection.")

if __name__ == "__main__":
    main()
