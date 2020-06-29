"""Holds template variables for HTML/JS/CSS."""

from utils import url_join


class Labels(object):
    """Text labels."""

    TITLE = 'Dixit'
    NEW_GAME = 'New Game'
    DEFAULT_TEXT = 'Say something!'


class WebPaths(object):
    """Client-side paths to resource directories."""

    STATIC    = 'static'
    IMAGES    = url_join(STATIC, 'images')
    JS        = url_join(STATIC, 'js')
    CSS       = url_join(STATIC, 'css')
    CARDS     = url_join(STATIC, 'cards')
    SMILIES   = url_join(IMAGES, 'smilies')
    JQUERY_UI = url_join(JS, 'jquery-ui-1.10.4')


class Images(object):
    """Client-side paths to images."""

    BANNER      = url_join(WebPaths.IMAGES, 'banner.png')
    BUNNY_READY = url_join(WebPaths.IMAGES, 'bunnyready.png')
    BUNNY_RUN   = url_join(WebPaths.IMAGES, 'bunnyrun.png')
    THINKING    = url_join(WebPaths.IMAGES, 'thinking.gif')
    CARD_BACK   = url_join(WebPaths.IMAGES, 'cardback.png')
    VOTE_TOKEN  = url_join(WebPaths.IMAGES, 'votetoken.png')
    YOUR_TURN   = url_join(WebPaths.IMAGES, 'arrow.ico')
    ICON_ACTIVE = url_join(WebPaths.IMAGES, 'bunnyicongreen.png')
    ICON_AWAY   = url_join(WebPaths.IMAGES, 'bunnyiconyellow.png')
    ICON_ASLEEP = url_join(WebPaths.IMAGES, 'bunnyicongrey.png')


class Sizes(object):
    """Display sizes for images."""

    PIECE        = 45
    BUNNY_PICKER = 70
    CARD_WIDTH   = 210
    CARD_HEIGHT  = 320
    YOUR_TURN    = 24
    TOKEN        = 50


class BunnyPalette(object):
    """Bunny colours to choose from."""

    RED    = '#c52828'
    ORANGE = '#e59100'
    YELLOW = '#e2e05d'
    GREEN  = '#12751b'
    BLUE   = '#214ddc'
    PURPLE = '#a41bf3'
    PINK   = '#ff14f3'
    LGREEN = '#90ee90'
    BLACK  = '#3a363b'
    
    HPINK  = '#ff69b4'
    GREY   = '#c0c0c0'
    RAINB  = 'linear-gradient(to right, red,orange,yellow,green,blue,indigo,violet)'
    
    GBLUE = '#0d9a86'
    MARON = '#800000'
    
    COMM   = 'url(' + url_join(WebPaths.IMAGES, "comm.png") + ')'
    ANAR   = 'url(' + url_join(WebPaths.IMAGES, "anar.jpg") + ')'
    
    allColors = {'RED':RED, 'ORANGE':ORANGE, 'YELLOW':YELLOW, 'GREEN':GREEN, 'BLUE':BLUE, 'PURPLE':PURPLE, 
                'PINK':PINK, 'LGREEN':LGREEN, 'BLACK':BLACK, 'HPINK':HPINK, 'GREY':GREY, 'RAINB':RAINB,
                'MARON':MARON, 'GBLUE':GBLUE, 'COMM':COMM, 'ANAR':ANAR}
    allCols = [['RED', 'ORANGE', 'YELLOW','GREEN'] ,['BLUE', 'PURPLE','PINK', 'LGREEN'], [ 'BLACK', 'HPINK', 'GREY', 'RAINB'], ['MARON', 'GBLUE', 'COMM', 'ANAR']]
    
    @classmethod
    def is_colour(cls, cid):
        """Determines if the given colour id is valid."""
        return cid in cls.allColors
