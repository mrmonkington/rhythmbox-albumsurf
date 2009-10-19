import sys
import MySQLdb

import thread
import re
import time

# for controlling dbus
# see defs/*.xml for rhythmbox dbus interface definitions
import dbus
import urllib

from lxml import etree

import noisy

class Rhythmbox:
	
	instance = None
	albums = []

	def __init__( self ):
		#self.instance = pydcop.anyAppCalled( "amarok" )
		pass

	def load_albums( self ):
		"""
		<entry type="song">
			<title>B1</title>
			<genre>Electronic</genre>
			<artist>Gescom</artist>
			<album>A1 - D1</album>
			<track-number>3</track-number>
			<duration>474</duration>
			<file-size>11902847</file-size>
			<location>file:///home/mark/Music/Gescom/A1%20-%20D1/03.%20Gescom%20-%20B1.mp3</location>
			<mountpoint>file:///</mountpoint>
			<mtime>1213296825</mtime>
			<date>732677</date>
			<mimetype>application/x-id3</mimetype>
			<mb-trackid></mb-trackid>
			<mb-artistid></mb-artistid>
			<mb-albumid></mb-albumid>
			<mb-albumartistid></mb-albumartistid>
			<mb-artistsortname></mb-artistsortname>
		</entry>
				images.path,
				album.name,
				artist.name
		"""
		self.albums = []
		tree = etree.parse( "/home/mark/.gnome2/rhythmbox/rhythmdb.xml" )
		for entry in tree.getroot().getIterator( "entry" ):
			if entry.get( "type" ) == "song":
				track = {}
				for field in entry:
					album_name, album_artist = "", ""
					print "field: %s   val: %s " % ( field.tag.ljust( 20 ), field.text )
					if field.tag == "album":
						album_name = field.text
					elif field.tag == "artist":
						album_artist = field.text
					elif field.tag == "title":
						track[ "title" ] = field.text
				if album_name != "" and album_artist != "":
					album_key = album_artist + " - " + album_name
					if self.albums.has_key( album_key ):
						self.albums[ album_key ].append( album )
					else:
						self.albums[ album_key ] = {
							"album" : 
							[ track, ]
						}

		albums.sort( cmp = lambda x,y: cmp( x[ "title" ]. y[ "title" ] ) )
		#return results

	def play_album( self, album ):
		print "play"
		repstr = "^\."
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
			LIMIT 50
		""" % { "a": album.album_id }
		if row[ 0 ] and row[ 1 ]:
			list.append( "file://" + urllib.quote( row[ 0 ] + re.sub( repstr, "", row[ 1 ] ) ) )

		self.controlAmarok_playList( list )

	def get_album_tracklist( self, album ):
		print "get tracks"
		repstr = "^\."
		sql = """
			SELECT
				tags.track,
				tags.title
			FROM
				tags
			WHERE tags.album = %(a)d
			ORDER BY tags.track
			LIMIT 50
		""" % { "a": album.album_id }
		return results

	def controlAmarok_playList( self, list ):
		print "playing new album"
		print list
		print "play"
		self.kick_thread = thread.start_new_thread( self.kickAmarok, ( list, ) )

	def kickAmarok( self, list ):
		time.sleep( 0.5 )
		print "clearing playlist"
		#self.instance.playlist.clearPlaylist()
		print "adding media"
		for mf in list:
			#self.instance.playlist.addMedia( mf )
			pass
		time.sleep( 1 )
		print "kick"
		#self.instance.playlist.playByIndex( 0 )
		thread.exit()

if __name__ == '__main__':
	r = Rhythmbox()
	r.load_albums()
