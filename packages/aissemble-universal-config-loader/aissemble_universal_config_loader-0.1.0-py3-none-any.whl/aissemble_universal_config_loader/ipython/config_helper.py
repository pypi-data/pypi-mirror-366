###
# #%L
# aiSSEMBLE::Universal Config::Loader
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
)
import os
from ..util.utils import print_next_step, TITLE_DIVIDER

CONFIG_DIR = "/configurations/base/"


@magics_class
class ConfigHelper(Magics):
    """aiSSEMBLE-universal-config config helper class."""

    @line_magic
    def extract_vars_to_property_file(self, parameter_s):
        """
        Extract vars (str type and int type only) into a .properties file. File will be generated if not exists
        If there are no arguments are given, by default, it will be set as the configuration.properties if it's not set and
        the relative path for the property file from `current` directory. By default, it will be set to `../configurations/base` directory
                                    ├── current/
                                    │     └── foo.ipnb
                                    ├── configurations
                                    │     └── base
                                    │       └── configuration.properties
                                    └── ...
                                    Note: `UsageError` will be raised if there is no parent directory for the `current` directory

        If arguments are given, the variables will be writen to the given file within the given directory.

        Examples
        --------
        Define file name and relative file path with extract_vars_to_property_file:

          %extract_vars_to_property_file my-custom.properties

          %extract_vars_to_property_file my-custom.properties ../my/custom/folder

        """
        arg_list = parameter_s.split()
        if arg_list:
            if len(arg_list) >= 2:
                file_name = arg_list[0]
                relative_file_path = arg_list[1]
            elif len(arg_list) == 1:
                file_name = arg_list[0]
        else:
            file_name = "configuration.properties"
            relative_file_path = f"..{CONFIG_DIR}"

        os.environ["KRAUSENING_BASE"] = os.path.abspath(relative_file_path)
        try:
            # create config directory if not exists
            os.makedirs(relative_file_path, exist_ok=True)

            file_name = f"{relative_file_path}{file_name}"

            user_ns = self.shell.user_ns
            user_ns_hidden = self.shell.user_ns_hidden
            nonmatching = object()  # This can never be in user_ns
            varnames = [
                i
                for i in user_ns
                if not i.startswith("_")
                and (user_ns[i] is not user_ns_hidden.get(i, nonmatching))
            ]

            # only read the str or int variables
            typeset = set(["str", "int"])
            varnames = [i for i in varnames if type(user_ns[i]).__name__ in typeset]
            # sort the var name list
            varnames.sort()

            if not varnames:
                print("No variables match the `str` or the `int` type.")
                return

            varlist = [user_ns[n] for n in varnames]
            properties = []
            for vname, var in zip(varnames, varlist):
                properties.append(f"{vname}={var}")

            self._write_to(file_name=file_name, content=properties)

        except FileExistsError as fe:
            print(
                f"Error creating the configuration directory at {relative_file_path}. {fe}"
            )
        except OSError as e:
            print(
                f"Error creating the configuration directory, you can set the relative_file_path for the configuration file. {e}"
            )

    def _read_from(self, file_name: str) -> []:
        # Read the file content line by line into a list
        file_lines = []
        with open(file_name, "r") as file:
            file_lines = file.readlines()

        return file_lines

    def _write_to(self, file_name: str, content: []):
        try:
            file_name = os.path.expanduser(file_name)
            file_exists = os.path.isfile(file_name)
            final_content = []
            mode = "w"
            if not file_exists:
                final_content = content
            else:
                file_lines = self._read_from(file_name)
                mode = "a"
                for line in content:
                    if (line.strip() + "\n") not in file_lines:
                        final_content.append(line)

            with open(file_name, mode) as f:
                for line in final_content:
                    f.write(line + "\n")

            print_next_step(
                f"{self._load_property_instruction(config_path=os.getenv('KRAUSENING_BASE'))}",
                f"Optional{TITLE_DIVIDER}The variables have been extracted to {os.path.abspath(file_name)}.\n You can remove the following variables from your notebook and load them via the ConfigLoader:\n {final_content}",
            )
        except Exception as e:
            print(f"Failed to write to configuration file: {e}")

    def _load_property_instruction(self, config_path: str) -> str:
        return (
            f"Required{TITLE_DIVIDER}To load property values as global variables, add the below code snippets to a new cell and run the cell:"
            + "\n\n```"
            + "\n# import the ConfigLoader module"
            + "\nfrom aissemble_universal_config_loader.config_loader import ConfigLoader"
            + "\n"
            + "\n# set configuration file directory, this is for bootstrapping the library"
            + f"\nos.environ['KRAUSENING_BASE'] = '{config_path}'"
            + "\n"
            + "\n# load property values as global variables"
            + "\nConfigLoader().load_as_global()"
            + "\n\n```"
            + "\n Note: Use `ConfigLoader().load_as_env()` to load property values as environment variable."
            + "\n"
        )


# In order to actually use these magics, you must register them with a
# running IPython.
def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    ipython.register_magics(ConfigHelper)
