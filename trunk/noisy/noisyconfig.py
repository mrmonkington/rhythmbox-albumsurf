import random

class Configuration:

	cover_pixel_size = 128
	cover_width = 128
	cover_margin = 16
	cover_step = cover_width + cover_margin

	no_image_files = [
        "images/nocover1.png",
        "images/nocover2.png",
        "images/nocover3.png",
        "images/nocover4.png",
        "images/nocover5.png",
        "images/nocover6.png",
    ]

	def get_no_image_file( self ):
		return self.no_image_files[ int( random.random() * len( self.no_image_files ) ) ]
