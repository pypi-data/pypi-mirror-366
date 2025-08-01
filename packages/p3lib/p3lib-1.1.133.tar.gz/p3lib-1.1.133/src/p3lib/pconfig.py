#!/bin/sh/env python3

import  os
import  base64
import  datetime
import  sys
import  json
import  copy
import  platform

from    shutil import copyfile

from    os.path import join, expanduser, getmtime, basename, isdir, isfile
from    .helper import getHomePath

class ConfigManager(object):
    """@brief Responsible for storing and loading configuration.
              Also responsible for providing methods that allow users to enter
              configuration."""

    UNSET_VALUE                 = "UNSET"
    DECIMAL_INT_NUMBER_TYPE     = 0
    HEXADECIMAL_INT_NUMBER_TYPE = 1
    FLOAT_NUMBER_TYPE           = 2
    SSH_FOLDER                  = ".ssh"
    PRIVATE_SSH_KEY_FILENAME    = "id_rsa"

    @staticmethod
    def GetString(uio, prompt, previousValue, allowEmpty=True):
      """@brief              Get a string from the the user.
         @param uio          A UIO (User Inpu Output) instance.
         @param prompt       The prompt presented to the user in order to enter
                             the float value.
         @param previousValue The previous value of the string.
         @param allowEmpty   If True then allow the string to be empty."""
      _prompt = prompt
      try:
          prompt = "%s (%s)" % (prompt, previousValue)
      except ValueError:
          prompt = "%s" % (prompt)

      while True:

        response = uio.getInput("%s" % (prompt))

        if len(response) == 0:

            if allowEmpty:

                if len(previousValue) > 0:
                    booleanResponse = uio.getInput("Do you wish to enter the previous value '%s' y/n: " % (previousValue) )
                    booleanResponse=booleanResponse.lower()
                    if booleanResponse == 'y':
                        response = previousValue
                        break

                booleanResponse = uio.getInput("Do you wish to clear '%s' y/n: " % (_prompt) )
                booleanResponse=booleanResponse.lower()
                if booleanResponse == 'y':
                    break
                else:
                    uio.info("A value is required. Please enter a value.")

            else:

                booleanResponse = uio.getInput("Do you wish to enter the previous value of %s y/n: " % (previousValue) )
                booleanResponse=booleanResponse.lower()
                if booleanResponse == 'y':
                    response = previousValue
                    break
        else:
            break

      return response

    @staticmethod
    def IsValidDate(date):
        """@brief determine if the string is a valid date.
           @param date in the form DAY/MONTH/YEAR (02:01:2018)"""
        validDate = False
        if len(date) >= 8:
            elems = date.split("/")
            try:
                day = int(elems[0])
                month = int(elems[1])
                year = int(elems[2])
                datetime.date(year, month, day)
                validDate = True
            except ValueError:
                pass
        return validDate

    @staticmethod
    def GetDate(uio, prompt, previousValue, allowEmpty=True):
        """@brief Input a date in the format DAY:MONTH:YEAR"""
        if not ConfigManager.IsValidDate(previousValue):
            today =  datetime.date.today()
            previousValue = today.strftime("%d/%m/%Y")
        while True:
            newValue = ConfigManager.GetString(uio, prompt, previousValue, allowEmpty=allowEmpty)
            if ConfigManager.IsValidDate(newValue):
                return newValue

    @staticmethod
    def IsValidTime(theTime):
        """@brief determine if the string is a valid time.
           @param theTime in the form HOUR:MINUTE:SECOND (12:56:01)"""
        validTime = False
        if len(theTime) >= 5:
            elems = theTime.split(":")
            try:
                hour = int(elems[0])
                minute = int(elems[1])
                second = int(elems[2])
                datetime.time(hour, minute, second)
                validTime = True
            except ValueError:
                pass
        return validTime

    @staticmethod
    def GetTime(uio, prompt, previousValue, allowEmpty=True):
        """@brief Input a time in the format HOUR:MINUTE:SECOND"""
        if not ConfigManager.IsValidTime(previousValue):
            today =  datetime.datetime.now()
            previousValue = today.strftime("%H:%M:%S")
        while True:
            newValue = ConfigManager.GetString(uio, prompt, previousValue, allowEmpty=allowEmpty)
            if ConfigManager.IsValidTime(newValue):
                return newValue

    @staticmethod
    def _GetNumber(uio, prompt, previousValue=UNSET_VALUE, minValue=UNSET_VALUE, maxValue=UNSET_VALUE, numberType=FLOAT_NUMBER_TYPE, radix=10):
      """@brief              Get float repsonse from user.
         @param uio          A UIO (User Inpu Output) instance.
         @param prompt       The prompt presented to the user in order to enter
                             the float value.
         @param previousValue The previous number value.
         @param minValue     The minimum acceptable value.
         @param maxValue     The maximum acceptable value.
         @param numberType   The type of number."""

      if numberType == ConfigManager.DECIMAL_INT_NUMBER_TYPE:

          radix=10

      elif numberType == ConfigManager.HEXADECIMAL_INT_NUMBER_TYPE:

          radix = 16

      while True:

        response = ConfigManager.GetString(uio, prompt, previousValue, allowEmpty=False)

        try:

            if numberType == ConfigManager.FLOAT_NUMBER_TYPE:

                value = float(response)

            else:

                value = int(str(response), radix)

            if minValue != ConfigManager.UNSET_VALUE and value < minValue:

                if radix == 16:
                    minValueStr = "0x%x" % (minValue)
                else:
                    minValueStr = "%d" % (minValue)

                uio.info("%s is less than the min value of %s." % (response, minValueStr) )
                continue

            if maxValue != ConfigManager.UNSET_VALUE and value > maxValue:

                if radix == 16:
                    maxValueStr = "0x%x" % (maxValue)
                else:
                    maxValueStr = "%d" % (maxValue)

                uio.info("%s is greater than the max value of %s." % (response, maxValueStr) )
                continue

            return value

        except ValueError:

            if numberType == ConfigManager.FLOAT_NUMBER_TYPE:

                uio.info("%s is not a valid number." % (response) )

            elif numberType == ConfigManager.DECIMAL_INT_NUMBER_TYPE:

                uio.info("%s is not a valid integer value." % (response) )

            elif numberType == ConfigManager.HEXADECIMAL_INT_NUMBER_TYPE:

                uio.info("%s is not a valid hexadecimal value." % (response) )

    @staticmethod
    def GetDecInt(uio, prompt, previousValue=UNSET_VALUE, minValue=UNSET_VALUE, maxValue=UNSET_VALUE):
      """@brief              Get a decimal integer number from the user.
         @param uio          A UIO (User Inpu Output) instance.
         @param prompt       The prompt presented to the user in order to enter
                             the float value.
         @param previousValue The previous number value.
         @param minValue     The minimum acceptable value.
         @param maxValue     The maximum acceptable value."""

      return ConfigManager._GetNumber(uio, prompt, previousValue=previousValue, minValue=minValue, maxValue=maxValue, numberType=ConfigManager.DECIMAL_INT_NUMBER_TYPE)

    @staticmethod
    def GetHexInt(uio, prompt, previousValue=UNSET_VALUE, minValue=UNSET_VALUE, maxValue=UNSET_VALUE):
      """@brief              Get a decimal integer number from the user.
         @param uio          A UIO (User Inpu Output) instance.
         @param prompt       The prompt presented to the user in order to enter
                             the float value.
         @param previousValue The previous number value.
         @param minValue     The minimum acceptable value.
         @param maxValue     The maximum acceptable value."""

      return ConfigManager._GetNumber(uio, prompt, previousValue=previousValue, minValue=minValue, maxValue=maxValue, numberType=ConfigManager.HEXADECIMAL_INT_NUMBER_TYPE)

    @staticmethod
    def GetFloat(uio, prompt, previousValue=UNSET_VALUE, minValue=UNSET_VALUE, maxValue=UNSET_VALUE):
      """@brief              Get a float number from the user.
         @param uio          A UIO (User Inpu Output) instance.
         @param prompt       The prompt presented to the user in order to enter
                             the float value.
         @param previousValue The previous number value.
         @param minValue     The minimum acceptable value.
         @param maxValue     The maximum acceptable value."""

      return ConfigManager._GetNumber(uio, prompt, previousValue, minValue=minValue, maxValue=maxValue, numberType=ConfigManager.FLOAT_NUMBER_TYPE)

    @staticmethod
    def GetBool(uio, prompt, previousValue=True):
        """@brief Input a boolean value.
           @param uio          A UIO (User Input Output) instance.
           @param prompt       The prompt presented to the user in order to enter
                                the float value.
           @param previousValue The previous True or False value."""
        _prompt = "%s y/n" % (prompt)

        if previousValue:
            prevValue='y'
        else:
            prevValue='n'

        while True:
            value = ConfigManager.GetString(uio, _prompt, prevValue)
            value=value.lower()
            if value == 'n':
                return False
            elif value == 'y':
                return True

    @staticmethod
    def GetPrivateKeyFile():
        """@brief Get the private key file."""
        homePath = getHomePath()
        folder = os.path.join(homePath, ConfigManager.SSH_FOLDER)
        priKeyFile = os.path.join(folder, ConfigManager.PRIVATE_SSH_KEY_FILENAME)
        if not os.path.isfile(priKeyFile):
            raise Exception("%s file not found" % (priKeyFile) )
        return priKeyFile

    @staticmethod
    def GetPrivateSSHKeyFileContents():
        """@brief Get the private ssh key file.
           @return The key file contents"""
        privateRSAKeyFile = ConfigManager.GetPrivateKeyFile()
        fd = open(privateRSAKeyFile, 'r')
        fileContents = fd.read()
        fd.close()
        return fileContents

    @staticmethod
    def GetCrypter():
        """@brief Get the object responsible for encrypting and decrypting strings."""
        # Only import the cryptography module if it is used so as to avoid the
        # necessity of having the  cryptography module to use the pconfig module.
        from    cryptography.fernet import Fernet
        keyString = ConfigManager.GetPrivateSSHKeyFileContents()
        keyString = keyString[60:92]
        priKeyBytes = bytes(keyString, 'utf-8')
        priKeyBytesB64 = base64.b64encode(priKeyBytes)
        return Fernet(priKeyBytesB64)

    @staticmethod
    def Encrypt(inputString):
        """@brief Encrypt the string.
           @param inputString The string to encrypt.
           @return The encrypted string"""
        crypter = ConfigManager.GetCrypter()
        token = crypter.encrypt(bytes(inputString, 'utf-8'))
        return token.decode('utf-8')

    @staticmethod
    def Decrypt(inputString):
        """@brief Decrypt the string.
           @param inputString  The string to decrypt.
           return The decrypted string"""
        crypter = ConfigManager.GetCrypter()
        token = inputString.encode('utf-8')
        decryptedBytes = crypter.decrypt(token)
        return decryptedBytes.decode('utf-8')

    @staticmethod
    def GetConfigFile(cfgFilename, addDotToFilename=True, cfgPath=None):
        """@brief Get the config file."""

        if not cfgFilename:
            raise Exception("No config filename defined.")

        if addDotToFilename:
            if not cfgFilename.startswith("."):

                cfgFilename=".%s" % (cfgFilename)

        #The the config path has been set then use it
        if cfgPath:
            configPath = cfgPath

        else:
            # If the root user on a Linux system
            if platform.system() == 'Linux' and os.geteuid() == 0:
                # This should be the root users config folder.
                configPath="/root"

            else:
                configPath=""
                #If an absolute path is set for the config file then don't try to
                #put the file in the users home dir
                if not cfgFilename.startswith("/"):
                    configPath = expanduser("~")
                    configPath = configPath.strip()

        return join( configPath, cfgFilename )

    def __init__(self,
                 uio,
                 cfgFilename,
                 defaultConfig,
                 addDotToFilename=True,
                 encrypt=False,
                 cfgPath=None,
                 stripUnknownKeys=True,
                 addNewKeys=True):
        """@brief Constructor
           @param uio A UIO (User Input Output) instance. May be set to None if no user messages are required.
           @param cfgFilename   The name of the config file. If this is None then the default config filename is used.
           @param defaultConfig A default config instance containing all the default key-value pairs.
           @param addDotToFilename If True (default) then a . is added to the start of the filename. This hides the file in normal cases.
           @param encrypt If True then data will be encrypted in the saved files.
                          The encryption uses part of the the local SSH RSA private key.
                          This is not secure but assuming the private key has not been compromised it's
                          probably the best we can do. Therefore if encrypt is set True then the
                          an ssh key must be present in the ~/.ssh folder named id_rsa.
           @param cfgPath The config path when the config file will be stored. By default this is unset and the
                          current users home folder is the location of the config file.
           @param stripUnknownKeys If True then keys in the dict but not in the default config dict are stripped from the config.
           @param addNewKeys If keys are found in the default config that are not in the config dict, add them."""
        self._uio               = uio
        self._cfgFilename       = cfgFilename
        self._defaultConfig     = defaultConfig
        self._addDotToFilename  = addDotToFilename
        self._encrypt           = encrypt
        self._cfgPath           = cfgPath
        self._stripUnknownKeys  = stripUnknownKeys
        self._addNewKeys        = addNewKeys
        self._configDict        = {}

        # If the user passed None in as the cfg filename then generate the default config file.
        if self._cfgFilename is None:
            self._cfgFilename =  ConfigManager.GetDefaultConfigFilename()

        self._cfgFile = self._getConfigFile()
        self._modifiedTime = self._getModifiedTime()

    def _info(self, msg):
        """@brief Display an info message if we have a UIO instance.
           @param msg The message to be displayed."""
        if self._uio:
            self._uio.info(msg)

    def _debug(self, msg):
        """@brief Display a debug message if we have a UIO instance.
           @param msg The message to be displayed."""
        if self._uio:
            self._uio.debug(msg)

    def _getConfigFile(self):
        """@brief Get the config file."""
        return ConfigManager.GetConfigFile(self._cfgFilename, addDotToFilename=self._addDotToFilename, cfgPath=self._cfgPath)

    def addAttr(self, key, value):
        """@brief Add an attribute value to the config.
           @param key The key to store the value against.
           @param value The value to be stored."""
        self._configDict[key]=value

    def getAttrList(self):
        """@return A list of attribute names that are stored."""
        return self._configDict.keys()

    def getAttr(self, key, allowModify=True):
        """@brief Get an attribute value.
           @param key The key for the value we're after.
           @param allowModify If True and the configuration has been modified
                  since the last read by the caller then the config will be reloaded."""

        #If the config file has been modified then read the config to get the updated state.
        if allowModify and self.isModified():
            self.load(showLoadedMsg=False)
            self.updateModifiedTime()

        return self._configDict[key]

    def _saveDict(self, dictToSave):
      """@brief Save dict to a file.
         @param dictToSave The dictionary to save."""

      try:

          if self._encrypt:
              stringToSave = json.dumps(dictToSave, sort_keys=True)
              stringToSave = ConfigManager.Encrypt(stringToSave)
              fd = open(self._cfgFile, "w")
              fd.write(stringToSave)
              fd.close()
          else:
              json.dump(dictToSave, open(self._cfgFile, "w"), sort_keys=True)

          self._info("Saved config to %s" % (self._cfgFile) )

      except IOError as i:
        raise IOError(i.errno, 'Failed to write file \'%s\': %s'
            % (self._cfgFile, i.strerror), i.filename).with_traceback(i)

    def store(self, copyToRoot=False):
        """@brief Store the config to the config file.
           @param copyToRoot If True copy the config to the root user (Linux only)
                             if not running with root user config path. If True
                             on non Linux system config will only be saved in
                             the users home path. Default = False."""
        self._saveDict(self._configDict)

        self.updateModifiedTime()

        if copyToRoot and not self._cfgFile.startswith("/root/") and isdir("/root"):
            fileN = basename(self._cfgFile)
            rootCfgFile = join("/root", fileN)
            copyfile(self._cfgFile, rootCfgFile)
            self._info("Also updated service list in %s" % (rootCfgFile))

    def _getDict(self):
      """@brief Load dict from file
         @return Return the dict loaded from the file."""
      dictLoaded = {}

      if self._encrypt:
          fd = open(self._cfgFile, "r")
          encryptedData = fd.read()
          fd.close()
          decryptedString = ConfigManager.Decrypt(encryptedData)
          dictLoaded = json.loads(decryptedString)
      else:

          fp = open(self._cfgFile, 'r')
          dictLoaded = json.load(fp)
          fp.close()

      return dictLoaded

    def load(self, showLoadedMsg=True):
        """@brief Load the config.
           @param showLoadedMsg If True load messages are displayed."""

        if not isfile(self._cfgFile):

            self._configDict = self._defaultConfig
            self.store()

        else:
            #Get the config from the stored config file.
            loadedConfig = self._getDict()
            #Get list of all the keys from the config file loaded.
            loadedConfigKeys = list(loadedConfig.keys())

            #Get the default config
            defaultConfig = copy.deepcopy( self._defaultConfig )
            defaultConfigKeys = list(defaultConfig.keys())

            # Config parameters may be added or dropped over time. We use the default config to
            # check for parameters that should be added/removed.

            if self._addNewKeys:
                # Add any missing keys to the loaded config from the default config.
                for defaultKey in defaultConfigKeys:
                    if defaultKey not in loadedConfigKeys:
                        loadedConfig[defaultKey] = self._defaultConfig[defaultKey]
                        self._debug("----------> DEFAULT VALUE ADDED: {} = {}".format(defaultKey, loadedConfig[defaultKey]))

            if self._stripUnknownKeys:
                # If some keys have been dropped from the config, remove them.
                for loadedConfigKey in loadedConfigKeys:
                    if loadedConfigKey not in defaultConfigKeys:
                        self._debug("----------> DROPPED FROM CONFIG: {} = {}".format(loadedConfigKey, loadedConfig[loadedConfigKey]))
                        loadedConfig.pop(loadedConfigKey, None)

            self._configDict = loadedConfig
        self._info("Loaded config from %s" % (self._cfgFile) )

    def inputFloat(self, key, prompt, minValue=UNSET_VALUE, maxValue=UNSET_VALUE):
        """@brief Input a float value into the config.
           @key The key to store this value in the config.
           @param prompt       The prompt presented to the user in order to enter
                             the float value.
           @param minValue     The minimum acceptable value.
           @param maxValue     The maximum acceptable value."""
        value = ConfigManager.GetFloat(self._uio, prompt, previousValue=self._getValue(key), minValue=minValue, maxValue=maxValue)
        self.addAttr(key, value)

    def inputDecInt(self, key, prompt, minValue=UNSET_VALUE, maxValue=UNSET_VALUE):
        """@brief Input a decimal integer value into the config.
           @key The key to store this value in the config.
           @param prompt       The prompt presented to the user in order to enter
                             the float value.
           @param minValue     The minimum acceptable value.
           @param maxValue     The maximum acceptable value."""
        value = ConfigManager.GetDecInt(self._uio, prompt, previousValue=self._getValue(key), minValue=minValue, maxValue=maxValue)
        self.addAttr(key, value)

    def inputHexInt(self, key, prompt, minValue=UNSET_VALUE, maxValue=UNSET_VALUE):
        """@brief Input a hexadecimal integer value into the config.
           @key The key to store this value in the config.
           @param prompt       The prompt presented to the user in order to enter
                             the float value.
           @param minValue     The minimum acceptable value.
           @param maxValue     The maximum acceptable value."""
        value = ConfigManager.GetHexInt(self._uio, prompt, previousValue=self._getValue(key), minValue=minValue, maxValue=maxValue)
        self.addAttr(key, value)

    def _getValue(self, key):
        """@brief Get the current value of the key.
           @param key The key of the value we're after.
           @return The value of the key or and empty string if key not found."""
        value=""

        if key in self._configDict:
            value = self.getAttr(key)

        return value

    def inputStr(self, key, prompt, allowEmpty):
        """@brief Input a string value into the config.
           @param key The key to store this value in the config.
           @param prompt The prompt presented to the user in order to enter
                         the float value.
           @param allowEmpty   If True then allow the string to be empty."""
        value = ConfigManager.GetString(self._uio, prompt, previousValue=self._getValue(key), allowEmpty=allowEmpty )
        self.addAttr(key, value)

    def inputDate(self, key, prompt, allowEmpty):
        """@brief Input a date into the config.
           @param key The key to store this value in the config.
           @param prompt The prompt presented to the user in order to enter
                         the float value.
           @param allowEmpty   If True then allow the string to be empty."""
        value = ConfigManager.GetDate(self._uio, prompt, previousValue=self._getValue(key), allowEmpty=allowEmpty )
        self.addAttr(key, value)

    def inputTime(self, key, prompt, allowEmpty):
        """@brief Input a date into the config.
           @param key The key to store this value in the config.
           @param prompt The prompt presented to the user in order to enter
                         the float value.
           @param allowEmpty   If True then allow the string to be empty."""
        value = ConfigManager.GetTime(self._uio, prompt, previousValue=self._getValue(key), allowEmpty=allowEmpty )
        self.addAttr(key, value)

    def inputBool(self, key, prompt):
        """@brief Input a boolean value.
           @param key The key to store this value in the config.
           @param prompt The prompt presented to the user in order to enter
                         the boolean (Yes/No) value."""
        previousValue=self._getValue(key)
        yes = self.getYesNo(prompt, previousValue=previousValue)
        if yes:
            value=True
        else:
            value=False
        self.addAttr(key, value)

    def getYesNo(self, prompt, previousValue=0):
        """@brief Input yes no response.
           @param prompt The prompt presented to the user in order to enter
                         the float value.
           @param allowEmpty   If True then allow the string to be empty.
           @return True if Yes, False if No."""

        _prompt = "%s y/n" % (prompt)

        if previousValue:
            prevValue='y'
        else:
            prevValue='n'

        while True:
            value = ConfigManager.GetString(self._uio, _prompt, prevValue)
            value=value.lower()
            if value == 'n':
                return False
            elif value == 'y':
                return True

    def _getModifiedTime(self):
        """@brief Get the modified time of the config file."""
        mtime = 0
        try:

            if isfile(self._cfgFile):
                mtime = getmtime(self._cfgFile)

        except OSError:
            pass

        return mtime

    def updateModifiedTime(self):
        """@brief Update the modified time held as an attr in this nistance with the current modified time of the file."""
        self._modifiedTime = self._getModifiedTime()

    def isModified(self):
        """@Return True if the config file has been updated."""
        mTime = self._getModifiedTime()
        if mTime != self._modifiedTime:
            return True
        return False

    def _getConfigAttDetails(self, key, configAttrDetailsDict):
        """@brief Get the configAttrDetails details instance from the dict.
           @param key The in to the value in the configAttrDetailsDict
           @param configAttrDetailsDict The dict containing attr meta data."""
        if key in configAttrDetailsDict:
            return configAttrDetailsDict[key]
        raise Exception("getConfigAttDetails(): The %s dict has no key=%s" % ( str(configAttrDetailsDict), key) )

    def edit(self, configAttrDetailsDict):
        """@brief A high level method to allow user to edit all config attributes.
           @param configAttrDetailsDict A dict that holds configAttrDetails
                  instances, each of which provide data required for the
                  user to enter the configuration parameter."""

        if len(self._configDict.keys()) == 0:
            self.load(showLoadedMsg=True)

        keyList = list(self._configDict.keys())
        keyList.sort()
        index = 0
        while index < len(keyList):

            try:

                key = keyList[index]

                configAttrDetails = self._getConfigAttDetails(key, configAttrDetailsDict)

                if key.endswith("_FLOAT"):

                    self.inputFloat(key, configAttrDetails.prompt, minValue=configAttrDetails.minValue, maxValue=configAttrDetails.maxValue)

                elif key.endswith("_INT"):

                    self.inputDecInt(key, configAttrDetails.prompt, minValue=configAttrDetails.minValue, maxValue=configAttrDetails.maxValue)

                elif key.endswith("_HEXINT"):

                    self.inputHexInt(key, configAttrDetails.prompt, minValue=configAttrDetails.minValue, maxValue=configAttrDetails.maxValue)

                elif key.endswith("_STR"):

                    self.inputStr(key, configAttrDetails.prompt, configAttrDetails.allowEmpty)

                index = index + 1

            except KeyboardInterrupt:

                if index > 0:
                    index=index-1
                    print('\n')

                else:
                    while True:
                        try:
                            print('\n')
                            if self.getYesNo("Quit ?"):
                                sys.exit(0)
                            break
                        except KeyboardInterrupt:
                            pass

        self.store()

    def getConfigDict(self):
        """@return the dict holding the configuration."""
        return self._configDict

    def setDefaultConfig(self):
        """@brief Set the default configuration by removing the existing configuration file and re loading."""
        configFile = self._getConfigFile()
        if isfile(configFile):
            self._info(configFile)
            deleteFile = self._uio.getBoolInput("Are you sure you wish to delete the above file [y]/[n]")
            if deleteFile:
                os.remove(configFile)
                self._info("{} has been removed.".format(configFile))
                self._info("The default configuration will be loaded next time..")

    def configure(self, editConfigMethod, prompt="Enter 'E' to edit a parameter, or 'Q' to quit", editCharacters = 'E', quitCharacters= 'Q'):
        """@brief A helper method to edit the dictionary config.
           @param editConfigMethod The method to call to edit configuration.
           @return None"""
        running=True
        while running:
            idKeyDict=self.show()
            response = self._uio.getInput(prompt)
            response=response.upper()
            if response in editCharacters:
                id = self._uio.getIntInput("Enter the ID of the parameter to change")
                if id not in idKeyDict:
                    self._uio.error("Configuration ID {} is invalid.".format(id))
                else:
                    key=idKeyDict[id]
                    editConfigMethod(key)
                    self.store()

            elif response in quitCharacters:
                running = False

    def show(self):
        """@brief A helper method to show the dictionary config to the user.
           @return A dictionary mapping the attribute ID's (keys) to dictionary keys (values)."""
        maxKeyLen=10
        for key in self._configDict:
            if len(key) > maxKeyLen:
                maxKeyLen = len(key)
        self._info("ID  PARAMETER"+" "*(maxKeyLen-8)+" VALUE")
        id=1
        idKeyDict = {}
        for key in self._configDict:
            idKeyDict[id]=key
            self._info("{:<3d} {:<{}} {}".format(id, key, maxKeyLen+1, self._configDict[key]))
            id=id+1
        return idKeyDict

class ConfigAttrDetails(object):
    """@brief Responsible for holding config attribute meta data."""

    def __init__(self, prompt, minValue=ConfigManager.UNSET_VALUE, maxValue=ConfigManager.UNSET_VALUE, allowEmpty=True):
        self.prompt         =   prompt      #Always used to as k user to enter attribute value.
        self.minValue       =   minValue    #Only used for numbers
        self.maxValue       =   maxValue    #Only used for numbers
        self.allowEmpty     =   allowEmpty  #Only used for strings

class DotConfigManager(ConfigManager):
    """@brief This extends the previous ConfigManager and stores config under the ~/.config folder
              rather than in the home folder (~) using a filename prefixed with the . character.
              The ~/.config folder holds either a single config file of the startup python filename.
              The ./config folder can contain another python module folder which contains the config
              file. E.G for this example app the ~/.config/examples/pconfig_example.cfg folder is used."""
    DEFAULT_CONFIG = None       # This must be overridden in a subclass to define the configuration parameters and values.
    KEY_EDIT_ORDER_LIST = None

    @staticmethod
    def GetDefaultConfigFolder():
        """@brief Get the default config folder.."""
        dotConfigFolder = '.config'
        if platform.system() == 'Linux' and os.geteuid() == 0:
            homePath = "/root"
        else:
            homePath = os.path.expanduser("~")
        configFolder = os.path.join(homePath, dotConfigFolder)

        if not os.path.isdir(homePath):
            raise Exception(f"{homePath} HOME path does not exist.")

        # Create the ~/.config folder if it does not exist
        if not os.path.isdir(configFolder):
            # Create the ~/.config folder
            os.makedirs(configFolder)

        return configFolder

    @staticmethod
    def GetDefaultConfigFilename(filenameOverride=None):
        """@brief Get the default name of the config file for this app. This will be the program name
                  (file that started up initially) without the .py extension. A .cfg extension is added
                  and it will be found in the ~/.config folder.

                  This will not work if no python file was started

                  E.G
                  A command line as shown below

                  python -m poetry run python -c "import python_module.python_file; python_module.python_file.main()

           @param filenameOverride The name for the config file in the .config folder. If left as None then the program name ise used
                                   as the config filename."""
        configFolder = DotConfigManager.GetDefaultConfigFolder()

        if filenameOverride:
            progName = filenameOverride
        else:
            progName = sys.argv[0]
            if progName.endswith('.py'):
                progName = progName[0:-3]
            progName = os.path.basename(progName).strip()

        # Note that we assume that addDotToFilename in the ConfigManager constructor is set True
        # as this will prefix the filename with the . character.
        if os.path.isdir(configFolder):
            configFilename = os.path.join(".config", progName + ".cfg")

        else:
            raise Exception(f"Failed to create the {configFolder} folder.")

        return configFilename

    def __init__(self,
                 defaultConfig,
                 keyEditOrderList=None,
                 uio=None,
                 encrypt=False,
                 stripUnknownKeys=True,
                 addNewKeys=True,
                 filenameOverride=None):
        """@brief Constructor
           @param defaultConfig A default config instance containing all the default key-value pairs.
           @param keyEditOrderList A list of all the dict keys in the order that the caller wishes them to be displayed top the user.
           @param uio A UIO (User Input Output) instance. May be set to None if no user messages are required.
           @param encrypt If True then data will be encrypted in the saved files.
                          The encryption uses part of the the local SSH RSA private key.
                          This is not secure but assuming the private key has not been compromised it's
                          probably the best we can do.
                          !!! Therefore if encrypt is set True then the an ssh key must be present !!!
                          ||| in the ~/.ssh folder named id_rsa.                                   !!!
           @param stripUnknownKeys If True then keys in the dict but not in the default config dict are stripped from the config.
           @param addNewKeys If keys are found in the default config that are not in the config dict, add them.
           @param filenameOverride The name for the config file in the .config folder. If left as None then the program name ise used
                                   as the config filename."""
        super().__init__(uio,
                         DotConfigManager.GetDefaultConfigFilename(filenameOverride),
                         defaultConfig,
                         encrypt=encrypt,
                         stripUnknownKeys=stripUnknownKeys,
                         addNewKeys=addNewKeys)
        self._keyEditOrderList = keyEditOrderList
        # Ensure the config file is present and loaded into the internal dict.
        self.load()

    def show(self):
        """@brief A helper method to show the dictionary config to the user.
           @return A dictionary mapping the attribute ID's (keys) to dictionary keys (values)."""
        maxKeyLen=10
        # If the caller wants to present the parameters to the user in a partiular order
        if self._keyEditOrderList:
            keys = self._keyEditOrderList
            defaultKeys = list(self._configDict.keys())
            for defaultKey in defaultKeys:
                if defaultKey not in keys:
                    raise Exception(f"BUG: DotConfigManager: {defaultKey} key is missing from the keyEditOrderList.")
        # Present the parameters to the user in any order.
        else:
            keys = list(self._configDict.keys())

        for key in keys:
            if len(key) > maxKeyLen:
                maxKeyLen = len(key)
        self._info("ID  PARAMETER"+" "*(maxKeyLen-8)+" VALUE")
        id=1
        idKeyDict = {}
        for key in keys:
            idKeyDict[id]=key
            self._info("{:<3d} {:<{}} {}".format(id, key, maxKeyLen+1, self._configDict[key]))
            id=id+1
        return idKeyDict
