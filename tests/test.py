#!/usr/bin/env python

from mongoengine import *
from rimage.models import ResourceWithImage, Image

from rimage.config import update_config

class TestDoc( Document, ResourceWithImage):
    original_image = EmbeddedDocumentField( Image)
    display_image = EmbeddedDocumentField( Image)
    thumbnail = EmbeddedDocumentField( Image)


if __name__ == "__main__":
    import sys

    if( len( sys.argv) < 5):
        print "test.py aws_id aws_secret aws_bucket image_url"
        sys.exit( 1)

    aws_id = sys.argv[1]
    aws_secret = sys.argv[2]
    bucket_name = sys.argv[3]
    image_url = sys.argv[4]

    update_config({"AWS_KEY": aws_id, "AWS_SECRET": aws_secret, "S3_BUCKET_NAME": bucket_name})

    d = TestDoc()
    d.set_resource_image_from_url( image_url)

    print d.original_image.image_id
    print d.display_image.image_id
    print d.thumbnail.image_id
