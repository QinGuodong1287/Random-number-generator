import json
import os
import shutil

class DataStorage:
    """Provide data storage."""
    defaultStorage = {}
    
    def __init__(self, storageFile=r"data.json",
                 storageBackupFile=r"data.bak.json",
                 fileReadErrorHandler=None):
        if storageBackupFile == storageFile:
            raise ValueError("The storage backup file must be different from "
                             "storage file.")
        self.storageFile = str(storageFile)
        self.storageBackupFile = str(storageBackupFile)
        self.loadData(fileReadErrorHandler)

    def loadData(self, fileReadErrorHandler=None):
        if os.path.exists(self.storageFile):
            try:
                with open(self.storageFile, "r") as fp:
                    self.storage = json.load(fp)
            except json.decoder.JSONDecodeError:
                if callable(fileReadErrorHandler):
                    fileReadErrorHandler()
                self.storage = DataStorage.defaultStorage
                shutil.move(self.storageFile, self.storageBackupFile)
                with open(storageFile, "w") as fp:
                    json.dump(self.storage, fp)
        else:
            self.storage = DataStorage.defaultStorage
            with open(self.storageFile, "w") as fp:
                json.dump(self.storage, fp)
        self.storageModified = False

    def saveData(self):
        with open(self.storageFile, "w") as fp:
            json.dump(self.storage, fp, indent=4)
        self.storageModified = False

    @staticmethod
    def _validKey(key):
        if not key:
            raise ValueError("The `key` is empty.")
        elif not isinstance(key, (list, tuple)):
            raise TypeError("The `key` must be a list or a tuple "
                            "of the key path.")

    def getData(self, key, default=None):
        self._validKey(key)
        dic = self.storage
        for depth in range(len(key) - 1):
            if key[depth] not in dic:
                return default
            dic = dic[key[depth]]
        return dic.get(key[-1], default)

    def setData(self, key, value):
        self._validKey(key)
        dic = self.storage
        for depth in range(len(key) - 1):
            if key[depth] not in dic:
                dic[key[depth]] = {}
            dic = dic[key[depth]]
        dic[key[-1]] = value
        self.storageModified = True

    def deleteData(self, key):
        self._validKey(key)
        dic = self.storage
        for depth in range(len(key) - 1):
            if key[depth] not in dic:
                return
            dic = dic[key[depth]]
        if key[-1] not in dic:
            return
        del dic[key[-1]]
        self.storageModified = True

defaultStorage = DataStorage()
loadData = defaultStorage.loadData
saveData = defaultStorage.saveData
getData = defaultStorage.getData
setData = defaultStorage.setData
deleteData = defaultStorage.deleteData

loadData()
