import sys

import clutter
import gtk
import math

import noisyconfig
import re
import random
import time

from dummybackend import *

# global config to avoid messy config passing
config = False

class Album( clutter.Texture ):
    """
    A specialised texture that contains album information and can react to rollover events.  Doesn't handle click events,
    which are handled instead by AlbumView so it can dispatch messages to the media player interface and change views
    """
    image_file = ""
    def __init__( self, row ):
        clutter.Texture.__init__( self )

        if row[ "various" ] == 1:
            self.artist_name = "Various Artists"
        else:
            self.artist_name = row[ "artist" ]

        self.album_name = row[ "album" ]
        self.album_id = row[ "id" ]
        self.image_file = row[ "image" ]

        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file( config.root_path + "/" + self.image_file )
        except Exception, e:
            print >>sys.stderr, "Could not load image " + self.image_file
            print e
            print
            # this is the (rubbish) default image -- TODO we should construct one using album title
            pixbuf = gtk.gdk.pixbuf_new_from_file( config.root_path + "/" + config.get_no_image_file() )
            self.image_file = config.root_path + "/" + config.get_no_image_file()

        # everything same size (to avoid filling up texture mem?)
        pixbuf = pixbuf.scale_simple(
            config.cover_pixel_size,
            config.cover_pixel_size,
            gtk.gdk.INTERP_HYPER
        )

        if pixbuf.props.has_alpha:
            bpp = 4
        else:
            bpp = 3 
        # we can init base class now we have a pixmap
        self.set_from_rgb_data(
            pixbuf.get_pixels(),
            pixbuf.props.has_alpha,
            pixbuf.props.width,
            pixbuf.props.height,
            pixbuf.props.rowstride,
            bpp,
            0
        )
        
        # handle events
        self.set_reactive( True )
        
        # events for rollover
        self.connect( 'enter-event', self.on_enter)
        self.connect( 'leave-event', self.on_exit)

        # want it to rotate about centre
        self.set_anchor_point_from_gravity( clutter.GRAVITY_CENTER )
        self.set_opacity( 0xff )

        # random wobble
        self.set_rotation(
            axis = clutter.Z_AXIS,
            angle = random.gauss( 0, 2 ),
            x = 0,
            y = 3,
            z = 0
        )
        
    def on_enter( self, stage, event ):
        self.set_opacity( 0xff )
        self.set_scale( 1.1, 1.1 )
        return False

    def on_exit( self, stage, event ):
        self.set_opacity( 0xff )
        self.set_scale( 1, 1 )
        return False

    def ping( self ):
        print "ping"
        #self.timeline_in = clutter.Timeline(8, 60)
        #self.alpha_in = clutter.Alpha( self.timeline_in, clutter.sine_half_func ) 
        #self.in_behaviour = clutter.BehaviourScale(
        #    alpha = self.alpha_in,
        #    x_scale_start = 1.1,
        #    y_scale_start = 1.1,
        #    x_scale_end = 1.2,
        #    y_scale_end = 1.2
        #)
        #self.in_behaviour.apply( self )
        #self.timeline_in.start()
        self.animate( clutter.EASE_IN_OUT_BACK, 150, 'scale', 1.2  )
        self.animate( clutter.EASE_IN_OUT_BACK, 150, 'scale', 1.0  )
        return False

class AlbumView( clutter.Group ):
    albums = []
    album_label = None
    now_playing_label = None
    total_height = 0

    player = None

    max_rotation = 20

    target_view_w = 0
    target_view_h = 0

    def __init__( self, init_w, init_h, passed_config, listen_on ):
        global config
        config = passed_config

        self.player = dummybackend()
        clutter.Group.__init__( self )

        self.target_view_w = init_w
        self.target_view_h = init_h
        self.stage_height = init_h

        listen_on.connect( "button-press-event", self.on_button_press )
        listen_on.connect( "key-press-event", self.on_key_press )
        listen_on.connect( "enter-event", self.on_enter )
        listen_on.connect( "leave-event", self.on_exit )
        listen_on.connect( "scroll-event", self.on_scroll )

        #self.scroll_timeline = clutter.Timeline( 200 )
        #self.scroll_effect = clutter.EffectTemplate( self.scroll_timeline, clutter.ramp_inc_func )

        self.load_albums()
        self.setup_albums()
        self.set_rotate( 0 )

    def on_enter( self, stage, event ):
        if isinstance( event.source, Album ):
            #self.album_label.set_text( event.source.album_name  + " by " + event.source.artist_name )
            self.hover_album( event.source )
            pass

        # bubble
        return False

    def on_exit( self, stage, event ):
        if isinstance( event.source, Album ):
            #self.album_label.set_text( "" )
            self.clear_album( event.source )
            pass

        # bubble
        return False



    def load_albums( self ):
        album_data = self.player.load_albums()
        #print "Found the following albums:"
        repstr = "^\."
        for row in album_data:
            #print "  * '" + row[ "album" ] + "' by '" + row[ "artist" ] + "' cover: " + row[ "image" ]
            album = Album( row )
            self.albums.append( album )
            self.add( album );
        return
        
    
    def setup_albums( self ):
        x = config.cover_margin
        y = config.cover_step
        self.total_height = config.cover_step
        for album in self.albums:
            print ( "x", x )
            print self.target_view_w
            album.set_position( int( x ), int( y ) )
            x += config.cover_step

            if x > self.target_view_w:# - config.cover_step:
                x = config.cover_margin
                y += config.cover_step
                self.total_height += config.cover_step

            album.show()

        # 180 for hud
        #self.total_height += config.cover_margin + 180

    def run( self ): 
        self.timeline.start()



    def on_button_press( self, stage, event ):
        if event.button == 1:
            #print event.source
            #album = stage.get_actor_at_pos(event.x, event.y)
            album = event.source
            if isinstance( album, Album ):
                print "Playing new album"
                album.ping()
                self.play_album( album )
            return False

        return False

    def on_key_press( self, stage, event ):
        if event.keyval == gtk.keysyms.Page_Up:
            self.scroll( 200 )
        elif event.keyval == gtk.keysyms.Page_Down:
            self.scroll( -200 )
        elif event.keyval == gtk.keysyms.Up:
            self.scroll( 5 )
        elif event.keyval == gtk.keysyms.Down:
            self.scroll( -5 )
        elif event.keyval == gtk.keysyms.Escape:
            clutter.main_quit()

        return True

    def on_scroll( self, stage, event ):
        y_scroll = 32
        if event.direction == clutter.SCROLL_DOWN:
            y_scroll *= -1
        self.scroll( y_scroll ) 
        return True

    
    target_y = 0
    def scroll( self, pix ):
        new_y = self.target_y + pix
        if new_y > 0:
            new_y = 0
        if new_y < self.stage_height - self.total_height:
            new_y = self.stage_height - self.total_height
        #self.scroll_timeline.stop()
        self.target_y = new_y
#        self.scroll_rotate( new_y )
#        clutter.effect_move(
#            self.scroll_effect,
#            self,
#            self.get_x(),
#            new_y,
#            None,
#            None
        self.set_y( self.target_y )
        self.set_rotate( self.target_y )

    def set_rotate( self, y ):
        self.set_rotation(
            axis = clutter.X_AXIS,
            angle = 2 * self.max_rotation * ( float( y ) / float( self.stage_height - self.total_height ) - 0.5 ),
            x = 0,
            y = int( ( self.total_height ) * y / ( self.stage_height - self.total_height ) ),
            z = 0
        )

    
    def scroll_rotate( self, y ):
        rection = clutter.ROTATE_CW
        if self.target_y < self.get_y():
            #moving down, rotate ccw
            rection = clutter.ROTATE_CCW

        clutter.effect_rotate(
            self.scroll_effect,
            self,
            clutter.X_AXIS,
            2 * self.max_rotation * ( float( y ) / float( self.stage_height - self.total_height ) - 0.5 ),
            ( 0,
            int( ( self.total_height ) * y / ( self.stage_height - self.total_height ) ),
            0 ),
            rection
        )

    # listened actions
    # this is sort of signally I spose
    # probably better ways to do this :(

    listener = None
    def set_listener( self, obj ):
        self.listener = obj

    def play_album( self, album ):
        self.player.play_album( album )
        if self.listener != None:
            if self.listener.play_handler != None:
                self.listener.play_handler( album )

    def hover_album( self, album ):
        if self.listener != None:
            if self.listener.album_hover_handler != None:
                self.listener.album_hover_handler( album )

    def clear_album( self, album ):
        if self.listener != None:
            if self.listener.album_clear_handler != None:
                self.listener.album_clear_handler( album )

