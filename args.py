import sys


# Exception raised when an invalid API call is attempted. (Invalid user input
# does not raise an exception; instead the application exits with an error
# message.)
class ArgParserError(Exception):
    pass


# Internal class for storing option data.
class Option:

    def __init__(self, opt_type, def_value):
        self.type = opt_type
        self.default = def_value
        self.values = []

    @property
    def value(self):
        if self.values:
            return self.values[-1]
        else:
            return self.default

    def try_append_value(self, str_val):
        try:
            self.values.append(self.type(str_val))
            return True
        except:
            return False


# Internal class for storing flag data.
class Flag:

    def __init__(self):
        self.count = 0


# Internal class for making a list of arguments available as a stream.
class ArgStream:

    def __init__(self, args):
        self.args = list(args)
        self.index = 0

    def next(self):
        self.index += 1
        return self.args[self.index - 1]

    def has_next(self):
        return self.index < len(self.args)


# An ArgParser instance is responsible for registering options and commands
# and parsing the input stream of raw arguments.
class ArgParser:

    # Specifying a string of help text activates an automatic --help flag.
    # Specifying a version string activates an automatic --version flag.
    def __init__(self, helptext=None, version=None):

        # Help text for the application or command.
        self.helptext = helptext

        # Application version.
        self.version = version

        # Stores registered Option instances indexed by name.
        self.options = {}

        # Stores registered Flag instances indexed by name.
        self.flags = {}

        # Stores positional arguments parsed from the input stream.
        self.args = []

        # Stores registered command parsers indexed by command name.
        self.commands = {}

        # Stores the command name, if a command was found.
        self.command_name = None

        # Stores the command parser, if a command was found.
        self.command_parser = None

        # Stores a command parser's callback function.
        self.callback = None

    # ------------------------------------------------------
    # Setup methods.
    # ------------------------------------------------------

    # Register a new flag.
    def flag(self, name):
        flag = Flag()
        for alias in name.split():
            self.flags[alias] = flag

    # Register a new option.
    def option(self, name, type=str, default=None):
        option = Option(type, default)
        for alias in name.split():
            self.options[alias] = option

    # Register a new command.
    def command(self, name, helptext=None, callback=None):
        cmd_parser = ArgParser(helptext)
        cmd_parser.callback = callback
        for alias in name.split():
            self.commands[alias] = cmd_parser
        return cmd_parser

    # ------------------------------------------------------
    # Inspection methods.
    # ------------------------------------------------------

    # Returns the number of times the specified flag or option has been found.
    def count(self, name):
        if flag := self.flags.get(name):
            return flag.count
        elif option := self.options.get(name):
            return len(option.values)
        else:
            raise ArgParserError(f"'{name}' is not a recognised flag or option name")

    # Returns true if the specified flag or option was found.
    def found(self, name):
        return self.count(name) > 0

    # Returns the value of the specified option.
    def value(self, name):
        if option := self.options.get(name):
            return option.value
        else:
            raise ArgParserError(f"'{name}' is not a recognised option name")

    # Returns the specified option's list of values.
    def values(self, name):
        if option := self.options.get(name):
            return option.values
        else:
            raise ArgParserError(f"'{name}' is not a recognised option name")

    # ------------------------------------------------------
    # Parsing machinery.
    # ------------------------------------------------------

    # Parse a list of string arguments.
    def parse(self, args=sys.argv[1:]):
        self._parse_stream(ArgStream(args))

    # Parse a stream of string arguments.
    def _parse_stream(self, stream):
        is_first_arg = True

        while stream.has_next():
            arg = stream.next()

            if arg == "--":
                while stream.has_next():
                    self.args.append(stream.next())

            elif arg.startswith("--"):
                if "=" in arg:
                    self._handle_equals_opt(arg[2:])
                else:
                    self._handle_long_opt(arg[2:], stream)

            elif arg.startswith("-"):
                if arg == '-' or arg[1].isdigit():
                    self.args.append(arg)
                elif "=" in arg:
                    self._handle_equals_opt(arg[1:])
                else:
                    self._handle_short_opt(arg[1:], stream)

            elif is_first_arg and arg in self.commands:
                self.command_name = arg
                self.command_parser = self.commands[arg]
                self.command_parser._parse_stream(stream)
                if self.command_parser.callback:
                    self.command_parser.callback(arg, self.command_parser)

            elif is_first_arg and arg == "help":
                if stream.has_next():
                    name = stream.next()
                    if name in self.commands:
                        self.commands[name].exit_help()
                    else:
                        self.exit_error(f"'{name}' is not a recognised command")
                else:
                    self.exit_error("missing argument for the help command")

            else:
                self.args.append(arg)

            is_first_arg = False

    # Parse an argument of the form --name=value or -n=value.
    def _handle_equals_opt(self, arg):
        name, value = arg.split("=", maxsplit=1)
        if option := self.options.get(name):
            if not option.try_append_value(value):
                self.exit_error(f"invalid option value '{value}'")
        else:
            self.exit_error(f"'{name}' is not a recognised option name")

    # Parse a long-form option, i.e. an option beginning with a double dash.
    def _handle_long_opt(self, arg, stream):
        if flag := self.flags.get(arg):
            flag.count += 1
        elif option := self.options.get(arg):
            if stream.has_next():
                value = stream.next()
                if not option.try_append_value(value):
                    self.exit_error(f"invalid option value '{value}'")
            else:
                self.exit_error(f"missing argument for --{arg} option")
        elif arg == "help" and self.helptext is not None:
            self.exit_help()
        elif arg == "version" and self.version is not None:
            self.exit_version()
        else:
            self.exit_error(f"--{arg} is not a recognised flag or option name")

    # Parse a short-form option, i.e. an option beginning with a single dash.
    def _handle_short_opt(self, arg, stream):
        for char in arg:
            if flag := self.flags.get(char):
                flag.count += 1
            elif option := self.options.get(char):
                if stream.has_next():
                    value = stream.next()
                    if not option.try_append_value(value):
                        self.exit_error(f"invalid option value '{value}'")
                else:
                    self.exit_error(f"missing argument for '{char}' option in -{arg}")
            elif char == "h" and self.helptext is not None:
                self.exit_help()
            elif char == "v" and self.version is not None:
                self.exit_version()
            else:
                self.exit_error(f"'{char}' in -{arg} is not a recognised flag or option name")

    # ------------------------------------------------------
    # Utility methods.
    # ------------------------------------------------------

    # Print the parser's state for debugging.
    def __str__(self):
        lines = []

        lines.append("Flags:")
        if self.flags:
            for name, flag in sorted(self.flags.items()):
                lines.append(f"  {name}: {flag.count}")
        else:
            lines.append("  [none]")

        lines.append("\nOptions:")
        if self.options:
            for name, opt in sorted(self.options.items()):
                lines.append(f"  {name}: ({opt.default}) {opt.values}")
        else:
            lines.append("  [none]")

        lines.append("\nArguments:")
        if self.args:
            for arg in self.args:
                lines.append(f"  {arg}")
        else:
            lines.append("  [none]")

        lines.append("\nCommand:")
        if self.command_name:
            lines.append(f"  {self.command_name}")
        else:
            lines.append("  [none]")

        return "\n".join(lines)

    # Print the parser's help text and exit.
    def exit_help(self):
        print(self.helptext.strip() if self.helptext else "")
        sys.exit()

    # Print the parser's version string and exit.
    def exit_version(self):
        print(self.version.strip() if self.version else "")
        sys.exit()

    # Print a message to stderr and exit with a non-zero status.
    def exit_error(self, msg):
        sys.exit(f"Error: {msg}.")

