from glob import glob
from logging import info
from os.path import join as path_join
from PIL import Image
from random import choice
from random import randint

from content import ImageContent

# The directory containing static artwork images.
IMAGES_DIR = 'assets/artwork'

# The file extension of all artwork image files.
IMAGE_EXTENSION = '(gif|png|jpg)'


class Artwork(ImageContent):
    """A collection of randomly selected image artwork."""

    def _customConvert(self, silf, palette, dither=False):
        ''' Convert an RGB or L mode image to use a given P image's palette.
            PIL.Image.quantize() forces dither = 1. 
            This custom quantize function will force it to 0.
            https://stackoverflow.com/questions/29433243/convert-image-to-specific-palette-using-pil-without-dithering
        '''

        silf.load()

        # use palette from reference image made below
        palette.load()
        im = silf.im.convert("P", 0, palette.im)
        # the 0 above means turn OFF dithering making solid colors
        return silf._new(im)

    def image(self, _, size):
        """Generates an artwork image."""

        # Load a random image.
        paths = glob(path_join(IMAGES_DIR, '*.*' ))
        filename = choice(paths)
        info('Using artwork file: %s' % filename)
        image = Image.open(filename)
       
        image = image.convert('RGB')
       
        diff_width = size[0] - image.width
        diff_height = size[1] - image.height

        # Crop the image to a random display-sized area.
        x = randint(0, max(0, -diff_width))
        y = randint(0, max(0, -diff_height))

        if diff_width > 0:
            x -= diff_width / 2
        if diff_height > 0:
            y -= diff_height / 2

        image = image.crop((x, y, x + size[0], y + size[1]))

        return image
