import tkinter
import tkinter.ttk
import tkinter.messagebox as msgbox
import sys
import os
import functools
import time

import settings
import settings_window
import logger
import data_storage
import main_tabs
import constants
from basic_module import ensureInstanceOfType
from logger import logCall
import result_board
import startup_window

class MainApp:
    def __init__(self):
        self.app_path = os.path.dirname(__file__)
        self.settings = settings.Settings()
        self.top = tkinter.Tk()
        self.top.title(constants.app_foreign_title)
        self.window_width = 600
        self.window_height = 450
        self.screen_width = self.top.winfo_screenwidth()
        self.screen_height = self.top.winfo_screenheight()
        window_x = (self.screen_width - self.window_width) // 2
        window_y = (self.screen_height - self.window_height) // 2
        self.top.geometry("{width}x{height}+{x}+{y}".format(
            width=self.window_width, height=self.window_height,
            x=window_x, y=window_y))
        # Use self.top.iconbitmap or self.top.iconphoto here.
        icon_path = os.path.join(self.app_path, r"app_icon.ico")
        if os.path.exists(icon_path):
            self.top.iconbitmap(bitmap=icon_path, default=icon_path)
        
        self.settingsWindow = None
        self.resultBoard = None
        self.init_finished = False
        self.program_exited = False
        
        self.top.protocol("WM_DELETE_WINDOW", self.quit)

    def initWidgets(self, ev=None, startupWindowExitFunc=None):
        self.menu = tkinter.Menu(self.top)
        self.settingsMenu = tkinter.Menu(self.menu, tearoff=False)
        self.settingsMenu.add_command(
            label="设置", command=functools.partial(
                logCall, self.openSettingsWindow))
        self.menu.add_cascade(label="设置", menu=self.settingsMenu)
        self.helpMenu = tkinter.Menu(self.menu, tearoff=False)
        self.helpMenu.add_command(label="关于...", command=self.about)
        self.helpMenu.add_command(label="反馈问题或建议", command=self.feedback)
        self.menu.add_cascade(label="帮助", menu=self.helpMenu)
        self.top.config(menu=self.menu)

        self.mainNotebook = tkinter.ttk.Notebook(self.top)
        self.mainTabs = []
        self.mainTabs.append(main_tabs.SingleGroupNumberTab(
            self.top, self.mainNotebook, self.settings,
            "单范围随机数生成",
            openResultBoardFunc=self.openResultBoard,
            checkResultBoardExistsFunc=self.checkResultBoardExists,
            setResultToBoardFunc=self.setResultToBoard,
            closeResultBoardFunc=self.closeResultBoard))
        self.mainTabs.append(main_tabs.MultiGroupsNumberTab(
            self.top, self.mainNotebook, self.settings,
            "多范围随机数生成",
            openResultBoardFunc=self.openResultBoard,
            checkResultBoardExistsFunc=self.checkResultBoardExists,
            setResultToBoardFunc=self.setResultToBoard,
            closeResultBoardFunc=self.closeResultBoard))
        self.defaultTabIndex = 0
        previousTabIndex = data_storage.getData(["current_tab_index"],
                                                self.defaultTabIndex)
        previousTabIndex = ensureInstanceOfType(
            previousTabIndex, int, ValueError,
            default=self.defaultTabIndex)
        if not (0 <= previousTabIndex < len(self.mainTabs)):
            previousTabIndex = self.defaultTabIndex
        self.previousTabIndex = previousTabIndex
        self.mainNotebook.select(self.mainNotebook.tabs()[previousTabIndex])
        self.mainNotebook.bind("<<NotebookTabChanged>>", self.toggleTab)
        self.mainNotebook.pack(fill=tkinter.BOTH, side=tkinter.TOP, expand=True)

        self.buttonFrame = tkinter.Frame(self.top)
        self.generateButton = tkinter.Button(
            self.buttonFrame, text="生成随机数",
            command=self.generateRandomNumber)
        self.generateButton.pack()
        self.buttonFrame.pack(fill=tkinter.X, side=tkinter.BOTTOM, expand=True)
        def exitStartupWindow(ev=None):
            nonlocal startupWindowExitFunc, self
            if self.program_exited:
                return
            if callable(startupWindowExitFunc):
                startupWindowExitFunc()
            self.top.focus_force()
        if not self.program_exited:
            self.init_finished = True
            # self.top.after(2000, exitStartupWindow) # For test only.
            exitStartupWindow()
        
    def mainloop(self):
        startupWindow = startup_window.StartupWindow(
            self.top, programExitFunc=self.quit)
        self.top.after(1, functools.partial(
            self.initWidgets, startupWindowExitFunc=startupWindow.exit_window))
        self.top.mainloop()
        self.settings.saveSettings()

    def quit(self, ev=None):
        if self.init_finished:
            for tab in self.mainTabs:
                tab.saveData()
            currentTabIndex = self.mainNotebook.index(tkinter.CURRENT)
            if currentTabIndex != self.previousTabIndex:
                data_storage.setData(["current_tab_index"], currentTabIndex)
            data_storage.saveData()
        self.top.quit()
        self.top.destroy()
        self.program_exited = True

    def generateRandomNumber(self, ev=None):
        logCall(
            self.mainTabs[self.mainNotebook.index(tkinter.CURRENT)].generate,
            error_handler=(lambda e: \
                msgbox.showwarning("异常", "程序出现异常。", parent=self.top)))

    def toggleTab(self, ev=None):
        tabIndex = self.mainNotebook.index(tkinter.CURRENT)
        self.mainTabs[tabIndex].tabSwitched()

    def about(self):
        """
        msgbox.showinfo("关于 Random number generator",
                        "随机数生成器\n"
                        "Designed for Class 2310\n"
                        "Created by Qin Guodong from Class 2310\n"
                        "Supported by Mr. Li\n")
        """
        title = "关于 {title}".format(title=constants.app_foreign_title)
        """
        contentLines = (
            "{title}".format(title=constants.app_title),
            "为2310班设计，",
            "由Qin Guodong制作，",
            "并得到{leader}支持。".format(leader="Mr. Li"),
            "本程序运行于 Python {py_version} 和 Tk {tk_version}。".format(
                py_version="{}.{}.{}".format(sys.version_info.major,
                                             sys.version_info.minor,
                                             sys.version_info.micro),
                tk_version=tkinter.TkVersion))
        """
        """
        contentLines = (
            "{title}".format(title=constants.app_title),
            "作者：{author}".format(author=constants.author),
            "本程序运行于 Python {py_version} 和 Tk {tk_version}。".format(
                py_version="{}.{}.{}".format(sys.version_info.major,
                                             sys.version_info.minor,
                                             sys.version_info.micro),
                tk_version=tkinter.TkVersion),
            "",
            "本程序由{auth_origin}授权给以下组织：".format(
                auth_origin=authorize_information.authorizedOrigin),
            "\t{auth_org}".format(
                auth_org=authorize_information.authorizedOrgnization))
        """
        contentLines = (
            "{title}".format(title=constants.app_title),
            "作者：{author}".format(author=constants.author),
            "本程序运行于 Python {py_version} 和 Tk {tk_version}。".format(
                py_version="{}.{}.{}".format(sys.version_info.major,
                                             sys.version_info.minor,
                                             sys.version_info.micro),
                tk_version=tkinter.TkVersion))
        msgbox.showinfo(title, "\n".join(contentLines))

    def feedback(self):
        msgbox.showinfo(
            "反馈相关信息",
            "".join((
                "本程序可供学习之用。\n",
                "如程序运行时出现问题，或有有关本程序的建议，\n",
                "可自行修改源代码，",
                "或将问题或建议以电子邮件方式发送至作者邮箱",
                "{}\n".format(constants.author_email),
                "并将程序文件夹中的文件全部压缩至压缩包并添加到附件中。\n"
                "感谢您的支持！")))

    def openSettingsWindow(self, ev=None):
        if self.settingsWindow is not None:
            self.settingsWindow.focus()
            return
        self.settingsWindow = settings_window.SettingsWindow(
            self.top, self.top.winfo_x(), self.top.winfo_y())
        self.settingsWindow.mainloop()
        self.settings.loadSettings()
        del self.settingsWindow
        self.settingsWindow = None

    def openResultBoard(self, initial=""):
        board_x = self.top.winfo_x() + self.window_width
        board_y = self.top.winfo_y()
        if self.resultBoard is None:
            self.resultBoard = result_board.ResultBoard(
                self.top, board_x, board_y)
        elif not self.resultBoard.window_exists():
            self.resultBoard.config_window_info(self.top, board_x, board_y)
            self.resultBoard.init_window()
        else:
            self.resultBoard.focus()
        self.resultBoard.setText(initial)

    def checkResultBoardExists(self) -> bool:
        if not hasattr(self, "resultBoard"):
            return False
        if self.resultBoard is None:
            return False
        if not self.resultBoard.window_exists():
            return False
        return True

    def setResultToBoard(self, text: str):
        if self.resultBoard is None:
            return
        if not self.resultBoard.window_exists():
            return
        self.resultBoard.setText(text)

    def closeResultBoard(self):
        if self.resultBoard is None:
            return
        if not self.resultBoard.window_exists():
            return
        self.resultBoard.quit()

def main():
    try:
        MainApp().mainloop()
    except Exception:
        logger.flushErrorToBuffer()
    logger.logError()
    logger.closeBuffer()

if __name__ == "__main__":
    main()
