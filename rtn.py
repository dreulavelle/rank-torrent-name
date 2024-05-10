import argparse
import sys


def setup_parser():
    # Create the top-level parser
    parser = argparse.ArgumentParser(prog="RTN Tool", description="Process and analyze torrent metadata.")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Subparser for the "parse" command
    parse_parser = subparsers.add_parser("parse", aliases=["-p", "-rtn"], help="Parse a single torrent title using RTN")
    parse_parser.add_argument("title", type=str, help="Torrent title to parse")

    # Subparser for "PTN" parser
    ptn_parser = subparsers.add_parser("ptn", help="Parse a single torrent title using PTN")
    ptn_parser.add_argument("title", type=str, help="Torrent title to parse")

    # Subparser for "PTT" parser (parsett)
    ptt_parser = subparsers.add_parser("ptt", aliases=["-ptt", "parsett"], help="Parse a single torrent title using PTT")
    ptt_parser.add_argument("title", type=str, help="Torrent title to parse")

    # Subparser for "title_match"
    match_parser = subparsers.add_parser("match", help="Compare two torrent titles for similarity")
    match_parser.add_argument("title1", type=str, help="First torrent title to compare")
    match_parser.add_argument("title2", type=str, help="Second torrent title to compare")
    match_parser.add_argument("--threshold", type=float, default=0.9, help="Threshold for similarity (default 0.9)")

    # Subparser for "extract_episodes"
    episodes_parser = subparsers.add_parser("episodes", help="Extract episodes from a title")
    episodes_parser.add_argument("title", type=str, help="Torrent title from which to extract episodes")

    # Subparser for "extract_seasons"
    seasons_parser = subparsers.add_parser("seasons", help="Extract seasons from a title")
    seasons_parser.add_argument("title", type=str, help="Torrent title from which to extract seasons")

    # Subparser for "parse_extras"
    extras_parser = subparsers.add_parser("extras", help="Parse extra information from a title")
    extras_parser.add_argument("title", type=str, help="Torrent title to parse for extra information")

    return parser

def main():
    parser = setup_parser()
    # Manually handle the first argument for aliases
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        if first_arg in ["-p", "-rtn"]:
            sys.argv[1] = "parse"
        elif first_arg in ["-m"]:
            sys.argv[1] = "match"
        elif first_arg in ["-e"]:
            sys.argv[1] = "episodes"
        elif first_arg in ["-s"]:
            sys.argv[1] = "seasons"
        elif first_arg in ["-x"]:
            sys.argv[1] = "extras"
        elif first_arg in ["-ptn"]:
            sys.argv[1] = "ptn"
        elif first_arg in ["-ptt", "parsett"]:
            sys.argv[1] = "ptt"
            
    args = parser.parse_args()

    # Routing commands using match statement
    match args.command:
        case "parse":
            from RTN.parser import parse
            result = parse(args.title)
            print(result)
        case "match":
            from RTN.parser import title_match
            is_match = title_match(args.title1, args.title2, args.threshold)
            print(f"Titles match: {is_match}")
        case "episodes":
            from RTN.patterns import extract_episodes
            result = extract_episodes(args.title)
            print(result)
        case "seasons":
            from RTN.patterns import extract_seasons
            result = extract_seasons(args.title)
            print(result)
        case "extras":
            from RTN.patterns import parse_extras
            result = parse_extras(args.title)
            print(result)
        case "ptn":
            from PTN import parse
            result = parse(args.title, coherent_types=True)
            print(result)
        case "ptt":
            from RTN import parsett
            result = parsett(args.title)
            print(result)
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()
