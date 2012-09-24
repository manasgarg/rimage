#!/usr/bin/env python

config = {
    "AWS_KEY": "",
    "AWS_SECRET": "",
    "S3_BUCKET_NAME": "images",
    "S3_IMAGES_PATH_PREFIX": "",
}

def update_config( new_config):
    config.update( new_config)
