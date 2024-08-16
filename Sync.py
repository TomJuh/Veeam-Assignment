import os
import time
import hashlib
import sys


class Sync:
    # Utility functions
    def setLogFolderPath(self, logFolder):
        """
        Initial setup of log file path
        """
        if os.path.exists(logFolder):
            self.folderLPath = os.path.join(os.getcwd(), logFolder)
        else:
            print("\033[91mFile path doesn't exist\n\033[0m")
            exit(1)

    def setFolderSPath(self, sourceFolder):
        """
        Initial setup of source folder path
        """
        if os.path.exists(sourceFolder):
            self.folderSPath = os.path.join(os.getcwd(), sourceFolder)
        else:
            print("\033[91mFolder path doesn't exist\n\033[0m")
            exit(1)

    def setFolderRPath(self, replicaFolder):
        """
        Initial setup of replica folder path
        """
        if os.path.exists(replicaFolder):
            self.folderRPath = os.path.join(os.getcwd(), replicaFolder)
        else:
            print("\033[91mFolder path doesn't exist\n\033[0m")
            exit(1)

    def setInterval(self, interval):
        """
        Initial setup of interval value 
        """
        try:
            uInput = int(interval)
            self.interval = uInput
        except ValueError:
            print("\033[91mInput is not a number\n\033[0m")
            exit(1)

    def printHelp(self):
        """
        Display help information
        """
        print("To display this message again run the program with flag -h")
        print("Usage python3 Sync.py -[choosenFlag] [choosenValue]...")
        print("All variables must be set for program to run\n")
        print("\tset interval with -i [interval in seconds]")
        print("\tset source folder path with -sf [path to source folder]")
        print("\tset replica folder path -rf [path to replica folder]")
        print("\tset log file path -lf [path to log file]\n")
        print(
            "\033[91mApplication can be exited only with keyboard interrupt! - CTRL+C\033[0m")

    def tryToOpenFile(self, rights, path):
        """
        Utility function for safe file handling
        """
        try:
            return open(path, rights)
        except Exception as e:
            print(f"\033[91mCoudn't open file: {e}\n\033[0m")
            exit(1)

    def tryToWrite(self, pathW, pathR):
        """
        Utility function for safe file handling
        """
        try:
            pathW.write(pathR.read())
            pathW.close()
            pathR.close()
        except Exception as e:
            print(f"\033[91mCoudn't write to a file: {e}\n\033[0m")
            exit(1)

    def writeLogs(self, log):
        """
        Write changes to both output and log file
        """
        print(log)
        try:
            logFile = self.tryToOpenFile('a', self.folderLPath)
            logFile.write(log)
            logFile.close()
        except Exception as e:
            print(f"\033[91mCoudn't write to a log file: {e}\n\033[0m")

    # Main program functions
    def calMD5(self, filePath):
        """
        Calculates MD5 Hash for a specific file
        """
        hash_md5 = hashlib.md5()
        f = self.tryToOpenFile('rb', filePath)
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def md5OfFiles(self):
        """
        Creates two dictionaries and fills them with MD5 hashes of files
        Each dictionary represent a tracked folder
        MD5 hashes are used as values and filePaths as keys
        """
        f1MD5Dict = {}
        f2MD5Dict = {}
        for root, dirs, files in os.walk(self.folderSPath):
            for file in files:
                filePath = os.path.join(root, file)
                f1MD5Dict[filePath] = self.calMD5(filePath)
        for root, dirs, files in os.walk(self.folderRPath):
            for file in files:
                filePath = os.path.join(root, file)
                f2MD5Dict[filePath] = self.calMD5(filePath)

        return f1MD5Dict, f2MD5Dict

    def compareMd5(self, f1MD5, f2MD5):
        """
        Compares dictionaries of tracked folders
        Creates lists for all possible modifications
        If file is in source but not in replica add it to newFiles
        If it is in both folders but the hashes differ add it to modded
        If it is only in replica add it to delFiles
        """
        modFiles = []
        newFiles = []
        delFiles = []
        for filePath, md5Hash in f1MD5.items():
            fileName = os.path.basename(filePath)
            filePath = self.folderRPath + "/" + fileName
            if filePath in f2MD5:
                if f2MD5[filePath] != md5Hash:
                    modFiles.append(fileName)
            else:
                newFiles.append(fileName)

        for filePath, md5Hash in f2MD5.items():
            fileName = os.path.basename(filePath)
            filePath = self.folderSPath + "/" + fileName
            if md5Hash not in f1MD5.values() and fileName not in modFiles:
                delFiles.append(fileName)
        return modFiles, newFiles, delFiles

    def syncFiles(self, modFiles, newFiles, delFiles):
        """
        Syncs folders based on lists created in compareMd5
        List story only file name not whole path for easier manipulation
        Utility function for safer file handling are used
        """
        for file in modFiles:
            fileS = os.path.join(self.folderSPath, file)
            fileR = os.path.join(self.folderRPath, file)
            self.tryToWrite(self.tryToOpenFile('wb', fileR),
                            self.tryToOpenFile('r+b', fileS))
            self.writeLogs("File: " + file + " was modified")

        for file in newFiles:
            fileS = os.path.join(self.folderSPath, file)
            fileR = os.path.join(self.folderRPath, file)
            os.makedirs(os.path.dirname(fileR), exist_ok=True)
            if (not os.path.exists(fileS)):
                newFiles.pop(fileS, None)
                continue
            self.tryToWrite(self.tryToOpenFile('wb', fileR),
                            self.tryToOpenFile('r+b', fileS))
            self.writeLogs("File: " + file + " was created")

        for file in delFiles:
            os.remove(os.path.join(self.folderRPath, file))
            self.writeLogs("File: " + file + " was deleted")

    def printStartStatus(self):
        """
        Start of sync displays informations
        """
        print("Sync started with following values")
        print("Sync interval: "+str(self.interval))
        print("Source folder path: "+self.folderSPath)
        print("Replica folder path: "+self.folderLPath)
        print("Log file path: "+self.folderLPath)
        print("Now logging changes:\n")

    def periodicCheck(self):
        """
        Main loop periodically checks folders
        Can be exited only with KeyboardInterrupt
        """
        try:
            self.printStartStatus()
            while True:
                f1MD5, f2MD5 = self.md5OfFiles()
                modFiles, newFiles, delFiles = self.compareMd5(
                    f1MD5, f2MD5)
                self.syncFiles(modFiles, newFiles, delFiles)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("Goodbye!")

    def setup(self):
        """
        Initial setup
        Parse arguments
        Display help info and welcome user
        Set-up run variables based on arguments
        Start main loop
        """
        argLen = len(sys.argv)
        if argLen == 1:
            print("This is a simple synchronization tool")
            print("It maintains copy of files of one folder in another")
            print("Welcome to the sync tool.")
            print("Please set up folder paths and sync interval with following flags:")
            self.printHelp()
            exit(0)
        argIndex = 1
        while argIndex < argLen:
            func = self.argsSwitch.get(sys.argv[argIndex])
            if func:
                func(sys.argv[argIndex + 1])
                argIndex += 2
            else:
                print("\033[91mIncorrect argument\n\033[0m")
                self.printHelp()
                exit(1)

        self.periodicCheck()

    def __init__(self):
        """
        Class variable constructor
        """
        self.interval = 30
        self.folderSPath = os.path.join(os.getcwd(), "source")
        self.folderRPath = os.path.join(os.getcwd(), "replica")
        self.folderLPath = os.path.join(os.getcwd(), "log")
        self.argsSwitch = {
            'help': self.printHelp,
            '-h': self.printHelp,
            '-i': self.setInterval,
            '-rf': self.setFolderRPath,
            '-sf': self.setFolderSPath,
            '-lf': self.setLogFolderPath
        }


if __name__ == "__main__":
    sync = Sync()
    sync.setup()
