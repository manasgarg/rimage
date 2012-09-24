#!/usr/bin/env python

import Image as PILImage
from StringIO import StringIO

def crop_image( img, dst_ratio):
    src_width, src_height = img.size
    src_ratio = float(src_width) / float(src_height)

    if dst_ratio < src_ratio:
        crop_height = src_height
        crop_width = crop_height * dst_ratio
        x_offset = float(src_width - crop_width) / 2
        y_offset = 0
    else:
        crop_width = src_width
        crop_height = crop_width / dst_ratio
        x_offset = 0
        y_offset = float(src_height - crop_height) / 3
    x_offset = int(x_offset)
    y_offset = int(y_offset)

    img = img.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))

    return img

def create_thumbnail( filelikeobj, dimensions):
    img = PILImage.open ( StringIO(filelikeobj.read()) )
    return create_thumbnail_from_img( img, dimensions)

def create_thumbnail_from_img( img, dimensions):
    maxw, maxh = dimensions
    scale_ratio = float( maxw) / float( maxh)

    img = crop_image( img, scale_ratio)
    currw, currh = img.size

    if( currw <= maxw and currh <= maxh):
        return img

    img = img.resize( (maxw, maxh), PILImage.ANTIALIAS)

    return img

