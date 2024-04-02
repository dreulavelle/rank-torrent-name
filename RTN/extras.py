from javascript import require

from RTN.models import ParsedData

PTT = require("parse-torrent-title")


    # interface DefaultParserResult {
    #     title: string;
    #     date?: string;
    #     year?: number | string;
    #     resolution?: string;
    #     extended?: boolean;
    #     unrated?: boolean;
    #     proper?: boolean;
    #     repack?: boolean;
    #     convert?: boolean;
    #     hardcoded?: boolean;
    #     retail?: boolean;
    #     remastered?: boolean;
    #     complete?: boolean;
    #     region?: string;
    #     container?: string;
    #     extension?: string;
    #     source?: string;
    #     codec?: string;
    #     bitDepth?: string;
    #     hdr?: Array<string>;
    #     audio?: string;
    #     group?: string;
    #     volumes?: Array<number>;
    #     seasons?: Array<number>;
    #     season?: number;
    #     episodes?: Array<number>;
    #     episode?: number;
    #     languages?: string;
    #     dubbed?: boolean;
    # }

# class ParsedData(BaseModel):
#     """Parsed data model for a torrent title."""

#     raw_title: str
#     parsed_title: str
#     fetch: bool = False
#     is_4k: bool = False
#     is_multi_audio: bool = False
#     is_multi_subtitle: bool = False
#     is_complete: bool = False
#     year: int = 0
#     resolution: List[str] = []
#     quality: List[str] = []
#     season: List[int] = []
#     episode: List[int] = []
#     codec: List[str] = []
#     audio: List[str] = []
#     subtitles: List[str] = []
#     language: List[str] = []
#     bitDepth: List[int] = []
#     hdr: str = ""
#     proper: bool = False
#     repack: bool = False
#     remux: bool = False
#     upscaled: bool = False
#     remastered: bool = False
#     directorsCut: bool = False
#     extended: bool = False

def ptt_parse(title: str) -> ParsedData:
    # I need to convert the parsed data to a ParsedData object.
    # The parsed data is a javascript DefaultParserResult object.
    # That we need to map to a ParsedData object
    data = PTT.parse(title)
    return ParsedData(
        raw_title=title,
        parsed_title=data["title"],
        fetch=False,
        is_4k=False,
        is_multi_audio=data["audio"] and len(data["audio"]) > 1,
        is_multi_subtitle=False,
        is_complete=data["complete"],
        year=data["year"],
        resolution=[data["resolution"]],
        quality=[data["source"]],
        season=data["seasons"],
        episode=data["episodes"],
        codec=[data["codec"]],
        audio=data["audio"],
        subtitles=[],
        language=[data["languages"]],
        bitDepth=[int(data["bitDepth"])],
        hdr=data["hdr"],
        proper=data["proper"],
        repack=data["repack"],
        remux=data["remastered"],
        upscaled=False,
        remastered=data["remastered"],
        directorsCut=False,
        extended=data["extended"],
    )

