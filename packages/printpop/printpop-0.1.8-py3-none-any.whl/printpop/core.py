"""
core.py

Public-facing functions for printing styled text using the ColorPrinter class.
Supports ANSI formatting for text adornments, foreground/background color names, and RGB values.

Features:
- All 144 HTML-safe color names via named functions (e.g., print_indianred()).
- Arbitrary RGB values via print_rgb().
- Text adornments such as: bold, dim, italic, underline, blink, inverse, strikethrough.
- Combined styling using print_formatted().

Usage:
Use individual print_* functions for simple formatting, or print_formatted() for multiple styles.
Create reusable, styled print calls for terminal output, logs, or CLI utilities.

Author: Ryan LaPine  
Version: 0.1.8  
Date: 2025-07-30
"""

from .color_printer import ColorPrinter

#only show rgf of factor 51 so not to show millions of results
DEFAULT_RGB_FACTOR = 51

# The public facing wrapper functions use the ColorPrinter class to print text.
# This holds the ColorPrinter object so it can be reused if already created.
_color_printer = None
def _check_printer_obj():
    global _color_printer
    if _color_printer is None:
        _color_printer = ColorPrinter()
    return _color_printer


"""
Format print functions — wrappers for printing text with specific color settings.

Supports:
- bold
- dim
- italic
- underline
- blink
- inverse
- hidden
- strikethrough
- color (text color)
- back_color (background color)
"""

def print_formatted(
    *objects,
    sep=' ',
    end='\n',
    file=None,
    flush=False,
    bold=False,
    dim=False,
    italic=False,
    underline=False,
    blink=False,
    inverse=False,
    hidden=False,
    strikethrough=False,
    color="",
    back_color=""
):
    """Prints text using multiple ANSI format options.

    Supports combinations of text formatting styles, foreground and background colors.

    Args:
        *objects: Items to print.
        sep (str): Separator between items.
        end (str): End character.
        file (IO, optional): Output stream (defaults to sys.stdout).
        flush (bool): Whether to flush the output buffer.
        bold (bool): If True, applies bold formatting.
        dim (bool): If True, applies dim formatting.
        italic (bool): If True, applies italic formatting.
        underline (bool): If True, underlines text.
        blink (bool): If True, enables blinking text.
        inverse (bool): If True, reverses foreground/background colors.
        hidden (bool): If True, hides the text.
        strikethrough (bool): If True, applies strike-through.
        color (str): Foreground color name (HTML-safe).
        back_color (str): Background color name (HTML-safe).

    Returns:
        None
    """
    printer = _check_printer_obj()
    return printer.print_formatted(
        *objects,
        sep=sep,
        end=end,
        file=file,
        flush=flush,
        bold=bold,
        dim=dim,
        italic=italic,
        underline=underline,
        blink=blink,
        strikethrough=strikethrough,
        inverse=inverse,
        hidden=hidden,
        color=color,
        back_color=back_color
    )

#individual format print functions
def print_bold(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=reset, bold=True)

def print_italic(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=reset, italic=True)  

def print_underline(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=reset, underline=True)

def print_strikethrough(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=reset, strikethrough=True) 

def print_dim(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=reset, dim=True)
      
def print_blink(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, blink=True)

def print_inverse(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, inverse=True)

def print_hidden(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, hidden=True)

def print_reset(*objects, sep=' ', end='\n', file=None, flush=False, reset=True):
    _color_printer = _check_printer_obj()
    return _color_printer.print_formatted(*objects, sep=sep, end=end, file=file, flush=flush, reset=True)
    

"""
Color print functions — wrappers for printing text with specific color settings.

Supports:
- RGB color values via print_rgb().
- Named HTML-safe color strings via print_color().
"""


def print_rgb(
    *objects,
    sep=' ',
    end='\n',
    file=None,
    flush=False,
    reset=True,
    r=0,
    g=0,
    b=0,
    background=False
):
    """Prints text using a specific RGB color.

    Args:
        *objects: Items to print.
        sep (str): Separator between objects.
        end (str): End character after printing.
        file (IO, optional): Output stream.
        flush (bool): If True, flushes the output buffer.
        reset (bool): Resets ANSI formatting after printing.
        r (int): Red component (0–255).
        g (int): Green component (0–255).
        b (int): Blue component (0–255).

    Returns:
        None
    """
    printer = _check_printer_obj()
    return printer.print_rgb(
        *objects,
        sep=sep,
        end=end,
        file=file,
        flush=flush,
        reset=reset,
        r=r,
        g=g,
        b=b,
        background=background
    )


def print_color(
    *objects,
    color,
    sep=' ',
    end='\n',
    file=None,
    flush=False,
    reset=True,
    background=False
):
    """Prints text using a named color.

    Args:
        *objects: Items to print.
        color (str): Name of the HTML-safe color (e.g., 'salmon', 'lightcoral').
        sep (str): Separator between objects.
        end (str): End character after printing.
        file (IO, optional): Output stream.
        flush (bool): If True, flushes the output buffer.
        reset (bool): Resets ANSI formatting after printing.
        background (bool): If True, applies color to the background instead of foreground.

    Returns:
        None
    """
    printer = _check_printer_obj()
    return printer.print_color(
        *objects,
        sep=sep,
        end=end,
        file=file,
        flush=flush,
        reset=reset,
        color=color,
        background=background
    )

# individual color functions for printing text and background colors

def print_indianred(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.INDIANRED, background=background)
def print_indianred_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_indianred(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightcoral(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTCORAL, background=background)
def print_lightcoral_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightcoral(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_salmon(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SALMON, background=background)
def print_salmon_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_salmon(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darksalmon(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKSALMON, background=background)
def print_darksalmon_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darksalmon(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightsalmon(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTSALMON, background=background)
def print_lightsalmon_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightsalmon(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_crimson(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.CRIMSON, background=background)
def print_crimson_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_crimson(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_red(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.RED, background=background)
def print_red_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_red(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_firebrick(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.FIREBRICK, background=background)
def print_firebrick_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_firebrick(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkred(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKRED, background=background)
def print_darkred_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkred(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_pink(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PINK, background=background)
def print_pink_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_pink(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightpink(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTPINK, background=background)
def print_lightpink_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightpink(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_hotpink(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.HOTPINK, background=background)
def print_hotpink_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_hotpink(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_deeppink(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DEEPPINK, background=background)
def print_deeppink_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_deeppink(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumvioletred(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMVIOLETRED, background=background)
def print_mediumvioletred_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumvioletred(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_palevioletred(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PALEVIOLETRED, background=background)
def print_palevioletred_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_palevioletred(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightsalmon(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTSALMON, background=background)
def print_lightsalmon_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightsalmon(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_coral(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.CORAL, background=background)
def print_coral_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_coral(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_tomato(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.TOMATO, background=background)
def print_tomato_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_tomato(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_orangered(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.ORANGERED, background=background)
def print_orangered_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_orangered(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkorange(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKORANGE, background=background)
def print_darkorange_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkorange(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_orange(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.ORANGE, background=background)
def print_orange_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_orange(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_gold(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.GOLD, background=background)
def print_gold_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_gold(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_yellow(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.YELLOW, background=background)
def print_yellow_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_yellow(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightyellow(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTYELLOW, background=background)
def print_lightyellow_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightyellow(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lemonchiffon(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LEMONCHIFFON, background=background)
def print_lemonchiffon_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lemonchiffon(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightgoldenrodyellow(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTGOLDENRODYELLOW, background=background)
def print_lightgoldenrodyellow_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightgoldenrodyellow(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_papayawhip(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PAPAYAWHIP, background=background)
def print_papayawhip_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_papayawhip(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_moccasin(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MOCCASIN, background=background)
def print_moccasin_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_moccasin(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_peachpuff(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PEACHPUFF, background=background)
def print_peachpuff_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_peachpuff(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_palegoldenrod(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PALEGOLDENROD, background=background)
def print_palegoldenrod_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_palegoldenrod(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_khaki(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.KHAKI, background=background)
def print_khaki_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_khaki(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkkhaki(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKKHAKI, background=background)
def print_darkkhaki_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkkhaki(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lavender(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LAVENDER, background=background)
def print_lavender_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lavender(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_thistle(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.THISTLE, background=background)
def print_thistle_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_thistle(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_plum(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PLUM, background=background)
def print_plum_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_plum(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_violet(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.VIOLET, background=background)
def print_violet_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_violet(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_orchid(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.ORCHID, background=background)
def print_orchid_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_orchid(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_fuchsia(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.FUCHSIA, background=background)
def print_fuchsia_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_fuchsia(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_magenta(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MAGENTA, background=background)
def print_magenta_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_magenta(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumorchid(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMORCHID, background=background)
def print_mediumorchid_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumorchid(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumpurple(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMPURPLE, background=background)
def print_mediumpurple_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumpurple(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_rebeccapurple(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.REBECCAPURPLE, background=background)
def print_rebeccapurple_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_rebeccapurple(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_blueviolet(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.BLUEVIOLET, background=background)
def print_blueviolet_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_blueviolet(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkviolet(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKVIOLET, background=background)
def print_darkviolet_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkviolet(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkorchid(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKORCHID, background=background)
def print_darkorchid_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkorchid(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkmagenta(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKMAGENTA, background=background)
def print_darkmagenta_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkmagenta(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_purple(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PURPLE, background=background)
def print_purple_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_purple(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_indigo(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.INDIGO, background=background)
def print_indigo_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_indigo(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_slateblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SLATEBLUE, background=background)
def print_slateblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_slateblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkslateblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKSLATEBLUE, background=background)
def print_darkslateblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkslateblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumslateblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMSLATEBLUE, background=background)
def print_mediumslateblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumslateblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_greenyellow(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.GREENYELLOW, background=background)
def print_greenyellow_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_greenyellow(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_chartreuse(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.CHARTREUSE, background=background)
def print_chartreuse_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_chartreuse(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lawngreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LAWNGREEN, background=background)
def print_lawngreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lawngreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lime(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIME, background=background)
def print_lime_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lime(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_limegreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIMEGREEN, background=background)
def print_limegreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_limegreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_palegreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PALEGREEN, background=background)
def print_palegreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_palegreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTGREEN, background=background)
def print_lightgreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumspringgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMSPRINGGREEN, background=background)
def print_mediumspringgreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumspringgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_springgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SPRINGGREEN, background=background)
def print_springgreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_springgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumseagreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMSEAGREEN, background=background)
def print_mediumseagreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumseagreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_seagreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SEAGREEN, background=background)
def print_seagreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_seagreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_forestgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.FORESTGREEN, background=background)
def print_forestgreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_forestgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_green(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.GREEN, background=background)
def print_green_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_green(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKGREEN, background=background)
def print_darkgreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_yellowgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.YELLOWGREEN, background=background)
def print_yellowgreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_yellowgreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_olivedrab(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.OLIVEDRAB, background=background)
def print_olivedrab_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_olivedrab(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_olive(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.OLIVE, background=background)
def print_olive_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_olive(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkolivegreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKOLIVEGREEN, background=background)
def print_darkolivegreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkolivegreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumaquamarine(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMAQUAMARINE, background=background)
def print_mediumaquamarine_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumaquamarine(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkseagreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKSEAGREEN, background=background)
def print_darkseagreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkseagreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightseagreen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTSEAGREEN, background=background)
def print_lightseagreen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightseagreen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkcyan(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKCYAN, background=background)
def print_darkcyan_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkcyan(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_teal(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.TEAL, background=background)
def print_teal_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_teal(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_aqua(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.AQUA, background=background)
def print_aqua_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_aqua(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_cyan(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.CYAN, background=background)
def print_cyan_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_cyan(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightcyan(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTCYAN, background=background)
def print_lightcyan_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightcyan(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_paleturquoise(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PALETURQUOISE, background=background)
def print_paleturquoise_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_paleturquoise(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_aquamarine(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.AQUAMARINE, background=background)
def print_aquamarine_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_aquamarine(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_turquoise(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.TURQUOISE, background=background)
def print_turquoise_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_turquoise(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumturquoise(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMTURQUOISE, background=background)
def print_mediumturquoise_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumturquoise(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkturquoise(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKTURQUOISE, background=background)
def print_darkturquoise_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkturquoise(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_cadetblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.CADETBLUE, background=background)
def print_cadetblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_cadetblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_steelblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.STEELBLUE, background=background)
def print_steelblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_steelblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightsteelblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTSTEELBLUE, background=background)
def print_lightsteelblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightsteelblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_powderblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.POWDERBLUE, background=background)
def print_powderblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_powderblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTBLUE, background=background)
def print_lightblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_skyblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SKYBLUE, background=background)
def print_skyblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_skyblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightskyblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTSKYBLUE, background=background)
def print_lightskyblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightskyblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_deepskyblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DEEPSKYBLUE, background=background)
def print_deepskyblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_deepskyblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_dodgerblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DODGERBLUE, background=background)
def print_dodgerblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_dodgerblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_cornflowerblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.CORNFLOWERBLUE, background=background)
def print_cornflowerblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_cornflowerblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumslateblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMSLATEBLUE, background=background)
def print_mediumslateblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumslateblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_royalblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.ROYALBLUE, background=background)
def print_royalblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_royalblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_blue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.BLUE, background=background)
def print_blue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_blue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mediumblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MEDIUMBLUE, background=background)
def print_mediumblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mediumblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKBLUE, background=background)
def print_darkblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_navy(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.NAVY, background=background)
def print_navy_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_navy(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_midnightblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MIDNIGHTBLUE, background=background)
def print_midnightblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_midnightblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkgray(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKGRAY, background=background)
def print_darkgray_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkgray(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkgrey(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKGREY, background=background)
def print_darkgrey_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkgrey(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_dimgray(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DIMGRAY, background=background)
def print_dimgray_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_dimgray(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_dimgrey(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DIMGREY, background=background)
def print_dimgrey_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_dimgrey(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightslategray(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTSLATEGRAY, background=background)
def print_lightslategray_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightslategray(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightslategrey(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTSLATEGREY, background=background)
def print_lightslategrey_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightslategrey(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightgray(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTGRAY, background=background)
def print_lightgray_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightgray(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lightgrey(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LIGHTGREY, background=background)
def print_lightgrey_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lightgrey(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_slategray(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SLATEGRAY, background=background)
def print_slategray_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_slategray(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_slategrey(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SLATEGREY, background=background)
def print_slategrey_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_slategrey(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_gray(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.GRAY, background=background)
def print_gray_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_gray(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_grey(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.GREY, background=background)
def print_grey_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_grey(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkslategray(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKSLATEGRAY, background=background)
def print_darkslategray_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkslategray(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_darkslategrey(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.DARKSLATEGREY, background=background)
def print_darkslategrey_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_darkslategrey(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_gainsboro(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.GAINSBORO, background=background)
def print_gainsboro_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_gainsboro(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_whitesmoke(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.WHITESMOKE, background=background)
def print_whitesmoke_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_whitesmoke(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_silver(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SILVER, background=background)
def print_silver_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_silver(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_white(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.WHITE, background=background)
def print_white_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_white(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_ghostwhite(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.GHOSTWHITE, background=background)
def print_ghostwhite_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_ghostwhite(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_snow(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SNOW, background=background)
def print_snow_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_snow(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_honeydew(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.HONEYDEW, background=background)
def print_honeydew_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_honeydew(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mintcream(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MINTCREAM, background=background)
def print_mintcream_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mintcream(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_azure(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.AZURE, background=background)
def print_azure_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_azure(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_aliceblue(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.ALICEBLUE, background=background)
def print_aliceblue_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_aliceblue(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_floralwhite(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.FLORALWHITE, background=background)
def print_floralwhite_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_floralwhite(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_seashell(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SEASHELL, background=background)
def print_seashell_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_seashell(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_oldlace(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.OLDLACE, background=background)
def print_oldlace_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_oldlace(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_ivory(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.IVORY, background=background)
def print_ivory_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_ivory(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_lavenderblush(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LAVENDERBLUSH, background=background)
def print_lavenderblush_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_lavenderblush(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_linen(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.LINEN, background=background)
def print_linen_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_linen(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_mistyrose(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.MISTYROSE, background=background)
def print_mistyrose_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_mistyrose(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_antiquewhite(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.ANTIQUEWHITE, background=background)
def print_antiquewhite_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_antiquewhite(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_bisque(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.BISQUE, background=background)
def print_bisque_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_bisque(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_blanchedalmond(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.BLANCHEDALMOND, background=background)
def print_blanchedalmond_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_blanchedalmond(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_wheat(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.WHEAT, background=background)
def print_wheat_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_wheat(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_cornsilk(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.CORNSILK, background=background)
def print_cornsilk_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_cornsilk(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_brown(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.BROWN, background=background)
def print_brown_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_brown(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_saddlebrown(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SADDLEBROWN, background=background)
def print_saddlebrown_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_saddlebrown(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_sienna(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SIENNA, background=background)
def print_sienna_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_sienna(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_chocolate(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.CHOCOLATE, background=background)
def print_chocolate_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_chocolate(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_peru(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.PERU, background=background)
def print_peru_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_peru(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_sandybrown(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.SANDYBROWN, background=background)
def print_sandybrown_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_sandybrown(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_burlywood(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.BURLYWOOD, background=background)
def print_burlywood_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_burlywood(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_tan(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.TAN, background=background)
def print_tan_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_tan(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


def print_rosybrown(*objects, sep=' ', end='\n', file=None, flush=False, background=False):
    return print_color(*objects, sep=sep, end=end, file=file, flush=flush, reset=True, 
                       color=ColorPrinter.ROSYBROWN, background=background)
def print_rosybrown_back(*objects, sep=' ', end='\n', file=None, flush=False):
    return print_rosybrown(*objects, sep=' ', end='\n', file=None, flush=False, background=True) 


"""
functions to print available color and format options
"""
# Prints all available color options.
def print_all_color_options():
    _color_printer = _check_printer_obj()
    colors_options = []
    col_widths=[25,25,25,35,35]
    headers=["TEXT COLOR", "BACKGROUND COLOR", "RGB", "PRINT FUNCTION", "BACKGROUND PRINT FUNCTION"]
    header_str = (headers[0].ljust(col_widths[0], ' ') +
                    headers[1].ljust(col_widths[1], ' ') +
                    headers[2].ljust(col_widths[2], ' ') +
                    headers[3].ljust(col_widths[3], ' ') +
                    headers[4].ljust(col_widths[4], ' '))
    divider_str = '-' * len(header_str)
    print_bold(header_str)
    print(divider_str)
    colors_options = []
                
    for color in _color_printer.COLOR_RGB:
        color_rgb = _color_printer.COLOR_RGB[color]
        colors_options.append((color,color_rgb))
        _color_printer.print_rgb(color.ljust(col_widths[0], ' '),
                        r=color_rgb[0],
                        g=color_rgb[1],
                        b=color_rgb[2],
                        end='')
        _color_printer.print_rgb(color.ljust(col_widths[1], ' '),
                        r=color_rgb[0],
                        g=color_rgb[1],
                        b=color_rgb[2],
                        background=True,
                        end='')
        color_rgb_str = "rgb" + str(color_rgb)
        _color_printer.print_rgb(color_rgb_str.ljust(col_widths[2], ' '),
                        r=color_rgb[0],
                        g=color_rgb[1],
                        b=color_rgb[2],
                        end='')
        print_funct_str = "print_" + color
        print_back_funct_str = "print_" + color + "_back"
        print_function = globals()[print_funct_str]
        print_back_function = globals()[print_back_funct_str]
        print_funct_str = print_funct_str + "()"
        print_back_funct_str = print_back_funct_str + "()"
        print_function(print_funct_str.ljust(col_widths[3],' '), end='')
        print_back_function(print_back_funct_str.ljust(col_widths[4], ' '))

        print(divider_str)
    
    return colors_options

# Prints all available format options.
def print_all_format_options():
    _color_printer = _check_printer_obj()
    format_options = []
    col_widths=[20,20,30]
    headers=["FORMAT NAME", "FORMAT", "PRINT FORMAT FUNCTION"]
    header_str = (headers[0].ljust(col_widths[0], ' ') +
                    headers[1].ljust(col_widths[1], ' ') +
                    headers[2].ljust(col_widths[2], ' '))
    divider_str = '-' * len(header_str)
    print_bold(header_str)
    print(divider_str)
    for format_name in _color_printer.FORMAT_CODES.keys():
        format_options.append(format_name)
        print(format_name.ljust(col_widths[0], ' '), end='')
        ansi_codes = _color_printer.collect_codes(formats=[format_name])
        _color_printer.print_ansi(format_name.ljust(col_widths[1], ' '), ansi_list=ansi_codes, end='')
        format_funct_str = "print_" + format_name + "()"
        print(format_funct_str.ljust(col_widths[2],' '))
        print(divider_str)
        
    return format_options

# Prints some rgb options.
# There are over 16 million possible rgb combinations, so this prints a subset of them
# based on the factor parameter that only prints rgb values that are multiples of the factor.
def print_rgb_options(factor=None):
    _color_printer = _check_printer_obj()
    if factor is None:
        factor = DEFAULT_RGB_FACTOR
    
    col_widths=[20,20,45]
    headers=["RGB", "HEXIDECIMAL", "PRINT RGB FUNCTION"]
    header_str = (headers[0].ljust(col_widths[0], ' ') +
                    headers[1].ljust(col_widths[1], ' ') +
                    headers[2].ljust(col_widths[2], ' '))
    divider_str = '-' * len(header_str)
    print_bold(header_str)
    print(divider_str)
    for r in range(0,256,factor):
        for g in range(0,256,factor):
            for b in range(0,256,factor):
                rgb_str = f"rgb({r},{g},{b})".ljust(20, ' ')
                hex_str = "#{:02x}{:02x}{:02x}".format(r, g, b)
                _color_printer.print_rgb(rgb_str.ljust(col_widths[0], ' '), background=True, r=r, g=g, b=b, end='')
                _color_printer.print_rgb(hex_str.ljust(col_widths[1], ' '), background=True, r=r, g=g, b=b, end='')
                rgb_funct_str = f"print_rgb(*print_args, r={r}, g={g}, b={b})"
                print(rgb_funct_str.ljust(col_widths[2], ' '))
                print(divider_str)
                
    return None


"""
Console testing script entry point.

Provides a CLI for exploring available color and format options
supported by the ColorPrinter module. Interactive prompts allow the
user to test individual styles, RGB values, and combined formatting.
"""


def main():
    """Runs the console interface loop for demonstrating ColorPrinter functionality."""
    print()

    print_bold("PrintPop - Prints to Console with Color and Formatting")

    user_continue = True
    while user_continue:
        # Display menu options
        print()
        print_bold("Options")
        print("1) Print Available Colors.")
        print("2) Print Available Formats.")
        print("3) Print RGB Options.")
        print("4) Multiple Formats.")
        print("q) Exit.")
        print()
        print_bold("Enter an option:", end='')
        option = input().strip().lower()
        print()

        match option:
            case '1':
                # Show all named color options
                print_bold("All Available Colors:")
                print_all_color_options()
            case '2':
                # Show all text formatting styles
                print_bold("All Available Formats:")
                print_all_format_options()
            case '3':
                # Show RGB samples with simplified intervals
                print_bold("RGB Options:")
                print_bold(
                    "(All RGB values are available. "
                    "Only values of factor 51 are being shown.)"
                )
                print_rgb_options()
            case '4':
                # Prompt user for multiple format choices
                print_bold("Multiple Formats:")
                print_bold(
                    "(Some formats cannot be combined. "
                    "Some formats are not supported on all consoles.)"
                )

                # Gather individual formatting inputs
                bold = input("BOLD (y/n):") == "y"
                dim = input("DIM (y/n):") == "y"
                italic = input("ITALIC (y/n):") == "y"
                underline = input("UNDERLINE (y/n):") == "y"
                blink = input("BLINK (y/n):") == "y"
                inverse = input("INVERSE (y/n):") == "y"
                hidden = input("HIDDEN (y/n):") == "y"
                strikethrough = input("STRIKETHROUGH (y/n):") == "y"
                color = input("COLOR:").strip()
                back_color = input("BACK_COLOR:").strip()

                # Print sample string with selected styles
                print_formatted(
                    f"BOLD:{bold}, DIM:{dim}, ITALIC:{italic}, "
                    f"UNDERLINE:{underline}, BLINK:{blink}, INVERSE:{inverse}, "
                    f"HIDDEN:{hidden}, STRIKETHROUGH:{strikethrough}, COLOR:{color}, "
                    f"BACK_COLOR:{back_color}",
                    bold=bold,
                    dim=dim,
                    italic=italic,
                    underline=underline,
                    blink=blink,
                    inverse=inverse,
                    strikethrough=strikethrough,
                    color=color,
                    back_color=back_color
                )
            case _:
                # Exit loop
                user_continue = False
                print_bold("Bye!")
                print()


if __name__ == "__main__":
    main()