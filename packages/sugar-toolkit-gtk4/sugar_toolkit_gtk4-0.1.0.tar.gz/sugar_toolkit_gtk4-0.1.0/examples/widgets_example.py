#!/usr/bin/env python3
"""
Sugar GTK4 Text Editor Activity Example using Sugar widgets and the real Activity class.
"""

import os
import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk

# Add src to path for sugar widgets and activity
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from sugar.activity.activity import Activity
from sugar.activity.widgets import ActivityButton, EditToolbar, TitleEntry, DescriptionItem, StopButton, ShareButton


class SugarTextEditorActivity(Activity):
    @property
    def metadata(self):
        return self._metadata

    def __init__(self, application=None):
        super().__init__(application=application)
        self.set_title("Sugar Text Editor")
        self._metadata['icon-color'] = '#FF0000,#00FF00'
        self._metadata['description'] = ''
        self._metadata['icon-name'] = 'view-list'  # Use a valid icon name
        self._create_ui()

    def _create_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(12)
        main_box.set_margin_end(12)
        self.set_canvas(main_box)

        # Modern GTK4 background: use set_css_classes
        main_box.set_css_classes(["background"])
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b".background { background-color: #e0e0e0; }")
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Activity header with Sugar ActivityButton, pass icon_name
        activity_btn = ActivityButton(self, icon_name=self._metadata['icon-name'])
        main_box.append(activity_btn)

        # Title entry for renaming document/activity
        title_entry = TitleEntry(self)
        title_entry.connect('enter-key-press', self.on_title_changed)
        main_box.append(title_entry)

        # Description item for notes
        desc_item = DescriptionItem(self)
        desc_item.connect('clicked', self.on_description_clicked)
        main_box.append(desc_item)

        # EditToolbar for Undo/Redo/Copy/Paste
        toolbar = EditToolbar()
        toolbar.undo.connect('clicked', self.on_undo_clicked)
        toolbar.redo.connect('clicked', self.on_redo_clicked)
        toolbar.copy.connect('clicked', self.on_copy_clicked)
        toolbar.paste.connect('clicked', self.on_paste_clicked)
        # Add Open/Save as extra buttons
        open_btn = Gtk.Button(label="Open")
        open_btn.connect('clicked', self.on_open_clicked)
        save_btn = Gtk.Button(label="Save")
        save_btn.connect('clicked', self.on_save_clicked)
        toolbar.append(open_btn)
        toolbar.append(save_btn)
        main_box.append(toolbar)

        # Text area
        self.text_buffer = Gtk.TextBuffer()
        self.text_view = Gtk.TextView(buffer=self.text_buffer)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.set_vexpand(True)
        main_box.append(self.text_view)

        # Share and Stop buttons
        share_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        share_btn = ShareButton(self)
        share_btn.connect('clicked', self.on_share_clicked)
        stop_btn = StopButton(self)
        stop_btn.connect('clicked', self.on_stop_clicked)
        share_box.append(share_btn)
        share_box.append(stop_btn)
        main_box.append(share_box)

        # Status label
        self.status_label = Gtk.Label(label="Ready")
        main_box.append(self.status_label)

    def on_title_changed(self, widget):
        title = widget.get_text()
        self.set_title(title)
        self.status_label.set_text(f"Title set to: {title}")

    def on_description_clicked(self, widget):
        # For demo, just set a static description
        self._metadata['description'] = "Document notes updated."
        self.status_label.set_text("Description updated.")

    def on_undo_clicked(self, button):
        self.status_label.set_text("Undo (not implemented)")

    def on_redo_clicked(self, button):
        self.status_label.set_text("Redo (not implemented)")

    def on_copy_clicked(self, button):
        bounds = self.text_buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
            text = self.text_buffer.get_text(start, end, True)
            clipboard = Gtk.Clipboard.get_default(Gdk.Display.get_default())
            provider = Gdk.ContentProvider.new_for_value(text)
            clipboard.set_content(provider)
            self.status_label.set_text("Copied")
        else:
            self.status_label.set_text("No selection to copy")

    def on_paste_clicked(self, button):
        clipboard = Gtk.Clipboard.get_default(Gdk.Display.get_default())
        def on_text_received(clipboard, text):
            if text:
                self.text_buffer.insert_at_cursor(text)
            self.status_label.set_text("Pasted")
        clipboard.read_text_async(None, on_text_received)

    def on_save_clicked(self, button):
        dialog = Gtk.FileChooserDialog(title="Save File", action=Gtk.FileChooserAction.SAVE)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.ACCEPT)

        def response_handler(dlg, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dlg.get_file()
                if file:
                    filename = file.get_path()
                    start_iter = self.text_buffer.get_start_iter()
                    end_iter = self.text_buffer.get_end_iter()
                    text = self.text_buffer.get_text(start_iter, end_iter, True)
                    with open(filename, 'w') as f:
                        f.write(text)
                    self.status_label.set_text(f"Saved to {filename}")
            dlg.destroy()

        dialog.connect("response", response_handler)
        dialog.show()

    def on_open_clicked(self, button):
        dialog = Gtk.FileChooserDialog(title="Open File", action=Gtk.FileChooserAction.OPEN)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Open", Gtk.ResponseType.ACCEPT)

        def response_handler(dlg, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dlg.get_file()
                if file:
                    filename = file.get_path()
                    with open(filename, 'r') as f:
                        text = f.read()
                    self.text_buffer.set_text(text)
                    self.status_label.set_text(f"Opened {filename}")
            dlg.destroy()

        dialog.connect("response", response_handler)
        dialog.show()

    def on_share_clicked(self, button):
        self.share()
        self.status_label.set_text("Shared (mock)")

    def on_stop_clicked(self, button):
        self.close()
        self.status_label.set_text("Stopped (mock)")


class SugarTextEditorApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='org.sugarlabs.SugarTextEditor')

    def do_activate(self):
        window = SugarTextEditorActivity(application=self)
        window.present()

def main():
    app = SugarTextEditorApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())

# Example for icon usage in Sugar widgets:
# If you use ToolButton or similar, use icon_name="view-list" (not a file path)
# If you want a fallback, use icon_name="document-generic"