import sys
import MySQLdb

import thread
import re
import time

# for controlling amarok
import pydcop
import urllib

#import noisyconfig

config = False

class amarok:
	
	db = None
	amarokapp = None

	def __init__( self, passed_config ):
		global config
		self.amarokapp = pydcop.anyAppCalled( "amarok" )
		self.db = MySQLdb.connect( host = "localhost", user = "amarok", db = "amarok", passwd = "amarok" )
		config = passed_config

	def load_albums( self ):
		cursor = self.db.cursor()
		sql = """
			SELECT
				devices.lastmountpoint,
				images.path,
				album.name,
				album.id,
				artist.name,
				tags.sampler
			FROM
				album
				INNER JOIN
					tags
					ON tags.album = album.id
				INNER JOIN
					artist
					ON tags.artist = artist.id
				LEFT JOIN
					images
					ON album.name = images.album
				LEFT JOIN
					devices
					ON images.deviceid = devices.id
			WHERE album.name != ""
			GROUP BY album.id
			ORDER BY artist.name
		"""
		cursor.execute( sql )
		results = cursor.fetchall()
		repstr = "^\."
		albums = []
		for row in results:
			if row[ 0 ] and row[ 1 ]:
				# it's on a different disk
				image_file = row[ 0 ] + re.sub( repstr, "", row[ 1 ] )
			elif row[ 1 ]:
				# common case
				image_file = re.sub( repstr, "", row[ 1 ] )
			else:
				image_file = ""

			albums.append(
				{
					"id": row[ 3 ],
					"album": row[ 2 ],
					"artist": row[ 4 ],
					"various": row[ 5 ],
					"image": image_file
				}
			)

		return albums

	def play_album( self, album ):
		repstr = "^\."
		cursor = self.db.cursor()
		sql = """
			SELECT
				devices.lastmountpoint,
				tags.url
			FROM
				tags
				INNER JOIN
					devices
					ON tags.deviceid = devices.id
			WHERE tags.album = %(a)d
			ORDER BY tags.track
		""" % { "a": album.album_id }
		cursor.execute( sql )
		results = cursor.fetchall()
		list = []
		for row in results:
			if row[ 0 ] and row[ 1 ]:
				list.append( "file://" + urllib.quote( row[ 0 ] + re.sub( repstr, "", row[ 1 ] ) ) )
		self.controlAmarok_playList( list )

	def get_album_tracklist( self, album ):
		repstr = "^\."
		cursor = self.db.cursor()
		sql = """
			SELECT
				tags.track,
				tags.title
			FROM
				tags
			WHERE tags.album = %(a)d
			ORDER BY tags.track
		""" % { "a": album.album_id }
		cursor.execute( sql )
		results = cursor.fetchall()
		tracks = [ ( str( res[ 0 ] ), res[ 1 ] ) for res in results ]
		return tracks

	def controlAmarok_playList( self, list ):

		print "playing new album"
		print list
		print "play"
		self.kick_thread = thread.start_new_thread( self.kickAmarok, ( list, ) )

	def kickAmarok( self, list ):
		time.sleep( 0.5 )
		print "clearing playlist"
		self.amarokapp.playlist.clearPlaylist()
		print "adding media"
		for mf in list:
			self.amarokapp.playlist.addMedia( mf )
		time.sleep( 1 )
		print "kick"
		self.amarokapp.playlist.playByIndex( 0 )
		thread.exit()

_noisy_backend_class = amarok

