"""Sugar GTK4 Tray and Window Example."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk

from sugar.activity import SimpleActivity
from sugar.graphics.tray import HTray, VTray, TrayButton, TrayIcon
from sugar.graphics.window import Window
from sugar.graphics.xocolor import XoColor


class TrayAndWindowExampleActivity(SimpleActivity):
    """Example activity demonstrating Sugar GTK4 Tray and Window features."""

    def __init__(self):
        super().__init__()
        self.set_title("Sugar GTK4 Tray and Window Example")
        self._create_content()

    def _create_content(self):
        """Create the main content demonstrating tray and window features."""
        # Add CSS for black text and better styling
        css_provider = Gtk.CssProvider()
        css_data = """
        label, button, entry, .button, .label {
            color: #000000;
        }
        frame {
            margin: 10px;
        }
        """
        css_provider.load_from_data(css_data.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Scrolled window for main content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)

        # Title
        title = Gtk.Label()
        title.set_markup("<big><b>Sugar GTK4 Tray and Window Example</b></big>")
        title.set_hexpand(True)
        main_box.append(title)

        # Add tray examples
        self._add_htray_example(main_box)
        self._add_vtray_example(main_box)
        self._add_window_controls(main_box)

        scrolled.set_child(main_box)
        self.set_canvas(scrolled)
        self.set_default_size(900, 700)

    def _add_htray_example(self, container):
        frame = Gtk.Frame(label="Horizontal Tray (HTray)")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)

        info_label = Gtk.Label(label="Horizontal tray with scrolling - add many items to see scroll buttons")
        vbox.append(info_label)

        # Use SVGs from src/sugar/graphics/icons/
        icons_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "src", "sugar", "graphics", "icons"
        )
        svg_files = [
            "checkbox-checked.svg",
            "document-open.svg",
            "go-right.svg",
            "media-playback-pause.svg",
            "media-playback-start.svg",
            "preferences-system.svg",
            "radio-active.svg",
            "system-search.svg",
            "test.svg",
        ]
        # Create HTray with proper sizing
        self.htray = HTray()
        self.htray.set_hexpand(True)
        self.htray.set_vexpand(False)
        self.htray.set_size_request(-1, 120)  # Increased height

        # Add initial items using append (GTK4 method)
            # Add SVG icons as TrayIcon using file_name
        # for i, svg_file in enumerate(svg_files):
            # icon_path = os.path.join(icons_dir, svg_file)
            # icon = TrayIcon(file_name=icon_path, xo_color=XoColor.get_random_color())
            # icon.connect("clicked", self._on_tray_item_clicked, f"SVG Icon {i}")
            # self.htray.append(icon)

            # Add SVG icons as TrayIcon using file_name
        for i, svg_file in enumerate(svg_files):
            icon_path = os.path.join(icons_dir, svg_file)
            icon = TrayIcon(file_name=icon_path, xo_color=XoColor.get_random_color())
            icon.connect("clicked", self._on_tray_item_clicked, f"SVG Icon {i}")
            self.htray.add_item(icon)
        # for i in range(8):  # Reduced initial count for better display
        #     if i % 3 == 0:
        #         icon = TrayIcon(icon_name="applications-graphics", xo_color=XoColor.get_random_color())
        #         icon.connect("clicked", self._on_tray_item_clicked, f"Icon {i}")
        #         self.htray.append(icon)  # Use append() method
        #     else:
        #         button = TrayButton()
        #         button.set_label(f"Btn {i}")
        #         button.connect("clicked", self._on_tray_item_clicked, f"Button {i}")
        #         self.htray.append(button)  # Use append() method

        # Put HTray in a scrolled window with better size
        scrolled_htray = Gtk.ScrolledWindow()
        scrolled_htray.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scrolled_htray.set_child(self.htray)
        scrolled_htray.set_size_request(200, 150)  # Much larger width and height
        scrolled_htray.set_hexpand(False)
        scrolled_htray.set_vexpand(False)

        vbox.append(scrolled_htray)

        # Controls
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        controls.set_halign(Gtk.Align.CENTER)
        add_btn = Gtk.Button(label="Add Item")
        add_btn.connect("clicked", self._on_add_htray_item)
        controls.append(add_btn)
        remove_btn = Gtk.Button(label="Remove Last")
        remove_btn.connect("clicked", self._on_remove_htray_item)
        controls.append(remove_btn)
        vbox.append(controls)
        frame.set_child(vbox)
        container.append(frame)

    def _add_vtray_example(self, container):
        frame = Gtk.Frame(label="Vertical Tray (VTray)")
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_margin_start(10)
        hbox.set_margin_end(10)
        hbox.set_margin_top(10)
        hbox.set_margin_bottom(10)

        # Create VTray with proper sizing
        self.vtray = VTray()
        self.vtray.set_hexpand(False)
        self.vtray.set_vexpand(True)
        self.vtray.set_size_request(120, -1)  # Increased width

        # Add initial items using append
        for i in range(6):  # Reduced initial count
            icon = TrayIcon(
                icon_name="system-search" if i % 2 == 0 else "edit-copy",
                xo_color=XoColor.get_random_color()
            )
            icon.connect("clicked", self._on_tray_item_clicked, f"VTray Icon {i}")
            self.vtray.append(icon)  # Use append() method

        # Put VTray in a scrolled window with better size
        scrolled_vtray = Gtk.ScrolledWindow()
        scrolled_vtray.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_vtray.set_child(self.vtray)
        scrolled_vtray.set_size_request(150, 400)  # Much larger width and height
        scrolled_vtray.set_hexpand(False)
        scrolled_vtray.set_vexpand(True)

        hbox.append(scrolled_vtray)

        # Controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        controls_box.set_hexpand(True)
        controls_box.set_vexpand(True)

        info_label = Gtk.Label(label="Vertical tray with scrolling\nClick items to see events")
        info_label.set_halign(Gtk.Align.START)
        controls_box.append(info_label)

        add_btn = Gtk.Button(label="Add VTray Item")
        add_btn.connect("clicked", self._on_add_vtray_item)
        controls_box.append(add_btn)

        remove_btn = Gtk.Button(label="Remove Last")
        remove_btn.connect("clicked", self._on_remove_vtray_item)
        controls_box.append(remove_btn)

        self.status_label = Gtk.Label(label="No tray items clicked yet")
        self.status_label.set_halign(Gtk.Align.START)
        controls_box.append(self.status_label)

        hbox.append(controls_box)
        frame.set_child(hbox)
        container.append(frame)

    def _add_window_controls(self, container):
        """Add window control examples."""
        frame = Gtk.Frame(label="Window Controls")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)

        # Info
        info_label = Gtk.Label(
            label="Window controls - test fullscreen mode and other window features"
        )
        info_label.set_halign(Gtk.Align.START)
        vbox.append(info_label)

        # Controls
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        controls.set_halign(Gtk.Align.CENTER)

        fullscreen_btn = Gtk.Button(label="Toggle Fullscreen")
        fullscreen_btn.connect("clicked", self._on_toggle_fullscreen)
        controls.append(fullscreen_btn)

        window_info_btn = Gtk.Button(label="Window Info")
        window_info_btn.connect("clicked", self._on_show_window_info)
        controls.append(window_info_btn)

        vbox.append(controls)

        # Window status
        self.window_status_label = Gtk.Label(label="Window status: Normal")
        vbox.append(self.window_status_label)

        frame.set_child(vbox)
        container.append(frame)

    def _on_tray_item_clicked(self, widget, item_name):
        """Handle tray item clicks."""
        if hasattr(self, 'status_label'):
            self.status_label.set_text(f"Clicked: {item_name}")
        print(f"Tray item clicked: {item_name}")

    def _on_add_htray_item(self, button):
        """Add item to horizontal tray."""
        # Count current children using GTK4 method
        child_count = 0
        child = self.htray.get_first_child()
        while child:
            child_count += 1
            child = child.get_next_sibling()

        new_button = TrayButton()
        new_button.set_label(f"New {child_count}")
        new_button.connect(
            "clicked",
            self._on_tray_item_clicked,
            f"New Button {child_count}"
        )
        self.htray.append(new_button)  # Use append() method

    def _on_remove_htray_item(self, button):
        """Remove last item from horizontal tray."""
        # Find last child using GTK4 method
        last_child = self.htray.get_last_child()
        if last_child:
            self.htray.remove(last_child)  # Use remove() method

    def _on_add_vtray_item(self, button):
        """Add item to vertical tray."""
        # Count current children
        child_count = 0
        child = self.vtray.get_first_child()
        while child:
            child_count += 1
            child = child.get_next_sibling()

        new_icon = TrayIcon(
            icon_name="document-new",
            xo_color=XoColor.get_random_color()
        )
        new_icon.connect(
            "clicked",
            self._on_tray_item_clicked,
            f"New VIcon {child_count}"
        )
        self.vtray.append(new_icon)  # Use append() method

    def _on_remove_vtray_item(self, button):
        """Remove last item from vertical tray."""
        # Find last child
        last_child = self.vtray.get_last_child()
        if last_child:
            self.vtray.remove(last_child)  # Use remove() method

    def _on_toggle_fullscreen(self, button):
        """Toggle fullscreen mode."""
        if self.is_fullscreen():
            self.unfullscreen()
            self.window_status_label.set_text("Window status: Normal")
        else:
            self.fullscreen()
            self.window_status_label.set_text("Window status: Fullscreen")

    def _on_show_window_info(self, button):
        """Show window information."""
        info = [
            f"Window Title: {self.get_title()}",
            f"Window ID: {self.get_id()[:8]}...",
            f"Fullscreen: {self.is_fullscreen()}",
            f"Canvas: {type(self.get_canvas()).__name__}",
        ]

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Window Information"
        )
        dialog.set_property("text", "Window Information")
        dialog.set_property("secondary-text", "\n".join(info))
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()


def main():
    """Run the tray and window example activity."""
    app = Gtk.Application(application_id="org.sugarlabs.TrayWindowExample")

    def on_activate(app):
        activity = TrayAndWindowExampleActivity()
        app.add_window(activity)
        activity.present()

    app.connect("activate", on_activate)
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
    ## COPY 2
"""Sugar GTK4 Tray and Window Example."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk

from sugar.activity import SimpleActivity
from sugar.graphics.tray import HTray, VTray, TrayButton, TrayIcon
from sugar.graphics.window import Window
from sugar.graphics.xocolor import XoColor


class TrayAndWindowExampleActivity(SimpleActivity):
    """Example activity demonstrating Sugar GTK4 Tray and Window features."""

    def __init__(self):
        super().__init__()
        self.set_title("Sugar GTK4 Tray and Window Example")
        self._create_content()

    def _create_content(self):
        """Create the main content demonstrating tray and window features."""
        # Scrolled window for main content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)

        # Title
        title = Gtk.Label()
        title.set_markup("<big><b>Sugar GTK4 Tray and Window Example</b></big>")
        title.set_hexpand(True)
        main_box.append(title)

        # Add tray examples
        self._add_htray_example(main_box)
        self._add_vtray_example(main_box)
        self._add_window_controls(main_box)

        scrolled.set_child(main_box)
        self.set_canvas(scrolled)
        self.set_default_size(900, 700)

    def _add_htray_example(self, container):
        frame = Gtk.Frame(label="Horizontal Tray (HTray)")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)

        info_label = Gtk.Label(label="Horizontal tray with scrolling - add many items to see scroll buttons")
        vbox.append(info_label)

        # Use SVGs from src/sugar/graphics/icons/
        icons_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "src", "sugar", "graphics", "icons"
        )
        svg_files = [
            "checkbox-checked.svg",
            "document-open.svg",
            "go-right.svg",
            "media-playback-pause.svg",
            "media-playback-start.svg",
            "preferences-system.svg",
            "radio-active.svg",
            "system-search.svg",
            "test.svg",
        ]
        # Create HTray with proper sizing
        self.htray = HTray()
        self.htray.set_hexpand(True)
        self.htray.set_vexpand(False)
        self.htray.set_size_request(900, 120)  # Wider for better display

        # Add SVG icons as TrayIcon using
        for i, svg_file in enumerate(svg_files):
            icon_path = os.path.join(icons_dir, svg_file)
            icon = TrayIcon(icon_name=icon_path, xo_color=XoColor.get_random_color())
            icon.connect("clicked", self._on_tray_item_clicked, f"SVG Icon {i}")
            self.htray.add_item(icon)

        scrolled_htray = Gtk.ScrolledWindow()
        scrolled_htray.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scrolled_htray.set_child(self.htray)
        scrolled_htray.set_size_request(900, 150)
        scrolled_htray.set_hexpand(True)
        scrolled_htray.set_vexpand(False)

        vbox.append(scrolled_htray)

        # Controls
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        controls.set_halign(Gtk.Align.CENTER)
        add_btn = Gtk.Button(label="Add Item")
        add_btn.connect("clicked", self._on_add_htray_item)
        controls.append(add_btn)
        remove_btn = Gtk.Button(label="Remove Last")
        remove_btn.connect("clicked", self._on_remove_htray_item)
        controls.append(remove_btn)
        vbox.append(controls)
        frame.set_child(vbox)
        container.append(frame)

    def _add_vtray_example(self, container):
        frame = Gtk.Frame(label="Vertical Tray (VTray)")
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_margin_start(10)
        hbox.set_margin_end(10)
        hbox.set_margin_top(10)
        hbox.set_margin_bottom(10)

        icons_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "src", "sugar", "graphics", "icons"
        )
        svg_files = [
            "system-search.svg",
            "media-playback-start.svg",
            "media-playback-pause.svg",
            "go-right.svg",
            "preferences-system.svg",
            "radio-active.svg",
        ]

        self.vtray = VTray()
        self.vtray.set_hexpand(False)
        self.vtray.set_vexpand(True)
        self.vtray.set_size_request(120, 600)  # Taller for better display

        # Add SVG icons as TrayIcon using
        for i, svg_file in enumerate(svg_files):
            icon_path = os.path.join(icons_dir, svg_file)
            icon = TrayIcon(icon_name=icon_path, xo_color=XoColor.get_random_color())
            icon.connect("clicked", self._on_tray_item_clicked, f"VSVG Icon {i}")
            self.vtray.add_item(icon)

        scrolled_vtray = Gtk.ScrolledWindow()
        scrolled_vtray.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_vtray.set_child(self.vtray)
        scrolled_vtray.set_size_request(150, 600)
        scrolled_vtray.set_hexpand(False)
        scrolled_vtray.set_vexpand(True)

        hbox.append(scrolled_vtray)

        # Controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        controls_box.set_hexpand(True)
        controls_box.set_vexpand(True)

        info_label = Gtk.Label(label="Vertical tray with scrolling\nClick items to see events")
        info_label.set_halign(Gtk.Align.START)
        controls_box.append(info_label)

        add_btn = Gtk.Button(label="Add VTray Item")
        add_btn.connect("clicked", self._on_add_vtray_item)
        controls_box.append(add_btn)

        remove_btn = Gtk.Button(label="Remove Last")
        remove_btn.connect("clicked", self._on_remove_vtray_item)
        controls_box.append(remove_btn)

        self.status_label = Gtk.Label(label="No tray items clicked yet")
        self.status_label.set_halign(Gtk.Align.START)
        controls_box.append(self.status_label)

        hbox.append(controls_box)
        frame.set_child(hbox)
        container.append(frame)

    def _on_add_htray_item(self, button):
        """Add item to horizontal tray."""
        child_count = len(self.htray.get_children())
        new_button = TrayButton()
        new_button.set_label(f"New {child_count}")
        new_button.connect(
            "clicked",
            self._on_tray_item_clicked,
            f"New Button {child_count}"
        )
        self.htray.add_item(new_button)

    def _on_remove_htray_item(self, button):
        """Remove last item from horizontal tray."""
        children = self.htray.get_children()
        if children:
            self.htray.remove_item(children[-1])

    def _add_window_controls(self, container):
        """Add window control examples."""
        frame = Gtk.Frame(label="Window Controls")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)

        # Info
        info_label = Gtk.Label(
            label="Window controls - test fullscreen mode and other window features"
        )
        info_label.set_halign(Gtk.Align.START)
        vbox.append(info_label)

        # Controls
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        controls.set_halign(Gtk.Align.CENTER)

        fullscreen_btn = Gtk.Button(label="Toggle Fullscreen")
        fullscreen_btn.connect("clicked", self._on_toggle_fullscreen)
        controls.append(fullscreen_btn)

        window_info_btn = Gtk.Button(label="Window Info")
        window_info_btn.connect("clicked", self._on_show_window_info)
        controls.append(window_info_btn)

        vbox.append(controls)

        # Window status
        self.window_status_label = Gtk.Label(label="Window status: Normal")
        vbox.append(self.window_status_label)

        frame.set_child(vbox)
        container.append(frame)

    def _on_tray_item_clicked(self, widget, item_name):
        """Handle tray item clicks."""
        if hasattr(self, 'status_label'):
            self.status_label.set_text(f"Clicked: {item_name}")
        print(f"Tray item clicked: {item_name}")

    # def _on_add_htray_item(self, button):
    #     """Add item to horizontal tray."""
    #     # Count current children using GTK4 method
    #     child_count = 0
    #     child = self.htray.get_first_child()
    #     while child:
    #         child_count += 1
    #         child = child.get_next_sibling()

    #     new_button = TrayButton()
    #     new_button.set_label(f"New {child_count}")
    #     new_button.connect(
    #         "clicked",
    #         self._on_tray_item_clicked,
    #         f"New Button {child_count}"
    #     )
    #     self.htray.append(new_button)  # Use append() method

    # def _on_remove_htray_item(self, button):
    #     """Remove last item from horizontal tray."""
    #     # Find last child using GTK4 method
    #     last_child = self.htray.get_last_child()
    #     if last_child:
    #         self.htray.remove(last_child)  # Use remove() method

    def _on_add_vtray_item(self, button):
        """Add item to vertical tray."""
        # Count current children
        child_count = 0
        child = self.vtray.get_first_child()
        while child:
            child_count += 1
            child = child.get_next_sibling()

        new_icon = TrayIcon(
            icon_name="document-new",
            xo_color=XoColor.get_random_color()
        )
        new_icon.connect(
            "clicked",
            self._on_tray_item_clicked,
            f"New VIcon {child_count}"
        )
        self.vtray.append(new_icon)  # Use append() method

    def _on_remove_vtray_item(self, button):
        """Remove last item from vertical tray."""
        # Find last child
        last_child = self.vtray.get_last_child()
        if last_child:
            self.vtray.remove(last_child)  # Use remove() method

    def _on_toggle_fullscreen(self, button):
        """Toggle fullscreen mode."""
        if self.is_fullscreen():
            self.unfullscreen()
            self.window_status_label.set_text("Window status: Normal")
        else:
            self.fullscreen()
            self.window_status_label.set_text("Window status: Fullscreen")

    def _on_show_window_info(self, button):
        """Show window information."""
        info = [
            f"Window Title: {self.get_title()}",
            f"Window ID: {self.get_id()[:8]}...",
            f"Fullscreen: {self.is_fullscreen()}",
            f"Canvas: {type(self.get_canvas()).__name__}",
        ]

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Window Information"
        )
        dialog.set_property("text", "Window Information")
        dialog.set_property("secondary-text", "\n".join(info))
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()


def main():
    """Run the tray and window example activity."""
    app = Gtk.Application(application_id="org.sugarlabs.TrayWindowExample")

    def on_activate(app):
        activity = TrayAndWindowExampleActivity()
        app.add_window(activity)
        activity.present()

        # Apply CSS for black text and better styling after display is available
        css_provider = Gtk.CssProvider()
        css_data = """
        label, button, entry, .button, .label {
            color: #000000;
        }
        frame {
            margin: 10px;
        }
        """
        css_provider.load_from_data(css_data.encode())
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        else:
            import logging
            logging.warning("Failed to apply CSS: No display available")

    app.connect("activate", on_activate)
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
