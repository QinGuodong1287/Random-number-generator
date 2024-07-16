import tkinter

import constants
import basic_window

class StartupWindow(basic_window.Window):
    def config_window_info_sub(self):
        self.window_info["x"] = basic_window.Window.MIDDLE
        self.window_info["y"] = basic_window.Window.MIDDLE
        self.window_info["width"] = 300
        self.window_info["height"] = 200
        self.window_info["title"] = "欢迎"

    def init_with_other_args(self, programExitFunc=None):
        self.programExitFunc = programExitFunc

    def init_widgets(self):
        self.loadingLabel = tkinter.Label(self.top, text="启动中...")
        self.loadingLabel.pack(fill=tkinter.X, side=tkinter.BOTTOM)
        self.appTitleLabel = tkinter.Label(
            self.top, text=constants.app_title, font=("微软雅黑", 16))
        self.appTitleLabel.pack(fill=tkinter.BOTH, expand=True)
        self.top.attributes("-topmost", True)
        self.top.resizable(False, False)
        self.top.protocol("WM_DELETE_WINDOW", self.exit_program)

    def exit_program(self):
        if callable(self.programExitFunc):
            # self.top.after(10, self.programExitFunc)
            self.programExitFunc()
        try:
            self.exit_window()
        except tkinter.TclError:
            pass
