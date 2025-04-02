import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Parse Filenames and Rank them according to your preferences!")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse a filename or directly parse a string')
    parse_parser.add_argument('filename', nargs='?', type=str, help='The filename to parse or a string to directly parse')

    # FFprobe command
    ffprobe_parser = subparsers.add_parser('ffprobe', help='Parse a video file')
    ffprobe_parser.add_argument('filename', nargs='?', type=str, help='The video file to parse')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == 'parse':
        from RTN import parse
        if args.filename:
            result = parse(args.filename)
            print(result.model_dump_json(indent=4, exclude_none=True, exclude_defaults=True))

    if args.command == 'ffprobe':
        from RTN import parse_media_file
        if args.filename:
            try:
                result = parse_media_file(args.filename)
                print(result.model_dump_json(indent=4, exclude_none=True, exclude_defaults=True))
            except Exception as e:
                print(f"Error Parsing File: {e}")


if __name__ == "__main__":
    main()
