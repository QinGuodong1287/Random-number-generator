import tkinter

from basic_window import Window

class ResultBoard(Window):
    def config_window_info_sub(self):
        self.window_info["title"] = "结果显示"
        self.window_info["width"] = 300
        self.window_info["height"] = 200

    def init_widgets(self):
        self.board_label = tkinter.Label(
            self.top, font=("微软雅黑", 16),
            wraplength=self.window_info["width"])
        self.board_label.pack(fill=tkinter.BOTH, expand=True)
        
        self.top.attributes("-topmost", True)

    def quit(self):
        self.exit_window()

    def setText(self, text: str):
        if not self.window_exists():
            return
        self.board_label.config(text=str(text))
