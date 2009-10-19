import sys
import random

class dummybackend:
	
	def __init__( self ):
		print >>sys.stderr, "[DEBUG] dummybackend/init()"

	def load_albums( self ):
		print >>sys.stderr, "[DEBUG] dummybackend/loadalbums()"
		results = [
			{
				"id": album,
				"album": "Album Number %d" % album,
				"artist": "Artist #%d" % album,
				"various": int( round( random.random() - 0.4 ) ),
				"image": "images/nocover" + str( int( round( random.random() * 5 ) + 1 ) ) + ".png"
			}
			for album in range( 1, 100 )
		]
		return results

	def play_album( self, album ):
		print "play %s" % album.album_name

	def get_album_tracklist( self, album ):
		print "get tracks for %s" % album.album_name
		result = [ ( str( track ), "Track %d %d" % ( int( album.album_id ), track ) ) for track in range( 1, int( random.random() * 20 ) ) ]
		return result

_noisy_backend_class = dummybackend

