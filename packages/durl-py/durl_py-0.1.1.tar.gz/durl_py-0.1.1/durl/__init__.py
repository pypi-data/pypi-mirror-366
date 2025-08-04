import base64
import enum
import logging
import pathlib
import re
import types
import typing
import urllib.parse

import pydantic
from rich.pretty import pretty_repr

__version__ = pathlib.Path(__file__).parent.joinpath("VERSION").read_text().strip()

logger = logging.getLogger(__name__)


class MIMEType(enum.StrEnum):
    AAC_AUDIO = "audio/aac"  # AAC audio
    ABIWORD_DOCUMENT = "application/x-abiword"  # AbiWord document
    ANIMATED_PORTABLE_NETWORK_GRAPHICS_APNG_IMAGE = (
        "image/apng"  # Animated Portable Network Graphics (APNG) image
    )
    ARCHIVE_DOCUMENT_MULTIPLE_FILES_EMBEDDED = (
        "application/x-freearc"  # Archive document (multiple files embedded)
    )
    AVIF_IMAGE = "image/avif"  # AVIF image
    AVI_AUDIO_VIDEO_INTERLEAVE = "video/x-msvideo"  # AVI: Audio Video Interleave
    AMAZON_KINDLE_EBOOK_FORMAT = (
        "application/vnd.amazon.ebook"  # Amazon Kindle eBook format
    )
    ANY_KIND_OF_BINARY_DATA = "application/octet-stream"  # Any kind of binary data
    WINDOWS_OS_2_BITMAP_GRAPHICS = "image/bmp"  # Windows OS/2 Bitmap Graphics
    BZIP_ARCHIVE = "application/x-bzip"  # BZip archive
    BZIP2_ARCHIVE = "application/x-bzip2"  # BZip2 archive
    CD_AUDIO = "application/x-cdf"  # CD audio
    C_SHELL_SCRIPT = "application/x-csh"  # C-Shell script
    CASCADING_STYLE_SHEETS_CSS = "text/css"  # Cascading Style Sheets (CSS)
    COMMA_SEPARATED_VALUES_CSV = "text/csv"  # Comma-separated values (CSV)
    MICROSOFT_WORD = "application/msword"  # Microsoft Word
    MICROSOFT_WORD_OPENXML = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # Microsoft Word (OpenXML)  # noqa: E501
    MS_EMBEDDED_OPENTYPE_FONTS = (
        "application/vnd.ms-fontobject"  # MS Embedded OpenType fonts
    )
    ELECTRONIC_PUBLICATION_EPUB = (
        "application/epub+zip"  # Electronic publication (EPUB)
    )
    GZIP_COMPRESSED_ARCHIVE = "application/gzip"  # GZip Compressed Archive
    GRAPHICS_INTERCHANGE_FORMAT_GIF = "image/gif"  # Graphics Interchange Format (GIF)
    HYPERTEXT_MARKUP_LANGUAGE_HTML = "text/html"  # HyperText Markup Language (HTML)
    ICON_FORMAT = "image/vnd.microsoft.icon"  # Icon format
    ICALENDAR_FORMAT = "text/calendar"  # iCalendar format
    JAVA_ARCHIVE_JAR = "application/java-archive"  # Java Archive (JAR)
    JPEG_IMAGES = "image/jpeg"  # JPEG images
    JAVASCRIPT = "text/javascript"  # JavaScript
    JSON_FORMAT = "application/json"  # JSON format
    JSON_LD_FORMAT = "application/ld+json"  # JSON-LD format
    MARKDOWN = "text/markdown"  # Markdown
    MUSICAL_INSTRUMENT_DIGITAL_INTERFACE_MIDI = (
        "audio/midi"  # Musical Instrument Digital Interface (MIDI)
    )
    JAVASCRIPT_MODULE = "text/javascript"  # JavaScript module
    MP3_AUDIO = "audio/mpeg"  # MP3 audio
    MP4_VIDEO = "video/mp4"  # MP4 video
    MPEG_VIDEO = "video/mpeg"  # MPEG Video
    APPLE_INSTALLER_PACKAGE = (
        "application/vnd.apple.installer+xml"  # Apple Installer Package
    )
    OPENDOCUMENT_PRESENTATION_DOCUMENT = "application/vnd.oasis.opendocument.presentation"  # OpenDocument presentation document  # noqa: E501
    OPENDOCUMENT_SPREADSHEET_DOCUMENT = "application/vnd.oasis.opendocument.spreadsheet"  # OpenDocument spreadsheet document  # noqa: E501
    OPENDOCUMENT_TEXT_DOCUMENT = (
        "application/vnd.oasis.opendocument.text"  # OpenDocument text document
    )
    OGG_AUDIO = "audio/ogg"  # Ogg audio
    OGG_VIDEO = "video/ogg"  # Ogg video
    OGG = "application/ogg"  # Ogg
    OPUS_AUDIO_IN_OGG_CONTAINER = "audio/ogg"  # Opus audio in Ogg container
    OPENTYPE_FONT = "font/otf"  # OpenType font
    PORTABLE_NETWORK_GRAPHICS = "image/png"  # Portable Network Graphics
    ADOBE_PORTABLE_DOCUMENT_FORMAT_PDF = (
        "application/pdf"  # Adobe Portable Document Format (PDF)
    )
    HYPERTEXT_PREPROCESSOR_PERSONAL_HOME_PAGE = (
        "application/x-httpd-php"  # Hypertext Preprocessor (Personal Home Page)
    )
    MICROSOFT_POWERPOINT = "application/vnd.ms-powerpoint"  # Microsoft PowerPoint
    MICROSOFT_POWERPOINT_OPENXML = "application/vnd.openxmlformats-officedocument.presentationml.presentation"  # Microsoft PowerPoint (OpenXML)  # noqa: E501
    RAR_ARCHIVE = "application/vnd.rar"  # RAR archive
    RICH_TEXT_FORMAT_RTF = "application/rtf"  # Rich Text Format (RTF)
    BOURNE_SHELL_SCRIPT = "application/x-sh"  # Bourne shell script
    SCALABLE_VECTOR_GRAPHICS_SVG = "image/svg+xml"  # Scalable Vector Graphics (SVG)
    TAPE_ARCHIVE_TAR = "application/x-tar"  # Tape Archive (TAR)
    TAGGED_IMAGE_FILE_FORMAT_TIFF = "image/tiff"  # Tagged Image File Format (TIFF)
    MPEG_TRANSPORT_STREAM = "video/mp2t"  # MPEG transport stream
    TRUETYPE_FONT = "font/ttf"  # TrueType Font
    TEXT_GENERALLY_ASCII_OR_ISO_8859_N = (
        "text/plain"  # Text, (generally ASCII or ISO 8859-n)
    )
    MICROSOFT_VISIO = "application/vnd.visio"  # Microsoft Visio
    WAVEFORM_AUDIO_FORMAT = "audio/wav"  # Waveform Audio Format
    WEBM_AUDIO = "audio/webm"  # WEBM audio
    WEBM_VIDEO = "video/webm"  # WEBM video
    WEB_APPLICATION_MANIFEST = "application/manifest+json"  # Web application manifest
    WEBP_IMAGE = "image/webp"  # WEBP image
    WEB_OPEN_FONT_FORMAT_WOFF = "font/woff"  # Web Open Font Format (WOFF)
    WEB_OPEN_FONT_FORMAT_WOFF_2 = "font/woff2"  # Web Open Font Format (WOFF)
    XHTML = "application/xhtml+xml"  # XHTML
    MICROSOFT_EXCEL = "application/vnd.ms-excel"  # Microsoft Excel
    MICROSOFT_EXCEL_OPENXML = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # Microsoft Excel (OpenXML)  # noqa: E501
    XML = "application/xml"  # XML
    XUL = "application/vnd.mozilla.xul+xml"  # XUL
    ZIP_ARCHIVE = "application/zip"  # ZIP archive
    MIME_3GPP_AUDIO_VIDEO_CONTAINER = "video/3gpp"  # 3GPP audio/video container
    MIME_3G2_AUDIO_VIDEO_CONTAINER = "video/3gpp2"  # 3GPP2 audio/video container
    MIME_7_ZIP_ARCHIVE = "application/x-7z-compressed"  # 7-zip archive


ExtensionMIMEType = types.MappingProxyType(
    {
        "3g2": MIMEType.MIME_3G2_AUDIO_VIDEO_CONTAINER,
        "3gp": MIMEType.MIME_3GPP_AUDIO_VIDEO_CONTAINER,
        "7z": MIMEType.MIME_7_ZIP_ARCHIVE,
        "aac": MIMEType.AAC_AUDIO,
        "abw": MIMEType.ABIWORD_DOCUMENT,
        "apng": MIMEType.ANIMATED_PORTABLE_NETWORK_GRAPHICS_APNG_IMAGE,
        "arc": MIMEType.ARCHIVE_DOCUMENT_MULTIPLE_FILES_EMBEDDED,
        "avif": MIMEType.AVIF_IMAGE,
        "avi": MIMEType.AVI_AUDIO_VIDEO_INTERLEAVE,
        "azw": MIMEType.AMAZON_KINDLE_EBOOK_FORMAT,
        "bin": MIMEType.ANY_KIND_OF_BINARY_DATA,
        "bmp": MIMEType.WINDOWS_OS_2_BITMAP_GRAPHICS,
        "bz": MIMEType.BZIP_ARCHIVE,
        "bz2": MIMEType.BZIP2_ARCHIVE,
        "cda": MIMEType.CD_AUDIO,
        "csh": MIMEType.C_SHELL_SCRIPT,
        "css": MIMEType.CASCADING_STYLE_SHEETS_CSS,
        "csv": MIMEType.COMMA_SEPARATED_VALUES_CSV,
        "doc": MIMEType.MICROSOFT_WORD,
        "docx": MIMEType.MICROSOFT_WORD_OPENXML,
        "eot": MIMEType.MS_EMBEDDED_OPENTYPE_FONTS,
        "epub": MIMEType.ELECTRONIC_PUBLICATION_EPUB,
        "gz": MIMEType.GZIP_COMPRESSED_ARCHIVE,
        "gif": MIMEType.GRAPHICS_INTERCHANGE_FORMAT_GIF,
        "htm": MIMEType.HYPERTEXT_MARKUP_LANGUAGE_HTML,
        "html": MIMEType.HYPERTEXT_MARKUP_LANGUAGE_HTML,
        "ico": MIMEType.ICON_FORMAT,
        "ics": MIMEType.ICALENDAR_FORMAT,
        "jar": MIMEType.JAVA_ARCHIVE_JAR,
        "jpeg": MIMEType.JPEG_IMAGES,
        "jpg": MIMEType.JPEG_IMAGES,
        "js": MIMEType.JAVASCRIPT,
        "json": MIMEType.JSON_FORMAT,
        "jsonld": MIMEType.JSON_LD_FORMAT,
        "md": MIMEType.MARKDOWN,
        "mid": MIMEType.MUSICAL_INSTRUMENT_DIGITAL_INTERFACE_MIDI,
        "midi": MIMEType.MUSICAL_INSTRUMENT_DIGITAL_INTERFACE_MIDI,
        "mjs": MIMEType.JAVASCRIPT_MODULE,
        "mp3": MIMEType.MP3_AUDIO,
        "mp4": MIMEType.MP4_VIDEO,
        "mpeg": MIMEType.MPEG_VIDEO,
        "mpkg": MIMEType.APPLE_INSTALLER_PACKAGE,
        "odp": MIMEType.OPENDOCUMENT_PRESENTATION_DOCUMENT,
        "ods": MIMEType.OPENDOCUMENT_SPREADSHEET_DOCUMENT,
        "odt": MIMEType.OPENDOCUMENT_TEXT_DOCUMENT,
        "oga": MIMEType.OGG_AUDIO,
        "ogv": MIMEType.OGG_VIDEO,
        "ogx": MIMEType.OGG,
        "opus": MIMEType.OPUS_AUDIO_IN_OGG_CONTAINER,
        "otf": MIMEType.OPENTYPE_FONT,
        "png": MIMEType.PORTABLE_NETWORK_GRAPHICS,
        "pdf": MIMEType.ADOBE_PORTABLE_DOCUMENT_FORMAT_PDF,
        "php": MIMEType.HYPERTEXT_PREPROCESSOR_PERSONAL_HOME_PAGE,
        "ppt": MIMEType.MICROSOFT_POWERPOINT,
        "pptx": MIMEType.MICROSOFT_POWERPOINT_OPENXML,
        "rar": MIMEType.RAR_ARCHIVE,
        "rtf": MIMEType.RICH_TEXT_FORMAT_RTF,
        "sh": MIMEType.BOURNE_SHELL_SCRIPT,
        "svg": MIMEType.SCALABLE_VECTOR_GRAPHICS_SVG,
        "tar": MIMEType.TAPE_ARCHIVE_TAR,
        "tif": MIMEType.TAGGED_IMAGE_FILE_FORMAT_TIFF,
        "tiff": MIMEType.TAGGED_IMAGE_FILE_FORMAT_TIFF,
        "ts": MIMEType.MPEG_TRANSPORT_STREAM,
        "ttf": MIMEType.TRUETYPE_FONT,
        "txt": MIMEType.TEXT_GENERALLY_ASCII_OR_ISO_8859_N,
        "vsd": MIMEType.MICROSOFT_VISIO,
        "wav": MIMEType.WAVEFORM_AUDIO_FORMAT,
        "weba": MIMEType.WEBM_AUDIO,
        "webm": MIMEType.WEBM_VIDEO,
        "webmanifest": MIMEType.WEB_APPLICATION_MANIFEST,
        "webp": MIMEType.WEBP_IMAGE,
        "woff": MIMEType.WEB_OPEN_FONT_FORMAT_WOFF,
        "woff2": MIMEType.WEB_OPEN_FONT_FORMAT_WOFF_2,
        "xhtml": MIMEType.XHTML,
        "xls": MIMEType.MICROSOFT_EXCEL,
        "xlsx": MIMEType.MICROSOFT_EXCEL_OPENXML,
        "xml": MIMEType.XML,
        "xul": MIMEType.XUL,
        "zip": MIMEType.ZIP_ARCHIVE,
    }
)

MIME_TYPES: typing.TypeAlias = MIMEType
TEXT_MIME_TYPES: typing.TypeAlias = typing.Literal[
    MIMEType.CASCADING_STYLE_SHEETS_CSS,
    MIMEType.COMMA_SEPARATED_VALUES_CSV,
    MIMEType.HYPERTEXT_MARKUP_LANGUAGE_HTML,
    MIMEType.ICALENDAR_FORMAT,
    MIMEType.JAVASCRIPT,
    MIMEType.JSON_FORMAT,
    MIMEType.JSON_LD_FORMAT,
    MIMEType.MARKDOWN,
    MIMEType.JAVASCRIPT_MODULE,
    MIMEType.TEXT_GENERALLY_ASCII_OR_ISO_8859_N,
]
AUDIO_MIME_TYPES: typing.TypeAlias = typing.Literal[
    MIMEType.AAC_AUDIO,
    MIMEType.MUSICAL_INSTRUMENT_DIGITAL_INTERFACE_MIDI,
    MIMEType.MP3_AUDIO,
    MIMEType.OGG_AUDIO,
    MIMEType.OPUS_AUDIO_IN_OGG_CONTAINER,
    MIMEType.WAVEFORM_AUDIO_FORMAT,
    MIMEType.WEBM_AUDIO,
]
IMAGE_MIME_TYPES: typing.TypeAlias = typing.Literal[
    MIMEType.ANIMATED_PORTABLE_NETWORK_GRAPHICS_APNG_IMAGE,
    MIMEType.AVIF_IMAGE,
    MIMEType.WINDOWS_OS_2_BITMAP_GRAPHICS,
    MIMEType.GRAPHICS_INTERCHANGE_FORMAT_GIF,
    MIMEType.ICON_FORMAT,
    MIMEType.JPEG_IMAGES,
    MIMEType.PORTABLE_NETWORK_GRAPHICS,
    MIMEType.SCALABLE_VECTOR_GRAPHICS_SVG,
    MIMEType.TAGGED_IMAGE_FILE_FORMAT_TIFF,
    MIMEType.WEBP_IMAGE,
]


DATA_URL_PATTERN = re.compile(
    r"""
    ^data:
    (?P<media_type>[^;,]*)
    (?:  # whole parameter section
        ;
        (?P<params>
            [^;,=]+=[^;,]*  # first attr=value
            (?:;[^;,=]+=[^;,]*)*  # 0-n more ;attr=value
        )
    )?  # entire param list is optional
    (?P<base64>;base64)?  # optional ;base64 flag
    ,
    (?P<payload>.*)  # everything after the first comma
    \Z
    """,
    re.I | re.S | re.VERBOSE,
)


def is_text_content(mime_type: MIME_TYPES | str) -> bool:
    mime_type = MIMEType(mime_type)
    return mime_type in (TEXT_MIME_TYPES.__args__)


def is_audio_content(mime_type: MIME_TYPES | str) -> bool:
    mime_type = MIMEType(mime_type)
    return mime_type in (AUDIO_MIME_TYPES.__args__)


def is_image_content(mime_type: MIME_TYPES | str) -> bool:
    mime_type = MIMEType(mime_type)
    return mime_type in (IMAGE_MIME_TYPES.__args__)


class DataURL(pydantic.BaseModel):
    """Represents a Data URL (RFC 2397).

    A Data URL is a URI scheme that provides a way to include data in-line in
    web pages as if they were external resources.
    """

    mime_type: MIME_TYPES
    parameters: str | None = pydantic.Field(
        default=None,
        description="Parameters are key-value pairs separated by semicolons",
    )
    encoded: typing.Literal["base64"] = pydantic.Field(
        default="base64",
        description="Only support base64 encoding in any instance",
    )
    data: str = pydantic.Field(
        description="The data payload, which must be a base64-encoded string"
    )

    @pydantic.model_validator(mode="after")
    def validate_parameters(self) -> typing.Self:
        if self.parameters is None:
            return self

        if self.parameters.startswith(";"):
            self.parameters = self.parameters.lstrip(";")

        parts = self.parameters.split(";")
        for part in parts:
            if not part:
                continue
            if "=" not in part:
                raise ValueError(f"Invalid parameter format for '{part}': missing '=' ")
            key, value = part.split("=", 1)
            if not key.strip() or not value.strip():
                raise ValueError(
                    f"Invalid parameter format for '{part}': empty key or value"
                )
        return self

    @pydantic.model_serializer
    def serialize_model(self) -> str:
        return self.url

    @classmethod
    def is_data_url(cls, url: str) -> bool:
        """Checks if the given string is a valid data URL."""
        return bool(DATA_URL_PATTERN.match(url))

    @classmethod
    def from_url(cls, url: str) -> "DataURL":
        """Creates a DataURL object from a data URL string."""
        mime_type, parameters, encoded, data = cls.__parse_url(url)
        return cls(
            mime_type=mime_type, parameters=parameters, encoded=encoded, data=data
        )

    @classmethod
    def from_data(
        cls,
        mime_type: MIME_TYPES,
        raw_data: str | bytes,
        *,
        parameters: str | None = None,
    ) -> "DataURL":
        """Creates a DataURL object from raw data and a MIME type."""
        if isinstance(raw_data, str):
            data = base64.b64encode(raw_data.encode("utf-8")).decode("utf-8")
        else:
            data = base64.b64encode(raw_data).decode("utf-8")

        return cls(mime_type=mime_type, parameters=parameters, data=data)

    @property
    def url(self) -> str:
        """Returns the full data URL string representation."""
        STRING_PATTERN = (
            "data:{media_type}{might_semicolon_parameters}{semicolon_encoded},{data}"
        )

        return STRING_PATTERN.format(
            media_type=self.mime_type,
            might_semicolon_parameters=f";{self.parameters}" if self.parameters else "",
            semicolon_encoded=f";{self.encoded}" if self.encoded else "",
            data=self.data,
        )

    @property
    def url_truncated(self) -> str:
        """Returns a truncated version of the data URL string."""
        return pretty_repr(self.url, max_string=127).strip("'\"")

    @property
    def data_decoded(self) -> str | bytes:
        """Decodes and returns the base64-encoded data payload as a string."""
        b64_decoded = base64.b64decode(self.data)
        try:
            return b64_decoded.decode("utf-8")
        except UnicodeDecodeError:
            return b64_decoded

    @property
    def is_data_decoded_str(self) -> bool:
        return isinstance(self.data_decoded, str)

    @property
    def is_text_content(self) -> bool:
        return is_text_content(self.mime_type)

    @property
    def is_audio_content(self) -> bool:
        return is_audio_content(self.mime_type)

    @property
    def is_image_content(self) -> bool:
        return is_image_content(self.mime_type)

    @classmethod
    def __parse_url(
        cls,
        url: str,
    ) -> typing.Tuple[
        MIME_TYPES,
        str | None,
        typing.Literal["base64"],
        str,
    ]:
        """Parses a data URL string into its constituent parts."""
        m = DATA_URL_PATTERN.match(url)
        if not m:
            raise ValueError("Not a valid data URL")

        mime_type = m.group("media_type")
        if not mime_type:
            raise ValueError("MIME type is required")
        mime_type = MIMEType(mime_type)

        params: str | None = m.group("params")
        try:
            urllib.parse.parse_qsl(params)
        except ValueError as e:
            logger.warning(f"Invalid parameters in data URL, ignored: {pretty_repr(e)}")
            params = None

        encoded = m.group("base64")
        if encoded is None or encoded.lower() != ";base64":
            raise ValueError("Data URL must be base64 encoded")

        encoded_data: str = m.group("payload")

        return (mime_type, params, "base64", encoded_data)

    def __str__(self) -> str:
        return self.url


def message_contents_from_text(text: str) -> typing.List[typing.Union[str, DataURL]]:
    """Find and parse all data URLs in a string.

    This function splits the input text into a sequence of strings and
    DataURL objects. It will raise a ValueError for data URLs that are
    not base64 encoded.
    """
    pattern = re.compile(
        r"""
        (data:
        (?P<media_type>[^;,]*)
        (?:
            ;
            (?P<params>
                [^;,=]+=[^;,]*
                (?:;[^;,=]+=[^;,]*)*
            )
        )?
        ;base64,
        (?P<payload>(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)
        )
        """,
        re.I | re.VERBOSE | re.S,
    )

    contents = []
    last_end = 0
    for match in pattern.finditer(text):
        if match.start() > last_end:
            contents.append(text[last_end : match.start()])

        contents.append(DataURL.from_url(match.group(0)))
        last_end = match.end()

    if last_end < len(text):
        contents.append(text[last_end:])

    return [c for c in contents if c]
