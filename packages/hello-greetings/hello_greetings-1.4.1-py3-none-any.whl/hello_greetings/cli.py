#!/usr/bin/env python3
"""
A simple command line tool that greets the user.
"""

import argparse
import sys


def main() -> None:
    """Main function to handle command line arguments and greet the user."""
    parser = argparse.ArgumentParser(
        description="A simple greeting tool", epilog='Example: hello-greetings "World"'
    )

    parser.add_argument(
        "name",
        nargs="?",  # Makes the argument optional
        help="The name or thing to greet",
        default=None,
    )

    parser.add_argument(
        "-v", "--version", action="version", version="hello-greetings 1.3.0"
    )

    args = parser.parse_args()

    # If no name provided, ask for input
    if args.name is None:
        try:
            name = input("Enter something: ")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
    else:
        name = args.name

    # Print the greeting
    print(f"hello {name}")


if __name__ == "__main__":
    main()
