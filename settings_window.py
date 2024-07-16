import tkinter
import tkinter.ttk
import tkinter.messagebox as msgbox
import functools
import re
import enum

from exceptions import SettingsItemValueInvalid
from logger import logCall
from basic_window import Window
from settings import Settings

class SettingsWindow(Window):
    def config_window_info_sub(self):
        self.window_info["width"] = window_width = 450
        self.window_info["height"] = window_height = 400
        """
        if self.window_info["x"] is None:
            self.window_info["x"] = Window.MIDDLE
        if self.window_info["y"] is None:
            self.window_info["y"] = Window.MIDDLE
        """
        self.window_info["x"] = Window.MIDDLE
        self.window_info["y"] = Window.MIDDLE
        self.window_info["title"] = "设置"

    def init_with_other_args(self, orig_settings=None):
        assert orig_settings is None or isinstance(orig_settings, Settings)
        self.orig_settings = orig_settings
    
    def init_widgets(self):
        self.settings = Settings()
        
        self.items = {}
        """
        self.uiFrame = tkinter.ttk.LabelFrame(self.top, text="用户界面（ui）")
        self.items["nums_count"] = EntryItem(
            self.uiFrame, "随机数每行显示个数：",
            self.settings, ["ui", "nums_count_per_line"], 15,
            widgetValueToObject=self.numsCountHook)
        self.uiFrame.pack(side=tkinter.TOP, fill=tkinter.X)
        """
        self.advancedFrame = tkinter.ttk.LabelFrame(
            self.top, text="Advanced settings")

        self.advRandomFrame = tkinter.ttk.LabelFrame(
            self.advancedFrame, text="Random")
        """
        self.items["ignore_nums"] = EntryItem(
            self.advRandomFrame, "Ignore nums (separate with ','):",
            self.settings, ["random", "ignore_nums"], [],
            lambda nums: ','.join((str(num) for num in nums)),
            self.ignoreNumsHook)
        """
        self.items["ignore_nums"] = ListItem(
            self.advRandomFrame, "Ignore nums:",
            self.settings, ["random", "ignore_nums"], [],
            orient=SettingsItemOrient.VERTICAL,
            stringToObject=SettingsWindow.numHook,
            modifyElementHandler=self.focus,
            elementValueErrorHandler=lambda err: self.focus(),
            addElementLabel="添加数字", modifyElementLabel="修改数字",
            deleteElementLabel="删除数字")
        
        self.items["higher_level_nums"] = ListItem(
            self.advRandomFrame, "Higher level nums:",
            self.settings, ["random", "higher_level_nums"], [],
            orient=SettingsItemOrient.VERTICAL,
            stringToObject=SettingsWindow.numHook,
            modifyElementHandler=self.focus,
            elementValueErrorHandler=lambda err: self.focus(),
            addElementLabel="添加数字", modifyElementLabel="修改数字",
            deleteElementLabel="删除数字")
        
        self.advRandomFrame.pack(side=tkinter.TOP, fill=tkinter.X, expand=True)

        self.advancedFrame.pack(side=tkinter.TOP, fill=tkinter.X)
        
        self.buttonFrame = tkinter.ttk.Frame(self.top)
        self.cancelButton = tkinter.ttk.Button(
            self.buttonFrame, text="取消",
            command=functools.partial(self.quit, promptToSave=True))
        self.cancelButton.pack(side=tkinter.RIGHT)
        self.okButton = tkinter.ttk.Button(self.buttonFrame, text="确认",
                                           command=self.saveSettings)
        self.okButton.pack(side=tkinter.RIGHT)
        self.buttonFrame.pack(fill=tkinter.X, side=tkinter.BOTTOM,
                              anchor=tkinter.SE)
        
        self.top.protocol("WM_DELETE_WINDOW",
                          functools.partial(self.quit, promptToSave=True))
        self.focus()

    def quit(self, ev=None, promptToSave=False):
        if promptToSave:
            modified = False
            for item in self.items.values():
                if item.checkItemModified():
                    modified = True
                    break
            if modified:
                self.focus()
                if not msgbox.askokcancel(
                    "退出设置", "设置已修改。是否不保存设置并退出？",
                    parent=self.top):
                    self.focus()
                    return
        self.exit_window()

    def saveSettings(self, ev=None):
        errorLines = []
        for item in self.items.values():
            error = item.saveItem()
            if error:
                errorLines.append(error)
        if errorLines:
            self.focus()
            msgbox.showwarning("警告", "\n".join(errorLines), parent=self.top)
            self.focus()
            return
        if self.orig_settings is not None:
            self.orig_settings.update(self.settings)
        else:
            self.settings.saveSettings()
        self.quit()

    commaPattern = re.compile(r",\s*")

    @staticmethod
    def ignoreNumsHook(numsStr):
        numsStrs = re.split(SettingsWindow.commaPattern, numsStr)
        nums = []
        for numStr in numsStrs:
            numStr = numStr.strip()
            if not numStr:
                continue
            try:
                num = int(numStr)
            except ValueError:
                raise SettingsItemValueInvalid(
                    "Ignore nums have some error characters"
                    " or any of nums is not integer.")
            nums.append(num)
        return nums

    @staticmethod
    def numsCountHook(numStr):
        try:
            num = int(numStr)
            if num <= 0:
                raise ValueError
        except ValueError:
            raise SettingsItemValueInvalid("随机数每行显示个数不是正整数。")
        return num

    @staticmethod
    def numHook(numStr):
        try:
            num = int(numStr)
        except ValueError:
            raise SettingsItemValueInvalid("The num is not a valid integer.")
        return num

class SettingsItemOrient(enum.Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class SettingsItem:
    def __init__(self, master, text, settings, key, default=None,
                 objectToWidgetValue=None, widgetValueToObject=None,
                 orient=SettingsItemOrient.HORIZONTAL,
                 *args, **kwargs):
        settings.checkKey(key)
        self.settings = settings
        self.key = key
        self.default = default
        self.objectToWidgetValue = objectToWidgetValue
        self.widgetValueToObject = widgetValueToObject
        # self.itemValueErrorHandler = itemValueErrorHandler
        if not isinstance(orient, SettingsItemOrient):
            raise ValueError(
                "The `orient` is not a instance of SettingsItemOrient.")
        # self.orient = orient
        logCall(self.initWithOtherParams, *args, **kwargs)
        self.itemFrame = tkinter.ttk.Frame(master)
        self.itemLabel = tkinter.ttk.Label(self.itemFrame, text=text)
        if orient == SettingsItemOrient.VERTICAL:
            self.itemLabel.pack(fill=tkinter.X, side=tkinter.TOP)
        else:
            self.itemLabel.pack(fill=tkinter.Y, side=tkinter.LEFT)
        self.itemValueFrame = tkinter.ttk.Frame(self.itemFrame)
        itemValue = settings.get(key, default)
        self.initItemValueFrame(itemValue)
        if orient == SettingsItemOrient.VERTICAL:
            self.itemValueFrame.pack(fill=tkinter.BOTH, side=tkinter.BOTTOM,
                                     expand=True)
        else:
            self.itemValueFrame.pack(fill=tkinter.BOTH, side=tkinter.RIGHT,
                                     expand=True)
        self.itemFrame.pack(fill=tkinter.X)

    def initWithOtherParams(self, *args, **kwargs):
        """Init item with customized parameters."""
        pass

    @staticmethod
    def _convert(converter, value, finalConverter=None, default=None,
                 avoidNone=True):
        if value is not None:
            if callable(converter):
                newValue = converter(value)
                if newValue is not None or not avoidNone:
                    value = newValue
                del newValue
            if callable(finalConverter):
                newValue = finalConverter(value)
                if newValue is not None or not avoidNone:
                    value = newValue
                del newValue
        else:
            value = default
        return value

    def convertObjectToWidgetValue(self, value, finalConverter=None,
                                   default=None, avoidNone=True):
        return self._convert(self.objectToWidgetValue, value, finalConverter,
                             default, avoidNone)

    def convertWidgetValueToObject(self, value, finalConverter=None,
                                   default=None, avoidNone=True):
        return self._convert(self.widgetValueToObject, value, finalConverter,
                             default, avoidNone)

    def initItemValueFrame(self, itemValue):
        """Init widgets in itemValueFrame."""
        pass

    def saveItem(self) -> str:
        """Save item value. Return error string."""
        return ""

    def checkItemModified(self) -> bool:
        """Check item value if modified."""
        return False

class EntryItem(SettingsItem):
    def initItemValueFrame(self, itemValue):
        content = self.convertObjectToWidgetValue(
            itemValue, str, '')
        self.originalValue = content
        self.itemEntry = tkinter.ttk.Entry(self.itemValueFrame)
        self.itemEntry.insert('0', str(content))
        self.itemEntry.pack(fill=tkinter.BOTH, expand=True)

    def saveItem(self) -> str:
        itemValue = self.itemEntry.get()
        try:
            itemValue = self.convertWidgetValueToObject(itemValue,
                                                        default=self.default)
        except SettingsItemValueInvalid as e:
            return str(e)
        self.settings.set(self.key, itemValue)
        return ""

    def checkItemModified(self) -> bool:
        return self.itemEntry.get() != self.originalValue

class ListItem(SettingsItem):
    def initWithOtherParams(self, objectToString=None, stringToObject=None,
                            modifyElementHandler=None,
                            elementValueErrorHandler=None,
                            addElementLabel="添加元素",
                            modifyElementLabel="修改元素",
                            deleteElementLabel="删除元素"):
        self.objectToString = objectToString
        self.stringToObject = stringToObject
        self.modifyElementHandler = modifyElementHandler
        self.elementValueErrorHandler = elementValueErrorHandler
        self.addElementLabel = str(addElementLabel)
        self.modifyElementLabel = str(modifyElementLabel)
        self.deleteElementLabel = str(deleteElementLabel)
    
    def initItemValueFrame(self, itemValue):
        content = self.convertObjectToWidgetValue(
            itemValue,
            lambda content: (list(content) if isinstance(
                content, (list, tuple, set, frozenset)) else [content]),
            [])
        self.originalValue = content
        self.currentValue =  list(content)
        self.currentIndex = None
        self.itemListFrame = tkinter.ttk.Frame(self.itemValueFrame)
        self.itemList = tkinter.Listbox(self.itemListFrame, height=5,
                                        selectmode=tkinter.SINGLE)
        self.itemList.insert(tkinter.END, *content)
        self.itemList.bind("<<ListboxSelect>>", self.updateItem)
        self.itemList.pack(fill=tkinter.BOTH, side=tkinter.LEFT, expand=True)
        self.itemListScrollbar = tkinter.ttk.Scrollbar(
            self.itemListFrame, orient=tkinter.VERTICAL,
            command=self.itemList.yview)
        self.itemList.config(yscrollcommand=self.itemListScrollbar.set)
        self.itemListScrollbar.pack(fill=tkinter.Y, side=tkinter.RIGHT)
        
        self.itemEntry = tkinter.ttk.Entry(self.itemValueFrame)
        
        self.buttonFrame = tkinter.ttk.Frame(self.itemValueFrame)
        self.addButton = tkinter.ttk.Button(
            self.buttonFrame, text=self.addElementLabel,
            command=self.addElement)
        self.modifyButton = tkinter.ttk.Button(
            self.buttonFrame, text=self.modifyElementLabel,
            command=self.modifyElement)
        self.deleteButton = tkinter.ttk.Button(
            self.buttonFrame, text=self.deleteElementLabel,
            command=self.deleteElement)
        self.addButton.pack()
        self.modifyButton.pack()
        self.deleteButton.pack()
               
        self.buttonFrame.pack(fill=tkinter.X, side=tkinter.RIGHT)
        self.itemEntry.pack(fill=tkinter.X, side=tkinter.BOTTOM)
        self.itemListFrame.pack(fill=tkinter.X, side=tkinter.LEFT,
                                expand=True)

    def updateItem(self, ev=None):
        indexes  = self.itemList.curselection()
        if not indexes:
            return
        self.currentIndex = index = indexes[0]
        element = self.currentValue[index]
        if callable(self.objectToString):
            elementNew = self.objectToString
            if elementNew is not None:
                element = elementNew
            del elementNew
        self.itemEntry.delete('0', tkinter.END)
        self.itemEntry.insert('0', element)

    def addElement(self, ev=None):
        element = self.itemEntry.get()
        if not element.strip():
            return
        if callable(self.stringToObject):
            try:
                elementNew = self.stringToObject(element)
            except Exception as e:
                msgbox.showwarning("警告", str(e), parent=self.itemFrame)
                if callable(self.elementValueErrorHandler):
                    self.elementValueErrorHandler(e)
                return
            if elementNew is not None:
                element = elementNew
            del elementNew
        if element not in self.currentValue:
            self.currentValue.append(element)
            self.itemList.insert(tkinter.END, element)
        self.itemEntry.delete('0', tkinter.END)
        self.currentIndex = None

    def modifyElement(self, ev=None):
        indexes = self.itemList.curselection()
        if not indexes:
            if self.currentIndex is not None:
                index = self.currentIndex
                isSelected = self.itemList.select_includes(index)
                self.itemList.select_set(index)
                if not msgbox.askokcancel(
                    self.modifyElementLabel, "您上次选中该元素。是否修改？",
                    parent=self.itemFrame):
                    if callable(self.modifyElementHandler):
                        self.modifyElementHandler()
                    if not isSelected:
                        self.itemList.select_clear(index)
                    return
                if callable(self.modifyElementHandler):
                    self.modifyElementHandler()
            else:
                return
        else:
            index = indexes[0]
        element = self.itemEntry.get()
        if not element.strip():
            return
        if callable(self.stringToObject):
            try:
                elementNew = self.stringToObject(element)
            except Exception as e:
                msgbox.showwarning("警告", str(e), parent=self.itemFrame)
                if callable(self.elementValueErrorHandler):
                    self.elementValueErrorHandler(e)
                return
            if elementNew is not None:
                element = elementNew
            del elementNew
        del self.currentValue[index]
        self.itemList.delete(str(index))
        if element not in self.currentValue:
            self.currentValue.insert(index, element)
            self.itemList.insert(str(index), element)
        self.itemEntry.delete('0', tkinter.END)
        self.currentIndex = None

    def deleteElement(self, ev=None):
        indexes = self.itemList.curselection()
        if not indexes:
            return
        for index in sorted(indexes, reverse=True):
            del self.currentValue[index]
            self.itemList.delete(str(index))
        self.currentIndex = None

    def saveItem(self) -> str:
        self.settings.set(self.key, self.currentValue)
        return ""

    def checkItemModified(self) -> bool:
        return self.currentValue != self.originalValue

class CheckbuttonItem(SettingsItem):
    def initItemValueFrame(self, itemValue):
        pass
