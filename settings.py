import tkinter
import tkinter.ttk
import tkinter.messagebox as msgbox
import json
import os

class Settings:
    DEFAULT = {
        "random": [
            None,
            {
                "ignore_nums": [[], {}],
                "higher_level_nums": [[], {}]
            }
        ]
    }
    
    def __init__(self):
        self.settingsFile = r"settings.json"
        if not os.path.exists(self.settingsFile):
            with open(self.settingsFile, "w") as fp:
                json.dump(Settings.DEFAULT, fp)
        self.tempKeys = []
        self.tempSettings = {}
        self.modified = False
        self.loadSettings()
        # self.checkSettings()

    def loadSettings(self):
        with open(self.settingsFile, "r") as fp:
            self.settings = json.load(fp)
        self.modified = False
        
    def checkSettings(self):
        self.checkKey(["ui"], {})
        # self.set(["ui", "linesep"], "\n", temp=True)
        # self.set(["ui", "numsep"], " ", temp=True)
        self.checkKey(["ui", "nums_count_per_line"], 15)
        self.checkKey(["random"], {})
        self.checkKey(["random", "ignore_nums"], [])
        self.checkKey(["random", "higher_level_nums"], [])

    @staticmethod
    def _validKey(key):
        """`key` is a list or a tuple of the key path."""
        if not key:
            raise ValueError("The key path is empty.")
        if not isinstance(key, (list, tuple)):
            raise TypeError("`key` must be a list or a tuple of the key path.")
        
    def checkKey(self, key, default=None, autoFix=True, temp=False):
        Settings._validKey(key)
        if temp or key in self.tempKeys:
            dic = self.tempSettings
        else:
            dic = self.settings
        defDic = Settings.DEFAULT
        hasDefaultValue = True
        for depth in range(len(key) - 1):
            if key[depth] not in dic:
                if not autoFix:
                    return False
                dic[key[depth]] = [None, {}]
                if not temp:
                    self.modified = True
            if hasDefaultValue:
                if key[depth] in defDic:
                    defDic = defDic[key[depth]][1]
                else:
                    hasDefaultValue = False
            dic = dic[key[depth]][1]
        if key[-1] not in dic:
            if not autoFix:
                return False
            if hasDefaultValue and key[-1] in defDic:
                default = defDic[key[-1]][1]
            else:
                hasDefaultValue = False
            dic[key[-1]] = [default, {}]
            if temp:
                self.tempKeys.append(key)
            else:
                self.modified = True
            return False
        return True

    def set(self, key, value, autoFix=True, temp=False):
        Settings._validKey(key)
        self.checkKey(key, autoFix=autoFix, temp=temp)
        if temp or key in self.tempKeys:
            dic = self.tempSettings
        else:
            dic = self.settings
        for depth in range(len(key) - 1):
            dic = dic[key[depth]][1]
        dic[key[-1]][0] = value
        if temp:
            if key not in self.tempKeys:
                self.tempKeys.append(key)
        else:
            self.modified = True
            
    def get(self, key, default=None):
        self.checkKey(key, default)
        if key in self.tempKeys:
            dic = self.tempSettings
        else:
            dic = self.settings
        defDic = Settings.DEFAULT
        hasDefaultValue = True
        for depth in range(len(key) - 1):
            dic = dic[key[depth]][1]
            if hasDefaultValue:
                if key[depth] in defDic:
                    defDic = defDic[key[depth]][1]
                else:
                    hasDefaultValue = False
        if hasDefaultValue:
            if key[-1] in defDic:
                default = defDic[key[-1]][1]
            else:
                hasDefaultValue = False
        return dic[key[-1]][0] if key[-1] in dic else default

    def delete(self, key):
        Settings._validKey(key)
        if key in self.tempKeys:
            dic = self.tempSettings
        else:
            dic = self.settings
        for depth in range(len(key) - 1):
            if key[depth] not in dic:
                return
            dic = dic[key[depth]][1]
        if key[-1] not in dic:
            return
        del dic[key[-1]]
        if key not in self.tempKeys:
            self.modified = True

    def saveSettings(self):
        # print(self.settings, self.modified)
        # print(self.settings, self.tempKeys, self.tempSettings, sep='\n')
        if not self.modified:
            return
        with open(self.settingsFile, "w") as fp:
            json.dump(self.settings, fp, indent=4)
        self.modified = False

    def update(self, other):
        if not isinstance(other, Settings):
            raise TypeError("`other` must be a instance of Settings.")
        self.settings.update(other.settings)
        self.modified = True
