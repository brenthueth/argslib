#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# This sample application parses and prints its own command line arguments.
# ------------------------------------------------------------------------------

import args

def main():

    # The ArgParser class is the library's public interface.
    parser = args.ArgParser()

    # Specifying a helptext string activates an automatic --help/-h flag.
    parser.helptext = "Usage: example..."

    # Specifying a version string activates an automatic --version/-v flag.
    parser.version = "1.0"

    # Register a flag, --foo, with a single-character shortcut, -f.
    parser.flag("foo f")

    # Register a string-valued option, --bar <arg>, with a single-character
    # shortcut, -b <arg>.
    parser.option("bar b")

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
