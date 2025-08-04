"""
Main command-line entry point.
"""


import locale
import sys
from argparse import ArgumentParser, FileType
from io import BufferedReader, TextIOWrapper

from .codecs.info import MODULE_NAME, MODULE_VERSION, ENCODING_NAME, CODEC_NAME, SIGNATURE_SUFFIX


def encode(args) -> int:
    """
    Encode text to SCSU via the command line.

    :param args: Command-line arguments.
    :return: 0 if encoding is successful; 1 otherwise.
    """
    output_codec = CODEC_NAME + SIGNATURE_SUFFIX if args.signature else CODEC_NAME
    exit_code = 0

    try:
        input_bytes = bytes()
        assert type(args.filename) is TextIOWrapper or type(args.filename) is BufferedReader

        if type(args.filename) is TextIOWrapper:
            input_bytes = args.filename.buffer.read()
        elif type(args.filename) is BufferedReader:
            input_bytes = args.filename.read()

        input_str = input_bytes.decode(args.encoding)
        sys.stdout.buffer.write(input_str.encode(output_codec))
        sys.stdout.buffer.flush()
    except Exception as e:
        print(e, file=sys.stderr)
        exit_code = 1

    return exit_code


def decode(args) -> int:
    """
    Decode text from SCSU via the command line.

    :param args: Command-line arguments.
    :return: 0 if decoding is successful; 1 otherwise.
    """
    input_codec = CODEC_NAME + SIGNATURE_SUFFIX if args.signature else CODEC_NAME
    exit_code = 0

    try:
        input_bytes = bytes()
        assert type(args.filename) is TextIOWrapper or type(args.filename) is BufferedReader

        if type(args.filename) is TextIOWrapper:
            input_bytes = args.filename.buffer.read()
        elif type(args.filename) is BufferedReader:
            input_bytes = args.filename.read()

        input_str = input_bytes.decode(input_codec)
        sys.stdout.buffer.write(input_str.encode(args.encoding))
        sys.stdout.buffer.flush()
    except Exception as e:
        print(e, file=sys.stderr)
        exit_code = 1

    return exit_code


def main() -> int:
    """
    Command-line entry point.

    :return: 0 if all operations are successful; 1 otherwise.
    """
    encoding = locale.getpreferredencoding()

    parser = ArgumentParser(prog=MODULE_NAME, description=ENCODING_NAME)
    parser.add_argument("-V", "--version",
                        action="version",
                        version=f"{MODULE_NAME} v{MODULE_VERSION}")
    command = parser.add_subparsers(title="commands", required=True)

    encode_command = command.add_parser("encode", help=f"encode text as {CODEC_NAME}")
    encode_command.add_argument("-e", "--encoding",
                                metavar="ENCODING",
                                default=encoding,
                                help=f"input file encoding (default: {encoding!r})")
    encode_command.add_argument("-s", "--signature",
                                action="store_true",
                                help="insert byte order mark")
    encode_command.add_argument("filename",
                                nargs="?",
                                type=FileType("rb"),
                                default=sys.stdin,
                                help="text file to encode")
    encode_command.set_defaults(func=encode)

    decode_command = command.add_parser("decode", help=f"decode text as {CODEC_NAME}")
    decode_command.add_argument("-e", "--encoding",
                                metavar="ENCODING",
                                default=encoding,
                                help=f"output file encoding (default: {encoding!r})")
    decode_command.add_argument("-s", "--signature",
                                action="store_true",
                                help="remove byte order mark")
    decode_command.add_argument("filename",
                                nargs="?",
                                type=FileType("rb"),
                                default=sys.stdin,
                                help="text file to decode")
    decode_command.set_defaults(func=decode)

    arguments = parser.parse_args()
    return arguments.func(arguments)


if __name__ == "__main__":
    exit(main())
