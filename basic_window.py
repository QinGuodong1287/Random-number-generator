import tkinter

class Window:
    DEFAULT_WINDOW_INFO = {
        "master": None,
        "x": None,
        "y": None,
        "width": None,
        "height": None,
        "title": ""
        }
    MIDDLE = "middle"
    MAX = "max"
    
    def __init__(self, master=None, x=None, y=None, title="", *args, **kwargs):
        self.window_info = Window.DEFAULT_WINDOW_INFO
        self.is_in_mainloop = False
        self.config_window_info(master, x, y, title)
        self.init_with_other_args(*args, **kwargs)
        self.init_window()

    def config_window_info(self, master=None, x=None, y=None, title=""):
        """Set value in dict self.window_info."""
        if (not hasattr(self, "window_info") or \
            not isinstance(self.window_info, dict)):
            self.window_info = Window.DEFAULT_WINDOW_INFO
        if master is not None:
            self.window_info["master"] = master
        if x is not None:
            self.window_info["x"] = x
        if y is not None:
            self.window_info["y"] = y
        self.window_info["title"] = str(title) if title is not None else ""
        self.config_window_info_sub()

    def config_window_info_sub(self):
        """Customize your window basic geometry by overridding this function,
        and set value in dict self.window_info."""
        pass

    def fix_window_info(self):
        if (not hasattr(self, "window_info") or \
            not isinstance(self.window_info, dict)):
            self.window_info = Window.DEFAULT_WINDOW_INFO
        def ensure(dict_, key, value, type_, ignore_values=(None,)):
            # Ensure that the value is a instance of type_.
            assert isinstance(ignore_values, (list, tuple))
            if value not in ignore_values:
                if not isinstance(value, type_):
                    try:
                        value = type_(value)
                    except Exception as e:
                        raise TypeError("Can't convert value in type `{type_}`. "
                                        "(Key: {key} Cause: {cause})".format(
                                            type_=type_, key=repr(key),
                                            cause=str(e)))
            dict_[key] = value
        def ensure_self(dict_, key, type_, ignore_values=(None,)):
            ensure(dict_, key, dict_.get(key), type_, ignore_values)
        ensure_self(self.window_info, "x", int,
                    (None, Window.MIDDLE, Window.MAX))
        ensure_self(self.window_info, "y", int,
                    (None, Window.MIDDLE, Window.MAX))
        ensure_self(self.window_info, "width", int)
        ensure_self(self.window_info, "height", int)
        ensure_self(self.window_info, "title", str)

    def init_with_other_args(self, *args, **kwargs):
        """Customize your window by overriding this function."""
        pass

    def init_basic_window(self):
        """Init the Toplevel window."""
        if self.window_exists():
            self.exit_window()
        self.top = tkinter.Toplevel(self.window_info["master"])
        if self.window_info["title"]:
            self.top.title(self.window_info["title"])
        window_width = self.window_info["width"]
        window_height = self.window_info["height"]
        if window_width is not None and window_height is not None:
            window_size = "{width}x{height}".format(
                width=window_width, height=window_height)
        else:
            window_size = ""
        window_x = self.window_info["x"]
        window_y = self.window_info["y"]
        if window_x is not None and window_y is not None:
            if window_width is not None:
                if window_x == Window.MAX:
                    window_x = self.top.winfo_screenwidth() - window_width
                elif window_x == Window.MIDDLE:
                    window_x = (self.top.winfo_screenwidth() - \
                                window_width) // 2
            if window_height is not None:
                if window_y == Window.MAX:
                    window_y = self.top.winfo_screenheight() - window_height
                elif window_y == Window.MIDDLE:
                    window_y = (self.top.winfo_screenheight() - \
                                window_height) // 2
            window_position = "+{x}+{y}".format(
                x=window_x, y=window_y)
        else:
            window_position = ""
        if window_size or window_position:
            self.top.geometry("{size}{position}".format(
                size=window_size, position=window_position))
        self.top.protocol("WM_DELETE_WINDOW", self.exit_window)

    def init_widgets(self):
        """Init your widgets here."""
        pass

    def init_window(self):
        self.config_window_info()
        self.fix_window_info()
        self.init_basic_window()
        self.init_widgets()

    def window_exists(self) -> bool:
        """Check whether the window is exists."""
        return (hasattr(self, "top") and \
                isinstance(self.top, tkinter.Toplevel))

    def ensure_window_exists(self):
        """Make sure that the window is exists, or raise
        WindowNotExistsError."""
        if not self.window_exists():
            raise WindowNotExistsError(
                "The window is not exists. Please call init_window() first.")

    def handle_window_exit(self):
        """Do something when window exits."""
        pass

    def exit_window(self, ev=None):
        self.ensure_window_exists()
        self.handle_window_exit()
        if self.is_in_mainloop:
            self.top.quit()
        self.top.destroy()
        del self.top
        self.top = None

    def mainloop(self):
        self.ensure_window_exists()
        self.is_in_mainloop = True
        self.top.mainloop()
        self.is_in_mainloop = False

    def focus(self):
        self.ensure_window_exists()
        self.top.deiconify()
        self.top.focus()

class WindowNotExistsError(Exception):
    """The Toplevel window is not exists."""
    pass
