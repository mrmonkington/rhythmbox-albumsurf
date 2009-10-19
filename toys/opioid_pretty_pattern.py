import sys, MySQLdb, re, random
from Opioid2D import *

print random.randint( 50, 500 )

size = width, height = 640, 480

class Album:
	def __init__( self, row ):
		repstr = "^\."
		no_image_file = "small_missing.png"
		if row[ 0 ] and row[ 1 ]:
			self.image_file = row[ 0 ] + re.sub( repstr, "", row[ 1 ] )
		else:
			self.image_file = no_image_file
	
		try:
			self.sprite = Sprite( self.image_file )
		except IOError:
			self.image_file = no_image_file
			self.sprite = Sprite( self.image_file )

		self.album_name = row[ 2 ]
		self.album_id = row[ 3 ]
		self.artist_name = row[ 4 ]


def load_albums():
	print 'MirraTemplate is starting'
	db = MySQLdb.connect( host="localhost", user="amarok", db="amarok" )
	cursor = db.cursor()
	sql = """
		SELECT
			devices.lastmountpoint,
			images.path,
			album.name,
			album.id,
			images.artist
		FROM
			album
			LEFT JOIN
				images
				ON album.name = images.album
			LEFT JOIN
				devices
				ON images.deviceid = devices.id
		GROUP BY album.name
		limit 2000
	"""
	cursor.execute( sql )
	results = cursor.fetchall()
	albums = []
	print "Found the following albums:"
	for row in results:
		albums.append( Album( row ) )
		print "  * " + row[ 2 ]
	
	return albums
		
class BrowserScene( Scene ):
	layers = [ "main" ]
	def enter( self, albums ):
		self.albums = albums
		for album in self.albums:
			album.sprite.set(
				position = ( 100, 100 ),
				scale = 0.4,
				rotation = 45,
				alpha = 0.5,
				layer = "main"
			)
			album.sprite.do( MoveDelta( ( random.randint( 50, 500 ),  random.randint( 50, 400 ) ), secs = 4 ) )

Display.init( ( 800, 600 ) )
albums = load_albums()
Director.run( BrowserScene, albums )
