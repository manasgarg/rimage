Associate a profile image with mongo documents
==============================================

Let's say you have some documents in your mongodb that represent resources
(e.g. users). This module can help you associate a profile image with such
resources.

Important thing is that you can easily specify the various sizes that you want
to generate for the profile image and all those sizes will be generated and
saved on S3 automatically.

Example Code
============

Let's say you have User document and you want each user to have a profile image. You'll do something like this:

```
from mongonengine import *
from rimage.models import Image, ResourceWithImage

class User( Document, ResourceWithImage):
    ... # Various user document fields

    original_image = EmbeddedDocumentField( Image)  # Original image goes here.
    display_image = EmbeddedDocumentField( Image)   # Generated image that you want to use for display
    thumbnail_image = EmbeddedDocumentField( Image)   # Generated thumbnail that you want to use

    @property
    def thumbnail_details( self):
        """It's a hashtable of thumbnail field names and the dimensions. When
        an image is set for this object, this table will be scanned and
        thumbnails specified here will be generated for the given dimensions.
        """
        return { "display_image": { 'w': 180 }, "thumbnail_image": { "w": 50, "h": 50 } }
```

Now, in your code elsewhere, you can do the following to associate an image with this user's profile.

```
# Set user's image from image data.
user.set_resource_image( filelikeobj)

# Or set user's image from a url.
user.set_resource_image_from_url( url)

# Now save the user object.
user.save()
```

Once you do this, original_image, display_image and thumbnail_image will get populated automatically.

Configuration
=============

This is how you can configure this module.

```
from rimage.config import update_config as update_rimage_config

update_rimage_config( {"AWS_ID": "<your aws id>", "AWS_SECRET": "<your aws secret>"})
```

For all the configuration options, please look at rimage.config
