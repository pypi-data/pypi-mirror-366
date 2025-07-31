###
# #%L
# aiSSEMBLE::Universal Config::Loader
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###

TITLE_DIVIDER = "|||"


def print_next_step(*args):
    """util function to print the next step"""
    header = (
        "\n****************************************************************************************"
        + "\n Next Steps:"
        + "\n****************************************************************************************"
    )
    counter = 0
    instructions = ""
    for instruction in args:
        counter += 1
        title = instruction.split(TITLE_DIVIDER, 1)[0]
        content = instruction.split(TITLE_DIVIDER, 1)[1]
        instructions = (
            instructions
            + f"\n {counter}: {title}"
            + "\n----------------------------------------------------------------------------------------"
            + f"\n {content}"
            + "\n\n----------------------------------------------------------------------------------------"
        )

    print(header + instructions)
