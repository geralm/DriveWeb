from CommandPatter import CreateFile, Login, CreateDirectory, ChangeDirectory, ListDirectory, ModifyFile, OpenFile, Copy, Move, Delete, Share
from Files.FileManager import FileManager
class CommandManager():

    def __init__(self):
        self.__commandList: dict = {}
        self.BD: FileManager = FileManager()

    def addCommand(self, name: str , command):
        self.__commandList[name] =  command
    def getCommand(self, name: str):
        return self.__commandList[name]
    def addAllCommands(self):
        self.addCommand('cr', CreateFile())
        self.addCommand('lg', Login())
        self.addCommand('cf', CreateFile())
        self.addCommand('cdir', CreateDirectory())
        self.addCommand('cd', ChangeDirectory())
        self.addCommand('ls', ListDirectory())
        self.addCommand('mf', ModifyFile())
        self.addCommand('open', OpenFile())
        self.addCommand('cp', Copy())# -rv -vr -vv 
        self.addCommand('mv', Move()) 
        self.addCommand('del', Delete())
        self.addCommand('share', Share())


manager = CommandManager()
comando = manager.getCommand('cr')
comando.execute()