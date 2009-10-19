import sys, MySQLdb, re, random, pygame
import psyco
import commands
import os
import shutil
#import pycop
import pydcop
import urllib
import time

from Opioid2D import *

psyco.full()

size = width, height = 640, 480

#class AlbumSprite( gui.GUISprite ):
class AlbumSprite( Sprite ):
	w = 0
	def __init__( self, img ):
		try:
			imsurf = pygame.image.load( img );
		except pygame.error:
			imsurf = pygame.image.load( "small_missing.png" )
		imsurf = pygame.transform.scale( imsurf, ( 64, 64 ) )
		#gui.GUISprite.__init__( self, imsurf )
		Sprite.__init__( self, imsurf )
		# store initial w
		self.w = self.rect.w
		
	def on_enter( self ):
		self.do(
			AlphaFade( 1, secs = 0.05 )
			+ ScaleTo( 45 / float( self.w ), secs = 0.05 )
		)

	def on_exit( self ):
		self.do(
			AlphaFade( 0.5, secs = 0.05 )
			+ ScaleTo( 40 / float( self.w ), secs = 0.05 )
		)

	def ping( self ):
		self.do(
			ScaleTo( 45 / float( self.w ), secs = 0.05 )
			+ ScaleTo( 40 / float( self.w ), secs = 0.05 )
		)
	
	def hilight( self ):
		self.do(
			AlphaFade( 1, secs = 0.05 )
		)

	def lolight( self ):
		self.do(
			AlphaFade( 0.5, secs = 0.05 )
		)


	def contains( self, p ):
		#if p[0] > self.x and p[1] > self.y and p[0] < self.x + self.w and p[1] < self.y + self.h:
		if self.rect.collidepoint( p[0], p[1] ):
			return True

		return False
	

class Album:
	def __init__( self, row ):
		repstr = "^\."
		no_image_file = "small_missing.png"
		if row[ 0 ] and row[ 1 ]:
			self.image_file = row[ 0 ] + re.sub( repstr, "", row[ 1 ] )
		else:
			self.image_file = no_image_file
	
		try:
			self.sprite = AlbumSprite( self.image_file )
		except IOError:
			self.image_file = no_image_file
			self.sprite = AlbumSprite( self.image_file )

		self.album_name = row[ 2 ]
		self.album_id = row[ 3 ]
		self.artist_name = row[ 4 ]
	

		
class BrowserScene( Scene ):
	layers = [ "main" ]
	current_album_sprite = None
	db = None
	amarok = pydcop.anyAppCalled( "amarok" )

	def handle_mousebuttondown( self, ev ):
		#self.albums[0].sprite.do( MoveTo( ev.pos, secs = 0.2 ) )
		for album in self.albums:
			if album.sprite.contains( ev.pos ):
				album.sprite.ping()
				#print album.album_name
				#print album.album_id
				self.play_album( album )

	def handle_mousemotion( self, ev ):
		#self.albums[0].sprite.do( MoveTo( ev.pos, secs = 0.2 ) )
		if self.current_album_sprite == None:
			cc = 0
			for album in self.albums:
				#if cc > 20:
				#	break
					
				cc += 1
				if album.sprite.contains( ev.pos ):
					self.current_album_sprite = album.sprite
					self.current_album_sprite.hilight()
		else:
			if not self.current_album_sprite.contains( ev.pos ):
				self.current_album_sprite.lolight()
				self.current_album_sprite = None

	def load_albums( self ):
		self.db = MySQLdb.connect( host = "localhost", user = "amarok", db = "amarok" )
		cursor = self.db.cursor()
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
		"""
		#LIMIT 20
		cursor.execute( sql )
		results = cursor.fetchall()
		print "Found the following albums:"
		for row in results:
			self.albums.append( Album( row ) )
			print "  * " + row[ 2 ]
		

	def enter( self ):
		self.albums = []
		self.load_albums()
		cur_x = 50
		cur_y = 50
		cc = 0
		for album in self.albums:
			album.sprite.set(
				position = ( width / 2, height / 2 ),
				scale = 40 / float( album.sprite.w ), 
				rotation = 0,
				alpha = 0.5,
				layer = "main"
			)
			initial_action = MoveTo( ( cur_x, cur_y ), secs = 0.5 )
			initial_action.smooth( 0.2, 0.2 )
			album.sprite.do( initial_action )

			cur_x += 50
			if cur_x >= width - 100:
				cur_x = 50
				cur_y += 50

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
			LIMIT 30
		""" % { "a": album.album_id }
		cursor.execute( sql )
		results = cursor.fetchall()
		list = ""
		for row in results:
			if row[ 0 ] and row[ 1 ]:
				list = "file://" + urllib.quote( row[ 0 ] + re.sub( repstr, "", row[ 1 ] ) )
			
		#commands.getoutput('''dcop amarok playlist addMedia "''' + list + '''" ''')
		self.amarok.playlist.clearPlaylist()
		self.amarok.playlist.addMedia( list )
		time.sleep( 1 )
		self.amarok.playlist.playByIndex( 0 )

Display.init( size )
Director.run( BrowserScene )
