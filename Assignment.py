import os
import sys
import time
import hashlib
import threading

class Sync:
    def writeLogs(self, log):
         print("\n"+log+">",end="")
         with open(self.folderLPath, 'a') as file:
            file.write(log)

    def calMD5(self, filePath):
        hash_md5 = hashlib.md5()
        with open(filePath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def md5OfFiles(self):
        f1MD5Dict = {}
        f2MD5Dict = {}
        for root, dirs, files in os.walk(self.folderSPath):
            for file in files:
                filePath = os.path.join(root, file)
                f1MD5Dict [filePath] = self.calMD5(filePath)
        for root, dirs, files in os.walk(self.folderRPath):
            for file in files:
                filePath = os.path.join(root, file)
                f2MD5Dict [filePath] = self.calMD5(filePath)

        return f1MD5Dict, f2MD5Dict 

    def compareMd5(self, f1MD5, f2MD5):
        modFiles = []
        newFiles = []
        delFiles = []
        for filePath, md5Hash in f1MD5.items():
            filePath = filePath.replace('source','replica')
            if filePath in f2MD5:
                if f2MD5[filePath] != md5Hash:
                    modFiles.append(os.path.basename(filePath))
            else:
                newFiles.append(os.path.basename(filePath))

        for filePath in f2MD5:
            filePath = filePath.replace('replica','source')
            if md5Hash not in f1MD5.values():
                delFiles.append(os.path.basename(filePath))
        return modFiles, newFiles, delFiles

    def syncFiles(self, modFiles, newFiles, delFiles):
        for file in modFiles:
            fileS = os.path.join(self.folderSPath, file)
            fileR = os.path.join(self.folderRPath, file)
            with open(fileS, 'r+b') as f1, open(fileR, 'wb') as f2:
                f2.write(f1.read())
            self.writeLogs("File: " + fileS + " was modified\n")

        for file in newFiles:
            srcFile= os.path.join(self.folderSPath, file)
            destFile = os.path.join(self.folderRPath, file)
            os.makedirs(os.path.dirname(destFile), exist_ok=True)
            if (not os.path.exists(srcFile)):
                newFiles.pop(srcFile,None)
            with open(srcFile, 'rb') as f1, open(destFile, 'wb') as f2:
                f2.write(f1.read())
            self.writeLogs("File: " + file + " was created\n")

        for file in delFiles:
            os.remove(os.path.join(self.folderRPath, file))
            self.writeLogs("File: " + file + " was deleted\n")

    def createStartFiles(self):
        if not os.path.exists(self.folderSPath):
            os.mkdir(self.folderSPath)
        if not os.path.exists(self.folderRPath):
            os.mkdir(self.folderRPath)
        if not os.path.exists(self.folderRPath):
            with open(self.folderRPath, 'w') as file:
                file.write("")



    def periodicCheck(self, stopSync):
        while not stopSync.is_set():
            f1MD5, f2MD5 = self.md5OfFiles()
            modFiles, newFiles, delFiles = self.compareMd5(f1MD5, f2MD5)
            self.syncFiles(modFiles, newFiles, delFiles)
            time.sleep(self.interval)

    def inputLoop(self, stopSync):
        while True:
            userInput = input(">")
            lastGT = userInput.rfind(">")
            inputExtracted = userInput[lastGT + 1:]
            func = self.argsSwitch.get(inputExtracted.strip())
            if func:
                if inputExtracted == 'exit':
                    stopSync.set()
                func() 
            else:
                print ("Invalid Command\n")
                self.printHelp()
            


    def setLogFolderPath(self):
        uInput = input("Set log folder path to: ")
        if os.path.exists(uInput):
            self.folderLPath = uInput
        else:
            print ("File path doesn't exist")

    def setFolderSPath(self):
        uInput  = input("Set source folder path to: ")
        if os.path.exists(uInput):
            self.folderSPath = uInput
        else:
            print ("File path doesn't exist")

    def setFolderRPath(self):
        uInput = input("Set replica folder path to: ")
        if os.path.exists(uInput):
            self.folderRPath = uInput
        else:
            print ("File path doesn't exist")


    def setInterval(self):
        uInput = input("Set Interval to: ")
        try: 
            uInput = int(uInput)
            self.interval = uInput
        except ValueError:
            print ("Input is not a number")

    def printLogFolderPath(self):
        print (self.folderLPath)

    def printInterval(self):
        print (self.interval)

    def printFolderPath(self):
        print ("Source: " + self.folderSPath)
        print ("Replica: " + self.folderRPath)

    def printHelp(self):
        print ("This is a simple synchronization tool, that allows for setting of intervals and folder paths")
        print ("List of available commands:")
        print ("\texit: to exit the application") 
        print ("\thelp or -h: to display this message") 
        print ("\tshow folders path or -sh f: to display source and replica folder paths") 
        print ("\tshow log folder path or -sh l: to display log folder path") 
        print ("\tshow interval or -sh i: to show interval value") 
        print ("\tset interval or -set i: to set interval value") 
        print ("\tset folder source path or -set fs: to source folder path") 
        print ("\tset folder replica path or -set fr: to replica folder path") 
        print ("\tset folder log path or -set fl: to replica folder path") 
        
    def exitApplication(self):
        print("exiting")
        exit(0)

    def setup(self):
        print("Welcome to the sync tool./n Would you like to choose the source/replica and log folders path\n or use default setting (create folders and file inside of script folder)?")
        startInput = input("Press Y to set paths or N for default paths:\n")
        if (startInput == 'Y'):
            self.folderSPath = input("Please input source file path")
            self.folderRPath = input("Please input replica file path")
            self.folderLPath = input("Please input log file path")
        self.createStartFiles()
        self.printHelp()
        stopSync= threading.Event()
        syncLoop = threading.Thread(target=self.periodicCheck, args=(stopSync,))
        syncLoop.start()
        print("Please enter a command\n")
        self.inputLoop(stopSync)
        syncLoop.join()



    def __init__(self):
        self.interval = 3
        self.folderSPath = os.path.join(os.getcwd(), "source")
        self.folderRPath = os.path.join(os.getcwd(), "replica")
        self.folderLPath = os.path.join(os.getcwd(), "log")
        self.argsSwitch = {
            'help': self.printHelp,
            '-h': self.printHelp,
            'exit': self.exitApplication,
            'show folders path': self.printFolderPath,
            '-sh f': self.printFolderPath,
            'show interval': self.printInterval,
            '-sh i': self.printInterval,
            'show log folder path': self.printLogFolderPath,
            '-sh l': self.printLogFolderPath,
            'set interval': self.setInterval,
            '-set i': self.setInterval,
            'set source folder path': self.setFolderRPath,
            '-set fs p': self.setFolderRPath,
            'set replica folder path': self.setFolderRPath,
            '-set fr p': self.setFolderRPath,
            'set log folder path': self.setLogFolderPath,
            '-set fl p': self.setLogFolderPath
        }
       
def main():
    sync = Sync()
    sync.setup()

if __name__ == "__main__":
    main()