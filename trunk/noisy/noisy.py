import sys
import inspect
import thread

import re
import random
import commands
import os
import shutil

# rendering
import cluttergtk
import clutter
import gtk
import math

# optimisation
#import psyco

# this package
from noisyconfig import *
from hud import *
from albumview import *
from dummybackend import *

from layout import Layout

# global configuration (save nightmare config passing)
config = False

class Noisy():
    """
    The app!
    """

    def __init__( self, root_path ):
        global config
        config = Configuration()
        config.root_path = root_path
        pass

    def shortcuts( self, stage, event ):
        if event.keyval == clutter.keysyms.Escape:
            clutter.main_quit()
        

    def resize( self, w, h ):
        self.albumList.target_view_w = w
        self.albumList.target_view_w = h
        self.albumList.setup_albums()
        print w
        print self.albumList.get_width()
        self.bg.set_size( w + 4, h + 4 )
        self.bg.set_position( -2, -2 )
        self.hud.set_position( 0, int( h * Layout.surfMode.hud.t ) )
        self.hud.resize( w, h )

    def run( self, stage ):
        global config
        #stage = clutter.Stage()
        player = dummybackend()

        stage.set_reactive( True )
        stage.connect( "key-press-event", self.shortcuts )

        # initialise the stage (window)
        stage.set_color(clutter.Color( 0x20, 0x20, 0x20, 0xff ) )

        # set up background (just an image of gradient)
        pixbuf = gtk.gdk.pixbuf_new_from_file( "%s/images/bg.png" % config.root_path )
        self.bg = clutter.Texture()
        self.bg.set_from_rgb_data(
            pixbuf.get_pixels(),
            pixbuf.props.has_alpha,
            pixbuf.props.width,
            pixbuf.props.height,
            pixbuf.props.rowstride,
            4,
            0
        )
        self.bg.set_size( stage.get_width() + 4, stage.get_height() + 4 )
        self.bg.set_position( -2, -2 )
        stage.add( self.bg )
        self.bg.show()

        # create album scrolling list thing
        # Layout namespace has some config vars
        self.albumList = AlbumView(
            int( stage.get_width() * Layout.surfMode.albumViewer.w ),
            int( stage.get_height() * Layout.surfMode.albumViewer.w ),
            config,
            listen_on = stage
        )
        # stick it in a wrapper for some device size independence?
        albumWrapper = clutter.Group()
        albumWrapper.add( self.albumList )
        albumWrapper.set_scale( 1, 1 )    
        albumWrapper.set_position( 128, 0 )
        albumWrapper.show()
        self.albumList.show()
        #albumList.set_reactive( True )

        stage.add( albumWrapper )

        # set up the overlay (album info, text, buttons - all non 3D stuff)
        self.hud = Hud(
            stage.get_width(),
            stage.get_height(),
            Layout.surfMode,
            config
        )
        self.hud.set_position( 0, int( stage.get_height() * Layout.surfMode.hud.t ) )
        stage.add( self.hud )

        #connect albumview to hud
        self.albumList.set_listener( self.hud )
        #or
        #connect hud.item.onBlah = player.blah

        #timeline = clutter.Timeline( 60, 60 )
        #timeline.set_loop( True )

        stage.show_all()
        #timeline.start()
        #clutter.threads_init()
        #clutter.main()

        #return 0

# scratchpad
#( fovy, aspect, z_near, z_far ) = stage.get_perspective()
#print ( fovy, aspect, z_near, z_far )
#stage.set_perspective( 60.0, 1.0, 0.08, 70.0 )

#    def on_new_frame (self, tl, frame_num):
#        self.set_rotation (clutter.Z_AXIS,
#            frame_num,
#            self.stage.get_width() / 2,
#            self.stage.get_height () / 2,
#            0)
#      
#        angle = frame_num * -2
#
#        for i in range(self.n_hands):
#            hand = self.get_nth_child(i)
#            hand.set_rotation(clutter.Z_AXIS,
#                angle, 
#                hand.get_width() / 2,
#                hand.get_height() / 2,
#                0)
