"""
color_printer.py

ColorPrinter Class:
    Uses ANSI escape codes to print colored and formatted text in the terminal.
    Supports:
    - Predefined named colors (HTML-safe)
    - Custom RGB colors via print_rgb()
    - Common text styles: bold, dim, italic, underline, blink, inverse, hidden, strikethrough
    - Combinations of colors and styles via print_formatted()

Author: Ryan LaPine
Date:   2025-07-30
Version:0.1.6
"""

from typing import Any, List, Optional, TextIO


class ColorPrinter:
    """Utility for printing colored and formatted text using ANSI codes."""

    # ANSI escape code templates
    ANSI_BASE = "\x1b[{code}m"
    RGB_FOREGROUND = "\x1b[38;2;{r};{g};{b}m"
    RGB_BACKGROUND = "\x1b[48;2;{r};{g};{b}m"

    # Prefix to mark background-color formats
    BACK_TAG = "back_"

    # Default settings
    DEFAULT_COLOR = "white"
    
    # Predefined HTML-safe color names (add more as needed)
    ALICEBLUE="aliceblue"
    ANTIQUEWHITE="antiquewhite"
    AQUA="aqua"
    AQUAMARINE="aquamarine"
    AZURE="azure"
    BISQUE="bisque"
    BLANCHEDALMOND="blanchedalmond"
    BLUE="blue"
    BLUEVIOLET="blueviolet"
    BROWN="brown"
    BURLYWOOD="burlywood"
    CADETBLUE="cadetblue"
    CHARTREUSE="chartreuse"
    CHOCOLATE="chocolate"
    CORAL="coral"
    CORNFLOWERBLUE="cornflowerblue"
    CORNSILK="cornsilk"
    CRIMSON="crimson"
    CYAN="cyan"
    DARKBLUE="darkblue"
    DARKCYAN="darkcyan"
    DARKGRAY="darkgray"
    DARKGREEN="darkgreen"
    DARKGREY="darkgrey"
    DARKKHAKI="darkkhaki"
    DARKMAGENTA="darkmagenta"
    DARKOLIVEGREEN="darkolivegreen"
    DARKORANGE="darkorange"
    DARKORCHID="darkorchid"
    DARKRED="darkred"
    DARKSALMON="darksalmon"
    DARKSEAGREEN="darkseagreen"
    DARKSLATEBLUE="darkslateblue"
    DARKSLATEGRAY="darkslategray"
    DARKSLATEGREY="darkslategrey"
    DARKTURQUOISE="darkturquoise"
    DARKVIOLET="darkviolet"
    DEEPPINK="deeppink"
    DEEPSKYBLUE="deepskyblue"
    DIMGRAY="dimgray"
    DIMGREY="dimgrey"
    DODGERBLUE="dodgerblue"
    FIREBRICK="firebrick"
    FLORALWHITE="floralwhite"
    FORESTGREEN="forestgreen"
    FUCHSIA="fuchsia"
    GAINSBORO="gainsboro"
    GHOSTWHITE="ghostwhite"
    GOLD="gold"
    GRAY="gray"
    GREEN="green"
    GREENYELLOW="greenyellow"
    GREY="grey"
    HONEYDEW="honeydew"
    HOTPINK="hotpink"
    INDIANRED = "indianred"
    INDIGO="indigo"
    IVORY="ivory"
    KHAKI="khaki"
    LAVENDER="lavender"
    LAVENDERBLUSH="lavenderblush"
    LAWNGREEN="lawngreen"
    LEMONCHIFFON="lemonchiffon"
    LIGHTBLUE="lightblue"
    LIGHTCORAL = "lightcoral"
    LIGHTCYAN="lightcyan"
    LIGHTGOLDENRODYELLOW="lightgoldenrodyellow"
    LIGHTGRAY="lightgray"
    LIGHTGREEN="lightgreen"
    LIGHTGREY="lightgrey"
    LIGHTPINK="lightpink"
    LIGHTSALMON="lightsalmon"
    LIGHTSALMON="lightsalmon"
    LIGHTSEAGREEN="lightseagreen"
    LIGHTSKYBLUE="lightskyblue"
    LIGHTSLATEGRAY="lightslategray"
    LIGHTSLATEGREY="lightslategrey"
    LIGHTSTEELBLUE="lightsteelblue"
    LIGHTYELLOW="lightyellow"
    LIME="lime"
    LIMEGREEN="limegreen"
    LINEN="linen"
    MAGENTA="magenta"
    MEDIUMAQUAMARINE="mediumaquamarine"
    MEDIUMBLUE="mediumblue"
    MEDIUMORCHID="mediumorchid"
    MEDIUMPURPLE="mediumpurple"
    MEDIUMSEAGREEN="mediumseagreen"
    MEDIUMSLATEBLUE="mediumslateblue"
    MEDIUMSLATEBLUE="mediumslateblue"
    MEDIUMSPRINGGREEN="mediumspringgreen"
    MEDIUMTURQUOISE="mediumturquoise"
    MEDIUMVIOLETRED="mediumvioletred"
    MIDNIGHTBLUE="midnightblue"
    MINTCREAM="mintcream"
    MISTYROSE="mistyrose"
    MOCCASIN="moccasin"
    NAVY="navy"
    OLDLACE="oldlace"
    OLIVE="olive"
    OLIVEDRAB="olivedrab"
    ORANGE="orange"
    ORANGERED="orangered"
    ORCHID="orchid"
    PALEGOLDENROD="palegoldenrod"
    PALEGREEN="palegreen"
    PALETURQUOISE="paleturquoise"
    PALEVIOLETRED="palevioletred"
    PAPAYAWHIP="papayawhip"
    PEACHPUFF="peachpuff"
    PERU="peru"
    PINK="pink"
    PLUM="plum"
    POWDERBLUE="powderblue"
    PURPLE="purple"
    REBECCAPURPLE="rebeccapurple"
    RED="red"
    ROSYBROWN="rosybrown"
    ROYALBLUE="royalblue"
    SADDLEBROWN="saddlebrown"
    SALMON = "salmon"
    SANDYBROWN="sandybrown"
    SEAGREEN="seagreen"
    SEASHELL="seashell"
    SIENNA="sienna"
    SILVER="silver"
    SKYBLUE="skyblue"
    SLATEBLUE="slateblue"
    SLATEGRAY="slategray"
    SLATEGREY="slategrey"
    SNOW="snow"
    SPRINGGREEN="springgreen"
    STEELBLUE="steelblue"
    TAN="tan"
    TEAL="teal"
    THISTLE="thistle"
    TOMATO="tomato"
    TURQUOISE="turquoise"
    VIOLET="violet"
    WHEAT="wheat"
    WHITE="white"
    WHITESMOKE="whitesmoke"
    YELLOW="yellow"
    YELLOWGREEN="yellowgreen"


    # RGB mappings for named colors
    COLOR_RGB = {
        ALICEBLUE:(240,248,255),
        ANTIQUEWHITE:(250,235,215),
        AQUA:(0,255,255),
        AQUAMARINE:(127,255,212),
        AZURE:(240,255,255),
        BISQUE:(255,228,196),
        BLANCHEDALMOND:(255,235,205),
        BLUE:(0,0,255),
        BLUEVIOLET:(138,43,226),
        BROWN:(165,42,42),
        BURLYWOOD:(222,184,135),
        CADETBLUE:(95,158,160),
        CHARTREUSE:(127,255,0),
        CHOCOLATE:(210,105,30),
        CORAL:(255,127,80),
        CORNFLOWERBLUE:(100,149,237),
        CORNSILK:(255,248,220),
        CRIMSON:(220,20,60),
        CYAN:(0,255,255),
        DARKBLUE:(0,0,139),
        DARKCYAN:(0,139,139),
        DARKGRAY:(169,169,169),
        DARKGREEN:(0,100,0),
        DARKGREY:(169,169,169),
        DARKKHAKI:(189,183,107),
        DARKMAGENTA:(139,0,139),
        DARKOLIVEGREEN:(85,107,47),
        DARKORANGE:(255,140,0),
        DARKORCHID:(153,50,204),
        DARKRED:(139,0,0),
        DARKSALMON:(233,150,122),
        DARKSEAGREEN:(143,188,139),
        DARKSLATEBLUE:(72,61,139),
        DARKSLATEGRAY:(47,79,79),
        DARKSLATEGREY:(47,79,79),
        DARKTURQUOISE:(0,206,209),
        DARKVIOLET:(148,0,211),
        DEEPPINK:(255,20,147),
        DEEPSKYBLUE:(0,191,255),
        DIMGRAY:(105,105,105),
        DIMGREY:(105,105,105),
        DODGERBLUE:(30,144,255),
        FIREBRICK:(178,34,34),
        FLORALWHITE:(255,250,240),
        FORESTGREEN:(34,139,34),
        FUCHSIA:(255,0,255),
        GAINSBORO:(220,220,220),
        GHOSTWHITE:(248,248,255),
        GOLD:(255,215,0),
        GRAY:(128,128,128),
        GREEN:(0,128,0),
        GREENYELLOW:(173,255,47),
        GREY:(128,128,128),
        HONEYDEW:(240,255,240),
        HOTPINK:(255,105,180),
        INDIANRED: (205, 92, 92),
        INDIGO:(75,0,130),
        IVORY:(255,255,240),
        KHAKI:(240,230,140),
        LAVENDER:(230,230,250),
        LAVENDERBLUSH:(255,240,245),
        LAWNGREEN:(124,252,0),
        LEMONCHIFFON:(255,250,205),
        LIGHTBLUE:(173,216,230),
        LIGHTCORAL: (240, 128, 128),
        LIGHTCYAN:(224,255,255),
        LIGHTGOLDENRODYELLOW:(250,250,210),
        LIGHTGRAY:(211,211,211),
        LIGHTGREEN:(144,238,144),
        LIGHTGREY:(211,211,211),
        LIGHTPINK:(255,182,193),
        LIGHTSALMON:(255,160,122),
        LIGHTSALMON:(255,160,122),
        LIGHTSEAGREEN:(32,178,170),
        LIGHTSKYBLUE:(135,206,250),
        LIGHTSLATEGRAY:(119,136,153),
        LIGHTSLATEGREY:(119,136,153),
        LIGHTSTEELBLUE:(176,196,222),
        LIGHTYELLOW:(255,255,224),
        LIME:(0,255,0),
        LIMEGREEN:(50,205,50),
        LINEN:(250,240,230),
        MAGENTA:(255,0,255),
        MEDIUMAQUAMARINE:(102,205,170),
        MEDIUMBLUE:(0,0,205),
        MEDIUMORCHID:(186,85,211),
        MEDIUMPURPLE:(147,112,219),
        MEDIUMSEAGREEN:(60,179,113),
        MEDIUMSLATEBLUE:(123,104,238),
        MEDIUMSLATEBLUE:(123,104,238),
        MEDIUMSPRINGGREEN:(0,250,154),
        MEDIUMTURQUOISE:(72,209,204),
        MEDIUMVIOLETRED:(199,21,133),
        MIDNIGHTBLUE:(25,25,112),
        MINTCREAM:(245,255,250),
        MISTYROSE:(255,228,225),
        MOCCASIN:(255,228,181),
        NAVY:(0,0,128),
        OLDLACE:(253,245,230),
        OLIVE:(128,128,0),
        OLIVEDRAB:(107,142,35),
        ORANGE:(255,165,0),
        ORANGERED:(255,69,0),
        ORCHID:(218,112,214),
        PALEGOLDENROD:(238,232,170),
        PALEGREEN:(152,251,152),
        PALETURQUOISE:(175,238,238),
        PALEVIOLETRED:(219,112,147),
        PAPAYAWHIP:(255,239,213),
        PEACHPUFF:(255,218,185),
        PERU:(205,133,63),
        PINK:(255,192,203),
        PLUM:(221,160,221),
        POWDERBLUE:(176,224,230),
        PURPLE:(128,0,128),
        REBECCAPURPLE:(102,51,153),
        RED:(255,0,0),
        ROSYBROWN:(188,143,143),
        ROYALBLUE:(65,105,225),
        SADDLEBROWN:(139,69,19),
        SALMON: (250, 128, 114),
        SANDYBROWN:(244,164,96),
        SEAGREEN:(46,139,87),
        SEASHELL:(255,245,238),
        SIENNA:(160,82,45),
        SILVER:(192,192,192),
        SKYBLUE:(135,206,235),
        SLATEBLUE:(106,90,205),
        SLATEGRAY:(112,128,144),
        SLATEGREY:(112,128,144),
        SNOW:(255,250,250),
        SPRINGGREEN:(0,255,127),
        STEELBLUE:(70,130,180),
        TAN:(210,180,140),
        TEAL:(0,128,128),
        THISTLE:(216,191,216),
        TOMATO:(255,99,71),
        TURQUOISE:(64,224,208),
        VIOLET:(238,130,238),
        WHEAT:(245,222,179),
        WHITE:(255,255,255),
        WHITESMOKE:(245,245,245),
        YELLOW:(255,255,0),
        YELLOWGREEN:(154,205,50)
    }

    # Text style keywords
    BOLD = "bold"
    DIM = "dim"
    ITALIC = "italic"
    UNDERLINE = "underline"
    BLINK = "blink"
    INVERSE = "inverse"
    HIDDEN = "hidden"
    STRIKETHROUGH = "strikethrough"
    RESET = "reset"

    # ANSI codes for text styles
    FORMAT_CODES = {
        RESET: "0",
        BOLD: "1",
        DIM: "2",
        ITALIC: "3",
        UNDERLINE: "4",
        BLINK: "5",
        INVERSE: "7",
        HIDDEN: "8",
        STRIKETHROUGH: "9",
    }

    def _build_ansi_sequence(self, *, fg: bool = True, r: int = 0, g: int = 0,
                             b: int = 0) -> str:
        """Build an ANSI sequence for an RGB color.

        Args:
            fg (bool): True for foreground, False for background.
            r (int): Red component (0–255).
            g (int): Green component (0–255).
            b (int): Blue component (0–255).

        Returns:
            str: ANSI escape sequence for the specified RGB color.
        """
        template = self.RGB_FOREGROUND if fg else self.RGB_BACKGROUND
        return template.format(r=r, g=g, b=b)

    def collect_codes(self, formats: List[str]) -> List[str]:
        """Convert style names and color tags into ANSI code sequences.

        Args:
            formats (List[str]): List of style keywords or color tags.

        Returns:
            List[str]: Corresponding list of ANSI sequences.
        """
        codes: List[str] = []
        for fmt in formats:
            key = fmt.strip().lower()
            if key in self.FORMAT_CODES:
                # Text style (bold, underline, reset, etc.)
                codes.append(self.ANSI_BASE.format(code=self.FORMAT_CODES[key]))
            else:
                # Color or background
                is_background = False
                if key.startswith(self.BACK_TAG):
                    is_background = True
                    key = key[len(self.BACK_TAG):]

                rgb = self.COLOR_RGB.get(key)
                if rgb:
                    seq = self._build_ansi_sequence(fg=not is_background,
                                                    r=rgb[0], g=rgb[1], b=rgb[2])
                    codes.append(seq)
        return codes

    def print_ansi(self,
                    *objects: Any,
                    sep: str = " ",
                    end: str = "\n",
                    file: Optional[TextIO] = None,
                    flush: bool = False,
                    reset: bool = True,
                    ansi_list: Optional[List[str]] = None) -> None:
        """Core printer that injects ANSI sequences and resets formatting.

        Args:
            *objects (Any): Objects to print.
            sep (str): Separator between objects.
            end (str): Line ending.
            file (TextIO, optional): Output file-like object.
            flush (bool): Whether to flush the output buffer.
            reset (bool): Append ANSI reset code after printing.
            ansi_list (List[str], optional): ANSI sequences to prepend.
        """
        parts = list(map(str, objects))
        if ansi_list:
            # Prepend codes to the first piece
            parts[0] = "".join(ansi_list) + parts[0]
            if reset:
                # Append reset code to the last piece
                reset_seq = self.ANSI_BASE.format(code=self.FORMAT_CODES[self.RESET])
                parts[-1] = parts[-1] + reset_seq

        print(*parts, sep=sep, end=end, file=file, flush=flush)

    def print_formatted(self,
                        *objects: Any,
                        sep: str = " ",
                        end: str = "\n",
                        file: Optional[TextIO] = None,
                        flush: bool = False,
                        bold: bool = False,
                        dim: bool = False,
                        italic: bool = False,
                        underline: bool = False,
                        blink: bool = False,
                        inverse: bool = False,
                        hidden: bool = False,
                        strikethrough: bool = False,
                        color: str = "",
                        back_color: str = "",
                        reset = True) -> None:
        """Print text with a combination of styles and named colors.

        Args:
            *objects (Any): Objects to print.
            sep (str): Separator between objects.
            end (str): Line ending.
            file (TextIO, optional): Output file-like object.
            flush (bool): Whether to flush the output buffer.
            bold (bool): Apply bold style.
            dim (bool): Apply dim style.
            italic (bool): Apply italic style.
            underline (bool): Apply underline style.
            blink (bool): Apply blink style.
            inverse (bool): Apply inverse style.
            hidden (bool): Apply hidden style.
            strikethrough (bool): Apply strikethrough style.
            color (str): Named foreground color.
            back_color (str): Named background color.
        """
        fmt_keys: List[str] = []
        # Map boolean flags to style keywords
        if bold:
            fmt_keys.append(self.BOLD)
        if dim:
            fmt_keys.append(self.DIM)
        if italic:
            fmt_keys.append(self.ITALIC)
        if underline:
            fmt_keys.append(self.UNDERLINE)
        if blink:
            fmt_keys.append(self.BLINK)
        if inverse:
            fmt_keys.append(self.INVERSE)
        if hidden:
            fmt_keys.append(self.HIDDEN)
        if strikethrough:
            fmt_keys.append(self.STRIKETHROUGH)

        # Add named colors if valid
        name = color.strip().lower()
        if name in self.COLOR_RGB:
            fmt_keys.append(name)

        back_name = back_color.strip().lower()
        if back_name in self.COLOR_RGB:
            fmt_keys.append(self.BACK_TAG + back_name)

        ansi_seq = self.collect_codes(fmt_keys)
        self.print_ansi(*objects, sep=sep, end=end, file=file, flush=flush,
                         reset=reset, ansi_list=ansi_seq)

    def print_rgb(self,
                  *objects: Any,
                  sep: str = " ",
                  end: str = "\n",
                  file: Optional[TextIO] = None,
                  flush: bool = False,
                  reset: bool = True,
                  r: int = 0,
                  g: int = 0,
                  b: int = 0,
                  background: bool = False) -> None:
        """Print text with a custom RGB color.

        Args:
            *objects (Any): Objects to print.
            sep (str): Separator between objects.
            end (str): Line ending.
            file (TextIO, optional): Output file-like object.
            flush (bool): Whether to flush the output buffer.
            reset (bool): Append ANSI reset after text.
            r (int): Red component (0–255).
            g (int): Green component (0–255).
            b (int): Blue component (0–255).
            background (bool): True for background color, False for foreground.
        """
        seq = self._build_ansi_sequence(fg=not background, r=r, g=g, b=b)
        self.print_ansi(*objects, sep=sep, end=end, file=file,
                         flush=flush, reset=reset, ansi_list=[seq])

    def print_color(self,
                    *objects: Any,
                    sep: str = " ",
                    end: str = "\n",
                    file: Optional[TextIO] = None,
                    flush: bool = False,
                    color: str = DEFAULT_COLOR,
                    background: bool = False,
                    reset: bool = True) -> None:
        """Print text with a named color, defaulting to white.

        Args:
            *objects (Any): Objects to print.
            sep (str): Separator between objects.
            end (str): Line ending.
            file (TextIO, optional): Output file-like object.
            flush (bool): Whether to flush the output buffer.
            color (str): Named color (falls back to DEFAULT_COLOR).
            background (bool): True for background color, False for foreground.
        """
        name = color.strip().lower()
        rgb = self.COLOR_RGB.get(name, self.COLOR_RGB[self.DEFAULT_COLOR])
        self.print_rgb(*objects, sep=sep, end=end, file=file, flush=flush,
                       reset=reset, r=rgb[0], g=rgb[1], b=rgb[2],
                       background=background)