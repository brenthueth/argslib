#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# This sample application parses and prints its own command line arguments.
# ------------------------------------------------------------------------------

import args

def main():

    # Instantiate an ArgParser instance. Supplying help text activates an
    # automatic --help flag, supplying a version string activates an automatic
    # --version flag.
    parser = args.ArgParser("Usage: example...", "1.0")

    # Register a flag, --foo.
    parser.flag("foo")

    # Register a string-valued option, --string <arg>, with a single-character
    # alias, -s <arg>.
    parser.option("string s")

    # Register an integer-valued option, --int <arg>, with a single-character
    # alias, -i <arg>.
    parser.option("int i", type=int)

    # Register a floating-point-valued option, --float <arg>, with a single-
    # character alias, -f <arg>.
    parser.option("float f", type=float)

    # Register a command 'boo'.
    cmd_parser = parser.command("boo", "Usage: example boo...", cmd_callback)

    # Registering a command returns a new ArgParser instance which can support
    # its own flags and options.
    cmd_parser.flag("foo f")
    cmd_parser.option("bar b")

    # Parse the command line arguments.
    parser.parse()
    print(parser)

def cmd_callback(cmd_name, cmd_parser):
    print("------------ boo! ------------")
    print(cmd_parser)
    print("------------------------------\n")

if __name__ == "__main__":
    main()
