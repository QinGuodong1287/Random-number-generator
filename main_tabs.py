import random
import tkinter
import tkinter.ttk
import tkinter.messagebox as msgbox
import functools
import traceback

from app_core import generateSingleGroupNumbers, generateWithHigherLevelNumbers
import data_storage
from exceptions import RangeException, EntryException
from basic_module import findNum
import logger
import constants
from logger import logCall

class Tab:
    def __init__(self, master, notebook, settings, text,
                 openResultBoardFunc=None, checkResultBoardExistsFunc=None,
                 setResultToBoardFunc=None, closeResultBoardFunc=None):
        self.settings = settings
        self.master = master
        self.openResultBoardFunc = openResultBoardFunc
        self.checkResultBoardExistsFunc = checkResultBoardExistsFunc
        self.setResultToBoardFunc = setResultToBoardFunc
        self.closeResultBoardFunc = closeResultBoardFunc
        self.lastResult = ""
        self.mainFrame = tkinter.Frame(master)
        logCall(self.initWidgets)
        self.mainFrame.pack(fill=tkinter.BOTH, side=tkinter.TOP, expand=True)
        notebook.add(self.mainFrame, text=text)

    def initWidgets(self):
        """Custom your tab."""
        pass

    def openResultBoard(self, text=""):
        if not callable(self.openResultBoardFunc):
            return
        self.openResultBoardFunc(text)

    def checkResultBoardExists(self):
        if not callable(self.checkResultBoardExistsFunc):
            return
        if self.checkResultBoardExistsFunc():
            self.resultBoardButton.config(
                text="关闭放大显示结果", command=self.closeResultBoard)
        else:
            self.resultBoardButton.config(
                text="放大显示结果", command=self.showResultOnBoard)

    def setResultToBoard(self, text):
        if not callable(self.setResultToBoardFunc):
            return
        self.setResultToBoardFunc(text)

    def showResultOnBoard(self, ev=None):
        self.resultBoardButton.config(
            text="关闭放大显示结果", command=self.closeResultBoard)
        self.openResultBoard(self.lastResult)

    def closeResultBoard(self, ev=None):
        self.resultBoardButton.config(
            text="放大显示结果", command=self.showResultOnBoard)
        if not callable(self.closeResultBoardFunc):
            return
        self.closeResultBoardFunc()

    def initResultFrame(self):
        self.resultFrame = tkinter.Frame(self.mainFrame)
        self.resultTipLabel = tkinter.Label(self.resultFrame,
                                            text="随机数生成结果：")
        self.resultTipLabel.pack(fill=tkinter.X, side=tkinter.TOP, expand=True)
        self.resultLabel = tkinter.Label(self.resultFrame, text="")
        self.resultLabel.pack(fill=tkinter.BOTH, side=tkinter.BOTTOM,
                              expand=True)
        self.resultFrame.pack(fill=tkinter.BOTH, side=tkinter.TOP, expand=True)
        self.buttonFrame = tkinter.Frame(self.mainFrame)
        self.resultBoardButton = tkinter.Button(
            self.buttonFrame, text="放大显示结果",
            command=self.showResultOnBoard)
        self.resultBoardButton.pack(side=tkinter.RIGHT)
        self.buttonFrame.pack(fill=tkinter.X, side=tkinter.BOTTOM)

    def tabSwitched(self):
        """The function called when the tab is switched."""
        self.checkResultBoardExists()

    def generateSub(self) -> str:
        """Return result string."""
        return ""

    def generate(self, ev=None):
        result = str(self.generateSub())
        self.setResultToBoard(result)
        self.lastResult = result

    def saveData(self):
        pass

class SingleGroupNumberTab(Tab):
    def initWidgets(self):
        self.configureFrame = tkinter.Frame(self.mainFrame)
        
        self.countFrame = tkinter.Frame(self.configureFrame)
        self.countLabel = tkinter.Label(self.countFrame, text="随机数个数：")
        self.countLabel.pack(side=tkinter.LEFT)
        self.countEntry = tkinter.Entry(self.countFrame)
        try:
            numCount = data_storage.getData(
                ["single_number_range", "num_count"])
            if numCount:
                self.countEntry.insert('0', str(numCount))
        except ValueError:
            pass
        self.countEntry.pack(side=tkinter.RIGHT, fill=tkinter.X, expand=True)
        self.countFrame.pack(fill=tkinter.X, side=tkinter.TOP, expand=True)

        self.rangeMinFrame = tkinter.Frame(self.configureFrame)
        self.rangeMinLabel = tkinter.Label(self.rangeMinFrame,
                                           text="随机数范围最小值：")
        self.rangeMinLabel.pack(side=tkinter.LEFT)
        self.rangeMinEntry = tkinter.Entry(self.rangeMinFrame)
        try:
            rangeMin = data_storage.getData(
                ["single_number_range", "range_min"])
            if rangeMin:
                self.rangeMinEntry.insert('0', str(rangeMin))
        except ValueError:
            pass
        self.rangeMinEntry.pack(fill=tkinter.X, side=tkinter.RIGHT, expand=True)
        self.rangeMinFrame.pack(fill=tkinter.X, side=tkinter.TOP, expand=True)

        self.rangeMaxFrame = tkinter.Frame(self.configureFrame)
        self.rangeMaxLabel = tkinter.Label(self.rangeMaxFrame,
                                           text="随机数范围最大值：")
        self.rangeMaxLabel.pack(side=tkinter.LEFT)
        self.rangeMaxEntry = tkinter.Entry(self.rangeMaxFrame)
        try:
            rangeMax = data_storage.getData(
                ["single_number_range", "range_max"])
            if rangeMax:
                self.rangeMaxEntry.insert('0', str(rangeMax))
        except ValueError:
            pass
        self.rangeMaxEntry.pack(fill=tkinter.X, side=tkinter.RIGHT, expand=True)
        self.rangeMaxFrame.pack(fill=tkinter.X, side=tkinter.TOP, expand=True)

        self.configureFrame.pack(fill=tkinter.BOTH, side=tkinter.TOP,
                                 expand=True)

        self.initResultFrame()

        self.chosenNums = data_storage.getData(["chosen_nums"], [])

    def generateSub(self, ev=None):
        finished = False
        try:
            totalStr = self.countEntry.get()
            rangeMinStr = self.rangeMinEntry.get()
            rangeMaxStr = self.rangeMaxEntry.get()
            if not totalStr or not rangeMinStr or not rangeMaxStr:
                raise EntryException("输入错误：部分输入项为空。")
            total = int(totalStr)
            rangeMin = int(rangeMinStr)
            rangeMax = int(rangeMaxStr)
            ignoreNums = self.settings.get(["random", "ignore_nums"])
            higherLevelNums = self.settings.get(["random", "higher_level_nums"])
            try:
                resultList = generateWithHigherLevelNumbers(
                    rangeMin, rangeMax, total, ignoreNums, higherLevelNums)
            except ValueError as e:
                result = str(e)
                finished = True
                raise e
            linesep = constants.linesep
            numsep = constants.numsep
            numsPerLine = self.settings.get(["ui", "nums_count_per_line"], 15)
            lines = []
            sectionNum = 0
            count = len(resultList)
            while count > 0:
                lines.append(numsep.join(
                    (str(num) for num in \
                     resultList[sectionNum * numsPerLine : \
                                (sectionNum + 1) * numsPerLine])))
                sectionNum += 1
                count -= numsPerLine
            result = linesep.join(lines)
            finished = True
        except EntryException as e:
            result = str(e)
            finished = True
        except ValueError as e:
            if not finished:
                result = "数值错误：输入的数据不是整数。请检查输入。"
                finished = True
        except RangeException as e:
            result = str(e)
            finished = True
        except Exception:
            logger.flushErrorToBuffer()
            result = "程序出现异常。"
            finished = True
        self.resultLabel.config(text=result)
        return result

    def saveData(self):
        rangeDataStr = {
            "num_count": self.countEntry.get(),
            "range_min": self.rangeMinEntry.get(),
            "range_max": self.rangeMaxEntry.get()}
        rangeData = {}
        for key, value in rangeDataStr.items():
            try:
                itemValue = int(value)
            except ValueError:
                itemValue = None
            rangeData[key] = itemValue
        data_storage.setData(["single_number_range"], rangeData)

class MultiGroupsNumberTab(Tab):
    def initWidgets(self):
        self.ranges = []
        self.columns = columns = ("范围最小值", "范围最大值", "抽取数字个数")

        self.configureFrame = tkinter.Frame(self.mainFrame)

        self.rangesListFrame = tkinter.Frame(self.configureFrame)
        
        self.rangesListView = tkinter.ttk.Treeview(
            self.rangesListFrame, columns=columns, # show="headings",
            selectmode="browse")

        self.rangesListYScroll = tkinter.Scrollbar(
            self.rangesListFrame, orient=tkinter.VERTICAL,
            command=self.rangesListView.yview)
        self.rangesListView.config(yscrollcommand=self.rangesListYScroll.set)
        self.rangesListYScroll.pack(fill=tkinter.Y, side=tkinter.RIGHT)
                
        self.rangesListXScroll = tkinter.Scrollbar(
            self.rangesListFrame, orient=tkinter.HORIZONTAL,
            command=self.rangesListView.xview)
        self.rangesListView.config(xscrollcommand=self.rangesListXScroll.set)
        self.rangesListXScroll.pack(fill=tkinter.X, side=tkinter.BOTTOM)

        defaultColumnWidth = 100
        for column in columns:
            self.rangesListView.heading(column=column, text=column,
                                        anchor=tkinter.CENTER)
            self.rangesListView.column(column=column, anchor=tkinter.CENTER,
                                       width=defaultColumnWidth, minwidth=80)
        self.rangesListView.pack(fill=tkinter.BOTH, side=tkinter.TOP,
                                 expand=True)

        self.rangesListFrame.pack(fill=tkinter.BOTH, side=tkinter.LEFT,
                                  expand=True)

        self.buttonFrame = tkinter.Frame(self.configureFrame)
        self.addButton = tkinter.Button(
            self.buttonFrame, text="添加范围", command=self.addRange)
        self.addButton.pack()
        self.modifyButton = tkinter.Button(
            self.buttonFrame, text="修改范围", command=self.modifyRange)
        self.modifyButton.pack()
        self.removeButton = tkinter.Button(
            self.buttonFrame, text="删除范围", command=self.removeRange)
        self.removeButton.pack()
        self.buttonFrame.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=True)

        self.configureFrame.pack(fill=tkinter.BOTH, side=tkinter.TOP,
                                 expand=True)

        self.initResultFrame()

        for data in data_storage.getData(["multi_number_ranges"], []):
            self.addRangeItem(data)

        # self.insertTestData()

        self.modifierWindow = None

    def _validIndex(self, index, allowNone=True):
        if index is not None:
            if not (0 <= index < len(self.ranges)):
                raise IndexError("The index {} is out of range.".format(index))
        else:
            if not allowNone:
                raise ValueError("The index is None.")

    def addRangeItem(self, data, index=None):
        self._validIndex(index)
        if not data:
            return
        rangeData = {key: value for key, value in data.items()}
        item = self.rangesListView.insert(
            '', index if index else tkinter.END, text=data["label"],
            values=(rangeData["range_min"], rangeData["range_max"],
                    rangeData["num_count"]))
        rangeData["item"] = item
        if index:
            self.ranges.insert(index, rangeData)
        else:
            self.ranges.append(rangeData)

    def modifyRangeItem(self, data, index):
        self._validIndex(index, False)
        rangeData = self.ranges[index]
        if "item" not in rangeData:
            return
        item = rangeData["item"]
        item = self.rangesListView.item(
            item, text=data["label"],
            values=(data["range_min"], data["range_max"], data["num_count"]))
        rangeData["range_min"] = data["range_min"]
        rangeData["range_max"] = data["range_max"]
        rangeData["num_count"] = data["num_count"]
        rangeData["item"] = item

    def removeRangeItem(self, index):
        self._validIndex(index)
        item = self.ranges[index]["item"]
        self.rangesListView.delete(item)
        del self.ranges[index]

    def insertTestData(self):
        testData = [
            ["全班", 1, 54, 5],
            ["女生", 1, 17, 1],
            ["男生", 18, 54, 1]]
        for data in testData:
            self.addRangeItem({"label": data[0],
                               "range_min": data[1],
                               "range_max": data[2],
                               "num_count": data[3]})

    class RangeModifier:
        def __init__(self, master, rangesList, rangeIndex=None,
                     title="范围修改", x=None, y=None):
            if rangeIndex is not None:
                if not (isinstance(rangeIndex, int) and \
                   0 <= rangeIndex < len(rangesList)):
                    rangeIndex = None
            self.top = tkinter.Toplevel(master)
            self.top.title(title)
            # self.top.attributes("-topmost", True)
            self.master = master
            window_width = 250
            window_height = 150
            window_x = x or (self.top.winfo_screenwidth() - window_width) // 2
            window_y = y or (self.top.winfo_screenheight() - window_height) // 2
            self.top.geometry("{width}x{height}+{x}+{y}".format(
                width=window_width, height=window_height,
                x=window_x, y=window_y))

            self.labelFrame = tkinter.Frame(self.top)
            self.labelLabel = tkinter.Label(self.labelFrame, text="范围标签：")
            self.labelLabel.pack(fill=tkinter.X, side=tkinter.LEFT)
            self.labelEntry = tkinter.Entry(self.labelFrame)
            if rangeIndex is not None:
                label = rangesList[rangeIndex]["label"]
                if label:
                    self.labelEntry.insert('0', str(label))
            self.labelEntry.pack(fill=tkinter.X, side=tkinter.RIGHT,
                                 expand=True)
            self.labelFrame.pack(fill=tkinter.X, side=tkinter.TOP, expand=True)

            self.rangeMinFrame = tkinter.Frame(self.top)
            self.rangeMinLabel = tkinter.Label(self.rangeMinFrame,
                                               text="范围最小值：")
            self.rangeMinLabel.pack(fill=tkinter.X, side=tkinter.LEFT)
            self.rangeMinEntry = tkinter.Entry(self.rangeMinFrame)
            if rangeIndex is not None:
                rangeMin = rangesList[rangeIndex]["range_min"]
                if rangeMin:
                    self.rangeMinEntry.insert('0', str(rangeMin))
            self.rangeMinEntry.pack(fill=tkinter.X, side=tkinter.RIGHT,
                                    expand=True)
            self.rangeMinFrame.pack(fill=tkinter.X, side=tkinter.TOP,
                                    expand=True)

            self.rangeMaxFrame = tkinter.Frame(self.top)
            self.rangeMaxLabel = tkinter.Label(self.rangeMaxFrame,
                                               text="范围最大值：")
            self.rangeMaxLabel.pack(fill=tkinter.X, side=tkinter.LEFT)
            self.rangeMaxEntry = tkinter.Entry(self.rangeMaxFrame)
            if rangeIndex is not None:
                rangeMax = rangesList[rangeIndex]["range_max"]
                if rangeMax:
                    self.rangeMaxEntry.insert('0', str(rangeMax))
            self.rangeMaxEntry.pack(fill=tkinter.X, side=tkinter.RIGHT,
                                    expand=True)
            self.rangeMaxFrame.pack(fill=tkinter.X, side=tkinter.TOP,
                                    expand=True)

            self.numCountFrame = tkinter.Frame(self.top)
            self.numCountLabel = tkinter.Label(self.numCountFrame,
                                               text="随机数个数：")
            self.numCountLabel.pack(fill=tkinter.X, side=tkinter.LEFT)
            self.numCountEntry = tkinter.Entry(self.numCountFrame)
            if rangeIndex is not None:
                numCount = rangesList[rangeIndex]["num_count"]
                if numCount:
                    self.numCountEntry.insert('0', str(numCount))
            self.numCountEntry.pack(fill=tkinter.X, side=tkinter.RIGHT,
                                    expand=True)
            self.numCountFrame.pack(fill=tkinter.X, side=tkinter.TOP,
                                    expand=True)

            self.buttonFrame = tkinter.Frame(self.top)
            self.cancelButton = tkinter.Button(self.buttonFrame, text="取消",
                                               command=self.quit)
            self.cancelButton.pack(side=tkinter.RIGHT)
            self.okButton = tkinter.Button(
                self.buttonFrame, text="确认",
                command=functools.partial(self.quit, generateData=True))
            self.okButton.pack(side=tkinter.RIGHT)
            self.buttonFrame.pack(fill=tkinter.X, side=tkinter.BOTTOM,
                                  expand=True)

            self.rangeData = None

            self.top.protocol("WM_DELETE_WINDOW", self.quit)
            self.focus()

        def mainloop(self):
            self.top.mainloop()
            return self.rangeData

        def focus(self):
            self.top.deiconify()
            self.top.focus()

        def quit(self, ev=None, generateData=False):
            if generateData:
                try:
                    label = self.labelEntry.get()
                    rangeMin = int(self.rangeMinEntry.get())
                    rangeMax = int(self.rangeMaxEntry.get())
                    numCount = int(self.numCountEntry.get())
                except ValueError:
                    msgbox.showwarning("警告", "数据有误，请检查。",
                                       parent=self.top)
                    self.focus()
                    return
                self.rangeData = {
                    "label": label,
                    "range_min": rangeMin,
                    "range_max": rangeMax,
                    "num_count": numCount
                    }
            self.top.quit()
            self.top.destroy()

    def openModifierWindow(self, rangeIndex=None, title="范围修改"):
        if self.modifierWindow:
            self.modifierWindow.focus()
            return
        self.modifierWindow = MultiGroupsNumberTab.RangeModifier(
            self.master, self.ranges, rangeIndex, title=title,
            x=self.master.winfo_x(), y=self.master.winfo_y())
        rangeData = self.modifierWindow.mainloop()
        del self.modifierWindow
        self.modifierWindow = None
        return rangeData

    def addRange(self, ev=None):
        data = self.openModifierWindow(None, "范围添加")
        if data is None:
            return
        self.addRangeItem(data)

    def modifyRange(self, ev=None):
        selection = self.rangesListView.selection()
        if not selection:
            msgbox.showinfo("修改范围", "请先选中要修改的范围。",
                            parent=self.mainFrame)
            return
        item = selection[0]
        index = self.rangesListView.index(item)
        data = self.openModifierWindow(index)
        if not data:
            return
        self.modifyRangeItem(data, index)

    def removeRange(self, ev=None):
        rangeItems = self.rangesListView.selection()
        if not rangeItems:
            msgbox.showinfo("删除范围", "请先选中要删除的范围。",
                            parent=self.mainFrame)
            return
        if msgbox.askokcancel("删除范围", "确认删除该范围？",
                              parent=self.mainFrame):
            for item in reversed(rangeItems):
                index = self.rangesListView.index(item)
                self.removeRangeItem(index)

    def generateSub(self, ev=None):
        try:
            resultLines = []
            numsep = constants.numsep
            linesep = constants.linesep
            ignoreNums = self.settings.get(["random", "ignore_nums"])
            higherLevelNums = self.settings.get(["random", "higher_level_nums"])
            for index, rangeData in enumerate(self.ranges, start=1):
                label = rangeData["label"]
                rangeMin = rangeData["range_min"]
                rangeMax = rangeData["range_max"]
                numCount = rangeData["num_count"]
                numbers = generateWithHigherLevelNumbers(
                    rangeMin, rangeMax, numCount, ignoreNums, higherLevelNums)
                resultLines.append(
                    "范围 {index}（[{range_min}, {range_max}]）：{numbers}"\
                    .format(
                        index=(label if label else index),
                        range_min=rangeMin, range_max=rangeMax,
                        numbers=numsep.join((str(num) for num in numbers))))
            result = linesep.join(resultLines)
        except ValueError as e:
            result = str(e)
        except Exception:
            logger.flushErrorToBuffer()
            traceback.print_exc()
            result = "程序出现异常。"
        self.resultLabel.config(text=result)
        return result

    def saveData(self):
        data_storage.setData(["multi_number_ranges"],
                             [{"label": data["label"],
                               "range_min": data["range_min"],
                               "range_max": data["range_max"],
                               "num_count": data["num_count"]} \
                              for data in self.ranges])
