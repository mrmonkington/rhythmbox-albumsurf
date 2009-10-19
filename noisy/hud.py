import sys

import clutter
import gtk
import math
import noisyconfig
import re

from layout import Layout

from dummybackend import dummybackend

# global config to avoid messy config passing
config = False

class Controls( clutter.Group ):
    """
        Manager for stop/start buttons, etc
        TODO: add signals and handlers
    """

    buttons = {}

    def __init__( self ):
        global config
        try:
            clutter.Group.__init__( self )

            imgMap = (
                ( "play", "images/play.png" ),
                ( "pause", "images/pause.png" ),
                ( "stop", "images/stop.png" ),
                ( "next", "images/forward.png" ),
                ( "previous", "images/back.png" )
            )

            x_pos = 0
            for ( button_name, image_filename ) in imgMap:
                pixbuf = gtk.gdk.pixbuf_new_from_file( config.root_path + "/" + image_filename )
                pixbuf = pixbuf.scale_simple(
                    config.cover_pixel_size,
                    config.cover_pixel_size,
                    gtk.gdk.INTERP_HYPER
                )
                self.buttons[ button_name ] = clutter.Texture( pixbuf )
                self.add( self.buttons[ button_name ] )
                self.buttons[ button_name ].set_position( x_pos, 0 )
                self.buttons[ button_name ].show()
                x_pos += config.cover_pixel_size

        except Exception, e:
            print "(Can't find controls): " + str( e )
            sys.exit( 1 )

class Tracklist( clutter.Group ):
    """
    Rendering helper for formatting the playlist.
    TODO: find an easier way of doing this since it's a maintenance headache
    """

    labels = []
    max_height = 0
    track_width = 100
    num_width = 22
    gutter = 3
    margin = 6
    line_height = 10
    line_spacing = 5

    def resize( self, max_height ):
        self.max_height = max_height

    def __init__( self, max_height ):
        clutter.Group.__init__( self )
        self.max_height = max_height

    def clearTracks( self ):
        for label in self.labels:
            self.remove( label )

    def setTracks( self, tracks ):
        self.clearTracks()
        self.labels = [ self.createTrackLabel( track ) for track in tracks ]
        y = 0
        x = 0
        for label in self.labels:
            self.add( label )
            label.set_position( x, y )
            label.show()
            y += label.get_height() + self.line_spacing
            if y > self.max_height:
                y = 0
                x += self.track_width + self.num_width + self.gutter + self.margin
        if y > 0:
            self.set_width( x + self.track_width + self.num_width + self.gutter + self.margin )
        else:
            self.set_width( x )
        self.set_anchor_point_from_gravity( clutter.GRAVITY_NORTH_EAST )

    def createTrackLabel( self, track ):
        track_group = clutter.Group()
        num_label = clutter.Text()
        track_label = clutter.Text()
        track_label.set_text( track[ 1 ] )
        num_label.set_text( track[ 0 ] + "." )

        for t in track_label, num_label:
            t.set_font_name( "sans 11px" )
            t.set_color( clutter.Color( 0xff, 0xff, 0xff, 0xff ) )
            t.set_line_wrap( True )
            t.set_line_alignment( "left" )
            t.set_width( self.track_width )

        track_group.add( track_label )
        track_label.set_position( self.num_width + self.gutter, 0 )
        track_label.show()
        track_group.add( num_label )
        num_label.set_position( 0, 0 )
        num_label.show()
        track_group.set_height( track_label.get_height() )

        return track_group


class Hud( clutter.Group ):
    layout = None

    album_title_label = None
    album_artist_label = None
    album_cover_art = None

    now_playing_cover_art = None
    now_playing_artist_label = None
    now_playing_title_label = None

    labels = {}
    label_defs = (
        {
            "name": "album",
            "font": "Sans Bold 15px",
            "default": "Album",
            "colour": clutter.Color( 0xff, 0xff, 0xff, 0xff ),
            "position": ( 500, 300 ),
            "width": 200,
            "anchor": clutter.GRAVITY_NORTH_EAST,
            "align": "right"
        },
        {
            "name": "artist",
            "font": "Sans 15px",
            "default": "Artist",
            "colour": clutter.Color( 0xff, 0xff, 0xff, 0xff ),
            "position": ( 300, 300 ),
            "width": 200,
            "anchor": clutter.GRAVITY_NORTH_EAST,
            "align": "right"
        },
        {
            "name": "now_playing_album",
            "font": "sans Bold 11px",
            "default": "Now playing album",
            "colour": clutter.Color( 0xff, 0xff, 0xff, 0xff ),
            "position": ( 300, 200 ),
            "width": 200,
            "anchor": clutter.GRAVITY_NORTH_EAST,
            "align": "right"
        },
        {
            "name": "now_playing_artist",
            "font": "sans 11px",
            "default": "Now playing artist",
            "colour": clutter.Color( 0xff, 0xff, 0xff, 0xff ),
            "position": ( 400, 200 ),
            "width": 200,
            "anchor": clutter.GRAVITY_NORTH_EAST,
            "align": "right"
        }
    )

    controls = None

    album_tracks = None
    now_playing_tracks = None

    hud_bg = None

    target_w = 0
    target_h = 0
    mode = "chooser"

    player = None

    def resize( self, parent_w, parent_h ):
        init_w = int( parent_w * self.layout.hud.w )
        init_h = int( parent_h * self.layout.hud.h )
        self.set_size( init_w, init_h )
        self.target_w = init_w
        self.target_h = init_h
        #for l in self.labels:
        #    l.
        self.hud_bg.set_size( self.target_w, int( self.target_h * self.layout.hud.strip_h ) )
        self.album_tracks.set_position( init_w - 168, 10 )
        self.album_tracks.resize( int( init_h * self.layout.hud.strip_h ) - 60 )
        self.controls.set_position(
            init_w - int( 0.4 * self.controls.get_width() ) - 40,
            init_h - int( 0.4 * self.controls.get_height() ) - 10
        )
        self.album_cover_art.set_position( init_w - self.album_cover_art.get_width() - 40, 10 )

    def __init__( self, parent_w, parent_h, layout, passed_config ):
        global config
        config = passed_config

        self.layout = layout

        init_w = int( parent_w * self.layout.hud.w )
        init_h = int( parent_h * self.layout.hud.h )

        clutter.Group.__init__( self )
        self.player = dummybackend()
        self.set_size( init_w, init_h )
        self.target_w = init_w
        self.target_h = init_h

        # TODO: tidy this all up with some 'with' style blocks

        # background colouration
        #pixbuf = gtk.gdk.pixbuf_new_from_file( "images/slip.png" )
        self.hud_bg = clutter.Texture( config.root_path + "/" + "images/slip.png" )
        self.hud_bg.set_size( self.target_w, int( self.target_h * self.layout.hud.strip_h ) )
        self.hud_bg.set_position( 0, 0 )
        self.add( self.hud_bg )
        self.hud_bg.hide()

        for ld in self.label_defs:
            l = clutter.Text()
            l.set_font_name( ld[ "font" ] )
            l.set_text( ld[ "default" ] )
            l.set_color( ld[ "colour" ] )
            l.set_position( ld[ "position" ][ 0 ], ld[ "position" ][ 1 ] )
            l.set_width( ld[ "width" ] )
            l.set_anchor_point_from_gravity( ld[ "anchor" ] )
            l.set_line_alignment( ld[ "align" ] )
            self.labels[ ld[ "name" ] ] = l
            self.add( l )
            l.hide()
            
        self.album_tracks = Tracklist( int( init_h * self.layout.hud.strip_h ) - 60 )
        self.album_tracks.set_position( init_w - 168, 10 )
        self.add( self.album_tracks )

        self.now_playing_tracks = Tracklist( int( init_h * self.layout.hud.strip_h ) - 60 )
        self.now_playing_tracks.set_position( init_w - 168, 200 )
        self.add( self.now_playing_tracks )
        #self.now_playing_tracks.show()

        self.controls = Controls()
        self.controls.set_scale( 0.4, 0.4 )
        self.controls.set_position(
            init_w - int( 0.4 * self.controls.get_width() ) - 40,
            init_h - int( 0.4 * self.controls.get_height() ) - 10
        )
        self.add( self.controls )
        self.controls.show()

        self.album_cover_art = clutter.Texture()
        self.album_cover_art.set_size( 128, 128 )
        self.album_cover_art.set_position( init_w - self.album_cover_art.get_width() - 40, 10 )
        self.add( self.album_cover_art )

    def play_handler( self, album ):
        tracks = self.player.get_album_tracklist( album )
        self.labels[ "now_playing_album" ].set_text( album.album_name )
        self.labels[ "now_playing_artist" ].set_text( album.artist_name )
        self.labels[ "now_playing_album" ].show()
        self.labels[ "now_playing_artist" ].show()
        self.now_playing_tracks.setTracks( tracks )
        self.now_playing_tracks.show()

    def album_hover_handler( self, album ):
        tracks = self.player.get_album_tracklist( album )
        self.labels[ "album" ].set_text( album.album_name )
        self.labels[ "artist" ].set_text( album.artist_name )

        self.labels[ "artist" ].set_position( self.target_w - 40, 148 )
        self.labels[ "artist" ].set_anchor_point_from_gravity( clutter.GRAVITY_NORTH_EAST )
        self.labels[ "album" ].set_position( self.target_w - 40 - 128, 148 )
        self.labels[ "album" ].set_anchor_point_from_gravity( clutter.GRAVITY_NORTH_EAST )

        self.labels[ "album" ].show()
        self.labels[ "artist" ].show()

        self.album_tracks.setTracks( tracks )
        self.album_tracks.show()
        self.album_cover_art.set_cogl_texture( album.get_cogl_texture() )
        self.album_cover_art.show()

        self.hud_bg.show()

    def album_clear_handler( self, album ):
        self.album_tracks.hide()
        self.album_cover_art.hide()
        self.labels[ "album" ].hide()
        self.labels[ "artist" ].hide()

        #self.hud_bg.hide()
