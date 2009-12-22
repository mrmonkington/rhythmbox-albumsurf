import rb
import gtk
import gobject
import cluttergtk, clutter
import os.path

from albumsurf.noisy.noisy import Noisy

ui_str = \
"""<ui>
  <toolbar name="ToolBar">
    <placeholder name="ToolBarPluginPlaceholder">
      <toolitem name="AlbumSurf" action="ToggleAlbumSurf"/>
    </placeholder>
  </toolbar>
</ui>"""

class AlbumSurf( rb.Plugin ):

    def __init__(self):
        rb.Plugin.__init__(self)
        
    def activate(self, shell):
        data = {}
        manager = shell.get_player().get_property("ui-manager")
        self.player = shell.get_player()
        self.shell = shell
        
        icon_file_name = self.find_file("albumsurf-icon.svg")
        root_path = os.path.dirname( icon_file_name ) + "/noisy"
        iconsource = gtk.IconSource()
        iconsource.set_filename(icon_file_name)
        iconset = gtk.IconSet()
        iconset.add_source(iconsource)
        iconfactory = gtk.IconFactory()
        iconfactory.add("albumsurf", iconset)
        iconfactory.add_default()
        action = gtk.Action("ToggleAlbumSurf", "Album Surf",
                            "Album Surf",
                            "albumsurf");
        action.connect("activate", self.show_albumsurf, shell)
        
        data['action_group'] = gtk.ActionGroup('AlbumSurfPluginActions')
        data['action_group'].add_action(action)
        manager.insert_action_group(data['action_group'], 0)
        data['ui_id'] = manager.add_ui_from_string(ui_str)
        manager.ensure_update()
        shell.set_data('AlbumSurfPluginInfo', data)

        self.noisy = Noisy( root_path )


    def deactivate(self, shell):
        data = shell.get_data('AlbumSurfPluginInfo')
        manager = shell.get_player().get_property('ui-manager')
        manager.remove_ui(data['ui_id'])
        manager.remove_action_group(data['action_group'])
        manager.ensure_update()
        
    # don't know any other way to get reliable stage size
    def on_stage_allocate (self, actor, pspec, stage):
        print "allocate"
        (stage_w, stage_h) = actor.get_size()
        print (stage_w, stage_h)
        stage.set_size( stage_w, stage_h )
        self.noisy.resize( stage_w, stage_h )

    def show_albumsurf(self, event, shell):
        vbox = gtk.VBox(False, 6)
        shell.add_widget(vbox, rb.SHELL_UI_LOCATION_MAIN_NOTEBOOK)

        self.embed = cluttergtk.Embed()
        stage = self.embed.get_stage()
        #self.embed.set_size_request( 200, 200 )
        stage.set_color(clutter.Color( 0x20, 0x20, 0x20, 0xff ) )
        vbox.pack_start(self.embed, True, True, 0)
        
        self.embed.realize()
        vbox.show_all()
        #size = vbox.size_request()
        #print size
        #stage.set_size( ) )
        stage.show_all()
        shell.notebook_set_page( vbox )
        self.noisy.run( self.embed.get_stage() )
        stage.connect('notify::allocation', self.on_stage_allocate, stage)

    def hide_albumsurf(self, event, shell):
        shell.notebook_set_page( None )

        #self.player.connect("playing-song-changed", self.reload_playlist)
        #self.player.connect("playing-changed", self.reload_play_pause)

        #db = shell.get_property("db")
        #db.connect_after ("entry-extra-metadata-notify::rb:coverArt", 
        #                  self.notify_metadata)

        # Load current state
        #self.reload_playlist(self.player, self.player.get_playing_entry())

#    def playpause(self):
#        try:
#            self.player.playpause()
#        except:
#            self.play_entry(0)
#        
#    def play_entry(self, index):
#        if len(self.tracks) > index:
#            self.player.play_entry(self.tracks[index]["entry"])
#
#    def reload_play_pause(self, player, playing):
#        if playing:
#            elapsed = player.get_playing_time()
#            self.window.track_widgets[0].paused=False
#            self.window.track_widgets[0].start_progress_bar(elapsed)
#            self.window.current_info = "Now playing..."
#            self.window.track_infos[0] = FullscreenWindow.INFO_STATUS_PAUSE
#        else:
#            self.window.track_widgets[0].paused=True
#            self.window.current_info = FullscreenWindow.INFO_STATUS_IDLE
#            self.window.track_infos[0] = FullscreenWindow.INFO_STATUS_PLAY
#
#    def get_entries(self, player, entry, cnt):
#        """Gets the next entries to be played from both active source and queue
#        
#        Uses each source's query-model.
#        player = player to use
#        entry = entry to start from (as a kind of offset)
#        cnt = number of entries to return
#        """
#
#        if not entry:
#            return []
#
#        entries = [entry]
#        
#        queue = player.get_property("queue-source")
#        if queue:
#            querymodel = queue.get_property("query-model")
#            l = querymodel.get_next_from_entry(entry)
#            while l and len(entries) <= cnt:
#                entries.append(l)
#                l = querymodel.get_next_from_entry(l)
#        source = player.get_property("source")
#        if source:
#            querymodel = source.get_property("query-model")
#            l = querymodel.get_next_from_entry(entry)
#            while l and len(entries) <= cnt:
#                entries.append(l)
#                l = querymodel.get_next_from_entry(l)
#
#        return entries
#
#    def get_track_info(self, entry):
#        import rhythmdb
#        db = self.shell.get_property ("db")
#        artist = db.entry_get(entry, rhythmdb.PROP_ARTIST)
#        album = db.entry_get(entry, rhythmdb.PROP_ALBUM)
#        title = db.entry_get(entry, rhythmdb.PROP_TITLE)
#        duration = db.entry_get(entry, rhythmdb.PROP_DURATION)
#        track = {"artist":artist,
#                 "album":album,
#                 "title":title,
#                 "duration":duration,
#                 "entry":entry}
#        return track
#    
#    def notify_metadata(self, db, entry, field=None,metadata=None):
#        """Subscribe to metadata changes from database"""
#        if entry == self.shell.get_player().get_playing_entry():
#            self.set_cover_art(entry)
#    
#    def set_cover_art(self, entry):
#        if entry:
#            db = self.shell.get_property("db")
#            cover_art = db.entry_request_extra_metadata(entry, "rb:coverArt")
#            self.window.set_artwork(cover_art)
#        
#    
#    def reload_playlist(self, player, entry):
#
#        db = self.shell.get_property ("db")
#        
#        # If nothing is playing then use current play order
#        # to move to the next track.
#        if not entry:
#            try:
#                playorder = player.get_property("play-order-instance")
#                entry = playorder.get_next()
#            except:
#                print "play-order-instance not available"
#                return
#        
#        # Set cover art
#        self.set_cover_art(entry)
#        
#        entries = self.get_entries(player, entry, 20)
#        self.tracks = []
#        
#        for entry in entries:
#            self.tracks.append(self.get_track_info(entry))
#        
#        self.window.set_tracks(self.tracks)
#        try:
#            elapsed = player.get_playing_time()
#        except:
#            elapsed = 0.0
#
#        if player.get_playing():
#            self.window.track_widgets[0].start_progress_bar(elapsed)
#            self.window.current_info = "Now playing..." # TODO
#        else:
#            self.window.track_widgets[0].set_elapsed(elapsed)
#            self.window.current_info = FullscreenWindow.INFO_STATUS_IDLE
#        
#        self.window.show_info()

