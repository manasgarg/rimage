#!/usr/bin/env python
"""A generic module to meet the need of dealing with images for various
resources. The important stuff here is the ResourceWithImage class. Mongo
Documents should extend this class if they can be represented with an image.
"""

from mongoengine import *
import Image as PILImage
from cStringIO import StringIO
from utils import create_thumbnail
import bson.objectid
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from config import config

import urllib2, threading, os, time

import logging
logger = logging.getLogger( "rimage")

class Image( EmbeddedDocument):
    """Represents an image. image_id is a unique identifier to uniquely
    identify an image. The URL of the image would be settings.CDN_URL +
    settings.S3_PATH_PREFIX + image_id + .jpg.
    """
    image_id = StringField()
    width = IntField()
    height = IntField()

class ResourceWithImage(object):
    """This class expects presence of the following fields:
        * original_image of type Image.
        * Any thumbnails defined in thumbnail_deatils property.
    """

    @property
    def thumbnail_details( self):
        """It's a hashtable of thumbnail field names and the dimensions. When
        an image is set for this object, this table will be scanned and
        thumbnails specified here will be generated for the given dimensions.
        """
        return { "display_image": { 'w': 180 }, "thumbnail": { "w": 50, "h": 50 } }

    @property
    def has_image( self):
        """Tells you whether there is an image for this resource or not."""
        return self.original_image != None

    def set_resource_image( self, filelikeobj):
        """This is the main method for setting an image. Just give it the file
        like object for reading the image contents and this method will peform
        the following:
            * Save the original image in original_image field.
            * Look at the thumbnail_details property and generate thumbnails specified there.
        It pushes all images to S3 in separate threads to speed up the IO.
        """

        if( not filelikeobj):
            return

        def push_image( attr_name, img, quality=80):
            """A unit of work in terms of pushing image to S3."""
            image_id = str( bson.objectid.ObjectId())
            filelikeobj = StringIO()
            img.save ( filelikeobj, "JPEG", quality=quality )
            add_to_s3( image_id + ".jpg", filelikeobj.getvalue())
            setattr( self, attr_name, Image( image_id=image_id, width=img.size[0], height=img.size[1]))

        image_dict = {}

        orig_content = filelikeobj.read()

        filelikeobj = StringIO(orig_content)
        orig_img = PILImage.open ( filelikeobj )
        if orig_img.mode != "RGB":
            orig_img = orig_img.convert("RGB")

        image_list = [ ("original_image", orig_img, 100)]

        for thumbnail_name in self.thumbnail_details.keys():
            d = self.thumbnail_details[ thumbnail_name]
            width = d.get( 'w', 0)
            height = d.get( 'h', 0)

            image_width, image_height = orig_img.size

            if( width and height):
                dimensions = (width, height)
            elif( width):
                dimensions = ( width, int( float( image_height*width)/image_width))
            elif( height):
                dimensions = ( int( float( height*image_width)/image_height), height)
            else:
                logger.error( "Cannot have zero dimensions for a thumbnail in class: %s" % self.__class__.__name__)
                continue

            thumb_img = create_thumbnail( StringIO( orig_content), dimensions)
            if thumb_img.mode != "RGB":
                thumb_img = thumb_img.convert("RGB")

            image_list.append( (thumbnail_name, thumb_img, 80))

        thread_list = []
        for item in image_list:
            t = threading.Thread( target=push_image, args=item)
            t.start()
            thread_list.append( t)

        for t in thread_list:
            t.join()

    def set_resource_image_from_url( self, url):
        """Similar to set_resource_image() except that it fetches the image
        data from a given url.
        """
        req = urllib2.Request( url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_8; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.102 Safari/534.13"})
        f = urllib2.urlopen( req)
        self.set_resource_image( f)
        f.close()


def add_to_s3 ( name, contents, content_type="image/jpg"):
    bucket_name = config["S3_IMAGES_BUCKET_NAME"]
    path_prefix = config.get("S3_IMAGES_PATH_PREFIX", "")
    conn = S3Connection(config["AWS_KEY"], config["AWS_SECRET"])

    bucket = conn.get_bucket(bucket_name)

    k = Key(bucket)
    if( path_prefix):
        k.key = path_prefix + name
    else:
        k.key = name

    k.set_metadata( "Expires", "Thu, 15 Apr 2020 20:00:00 GMT")
    k.set_metadata( "Content-Type", content_type)
    k.set_contents_from_string(contents)
    k.set_acl('public-read')

    print name, len( contents)
