import shutil, os, datetime, sys
from stardewLibs import HelperLibraries, StardewSaveError
from types import NoneType
from csRandom import Random
import xml.etree.ElementTree as ET

SPRING = 0
SUMMER = 28
FALL = 56
WINTER = 84
SEASON = 28
YEAR = SEASON*4
BACKUP = True
CHANGE_OPTIONS = {'name':1,
                'invObj':2,
                'questView':0,
                'itemView':0,
                'buildingView':0,
                'monstersSlayed':0,
                'nextTrain':2,
                'changeSave':0,}

if len(sys.argv) > 1:
    savePath = sys.argv[1]
else:
    savePath = input('Please drag save folder here: ')

def initialize(savePath):
    '''
    Initialize the XML trees and set global variables
    '''
    global dirName, root, split, parsedXml, parsedSaveGameInfo, sGIRoot, root, gameID
    if not os.path.isdir(savePath):
        raise StardewSaveError('Isn\'t a directory.')
    
    dirName = os.path.basename(os.path.normpath(savePath))

    split = dirName.split('_')

    if not os.path.exists(os.path.join(savePath, dirName)):
        raise StardewSaveError(f'Missing save file {dirName}.')

    if not os.path.exists(os.path.join(savePath, f'{dirName}_old')):
        raise StardewSaveError(f'Missing save file {dirName}_old.')

    if not os.path.exists(os.path.join(savePath, 'SaveGameInfo')):
        raise StardewSaveError('Missing save file SaveGameInfo.')

    if not os.path.exists(os.path.join(savePath, 'SaveGameInfo_old')):
        raise StardewSaveError('Missing save file SaveGameInfo_old.')

    parsedXml = ET.parse(os.path.join(savePath, dirName))
    parsedSaveGameInfo = ET.parse(os.path.join(savePath, 'SaveGameInfo'))
    sGIRoot = parsedSaveGameInfo.getroot()
    root = parsedXml.getroot()

    gameID = int(root.find('uniqueIDForThisGame').text)
    print(gameID)

    #print(root.find('player').find('uniqueIDForThisGame').text)
    if split[1] != str(gameID):
        raise StardewSaveError('Game IDs do not match.')
    
    print(f'Season: {root.find("currentSeason").text.capitalize()}  Day: {root.find("dayOfMonth").text}')

def nameCmd(name:list):
    global savePath, BACKUP
    '''
    Change the name of the player.
    '''
    if BACKUP:
        backupPath =  os.path.abspath(os.path.join(savePath, os.pardir, f'{dirName}_BACKUP'))
        shutil.copytree(savePath, backupPath)
    playerId = dirName.split('_')[1]
    sGIRoot.find('name').text = name
    root.find('player').find('name').text = name
    HelperLibraries.saveXml(parsedXml, os.path.join(savePath, dirName))
    HelperLibraries.saveXml(parsedSaveGameInfo, os.path.join(savePath, 'SaveGameInfo'))
    os.rename(os.path.join(savePath, dirName), os.path.join(savePath, f'{name}_{playerId}'))
    os.rename(os.path.join(savePath, f'{dirName}_old'), os.path.join(savePath, f'{name}_{playerId}_old'))
    os.rename(savePath, os.path.abspath(os.path.join(savePath, os.pardir, f'{name}_{playerId}')))
    savePath = os.path.abspath(os.path.join(savePath, os.pardir, f'{name}_{playerId}'))
    initialize(savePath)
    print(f'Name changed to {name}.', end="")
    if BACKUP:
        print(f' Backup saved to {backupPath}')
    else:
        print('')

def questViewCmd():
    '''
    Lists all your current active quests.
    '''
    questTypeList = []

    for element in root.find('player').find('questLog'):
        questTitle = element.find('questTitle')
        if questTitle == NoneType:
            questTitle = element.find('_questTitle')
        try:
            questType = element.attrib['{http://www.w3.org/2001/XMLSchema-instance}type']
        except Exception:
            questType = 'OtherQuest'
        questType = questType.replace('Quest', '')

        questTypeNew = ''

        for letter in questType:
            if letter.isupper():
                questTypeNew += f' {letter}'
            else:
                questTypeNew += letter
        
        if questTypeNew[0] == ' ':
            questTypeNew = questTypeNew[1:]
        questTypeList.append(f'{questTypeNew}: {questTitle.text}')

    print('Your Quests are:')
    for quest in questTypeList:
        print(f'      {quest}')

def itemViewCmd():
    '''
    Lists all your current items.
    '''
    global root
    for item in root.find('player').find('items').findall('Item'):
        if '{http://www.w3.org/2001/XMLSchema-instance}type' in item.attrib:
            itemName = item.find('Name').text
            itemType = item.attrib['{http://www.w3.org/2001/XMLSchema-instance}type']
            itemTypeNew = ''
            for letter in itemType:
                if letter.isupper():
                    itemTypeNew += f' {letter}'
                else:
                    itemTypeNew += letter
            
            if itemTypeNew[0] == ' ':
                itemTypeNew = itemTypeNew[1:]
            print(f'{itemTypeNew}: {itemName}')
        else:
            print('Empty: None')

def monstersSlayedCmd():
    '''
    Lists the monsters you have slayed.
    '''
    for item in root.find("player").find("stats").find('specificMonstersKilled'):
        if item != NoneType:
            name = item.get('key').get('string').text
            amount = item.get('value').get('int').text
            print(f'{name}: {amount}')

def buildingViewCmd():
    '''
    Doesn't do anything yet.
    '''
    for item in root.find("player").find("stats").find('buildings').findall('Item'):
        if item != NoneType:
            name = item.find('Name').text
            amount = item.find('Amount').text
            print(f'{name}: {amount}')

def nextTrainCmd(gameSeed=None,ysd=None):
    #Thanks to MouseyPounds, https://github.com/MouseyPounds/stardew-predictor/blob/b32d9ad2e7de177c4b67136bbb88843e4258b11b/stardew-predictor.js#L4251
    '''
    Shows the next time a train will appear.
    '''
    global gameID, YEAR, SEASON
    if not gameSeed:
        gameSeed = gameID
    else:
        gameSeed = int(gameID)
    usingCustomPrediction = False
    dayOfMonth = None
    startDays = None
    if ysd:
        day, season, year = ysd.split('-')
        dayOfMonth = int(day)
        if dayOfMonth <= 0:
            raise StardewSaveError('Day must greater than zero.')
        if season.lower() == 'spring' or season.lower() == 'sp':
            season = SPRING
        elif season.lower() == 'summer' or season.lower() == 'su':
            season = SUMMER
        elif season.lower() == 'fall' or season.lower() == 'fa':
            season = FALL
        elif season.lower() == 'winter' or season.lower() == 'wi':
            season = WINTER
        else:
            raise StardewSaveError('Invalid season string.')
        if int(year) <= 0:
            raise StardewSaveError('Year must be greater than 0')
        year = int(year)*YEAR-YEAR
        startDays = dayOfMonth + season + year
    if type(gameSeed) == str:
        gameSeed = int(gameSeed)
    if not startDays:
        startDays = int(root.find('stats').find('daysPlayed').text)
    #daysPlayed = 29
    #dayOfMonth = 1
    if not dayOfMonth:
        dayOfMonth = int(root.find('dayOfMonth').text)
    foundTrain:bool = False
    offset = 0
    days = 0
    while not foundTrain and offset < 28-dayOfMonth:
        days = startDays + offset
        gen = Random(int(gameSeed/2+days))
        sample = gen.Sample()
        #print(sample)
        if sample < 0.2:
            trainTime = gen.Next(900,1800)
            trainTime -= trainTime % 10
            hour = round(trainTime/100)
            min = trainTime%100
            if min < 60:
                if hour > 12:
                    hour -= 12
                    ampm = 'PM'
                elif hour == 12:
                    ampm = 'PM'
                else:
                    ampm = 'AM'
                if min == 0:
                    min = '00'
                print(f'Next train on the {dayOfMonth+offset}th day at {hour}:{min} {ampm}.')
        offset += 1
    if not foundTrain:
        print('No more trains this season.')

def changeSaveCmd(savePathLocal:str=None):
    '''
    Change the active save.
    '''
    global savePath
    savePathLocal = input('Please drag save folder here: ')
    savePath = savePathLocal
    initialize(savePath)

initialize(savePath)

while True:
    try:
        whatToDo = input('Please provide an action: ')
        if whatToDo.lower().replace(' ','') == 'help':
            print('             === Help Menu ===')
            print('            help: Show this menu')
            for (command, params) in CHANGE_OPTIONS.items():
                print(f'            {command}    Parameters: {params}')
        elif whatToDo.lower().replace(' ','') == 'exit':
            exit()
        else:
            cmdParamsFound = True
            try:
                whatToDoNew, cmdParams = whatToDo.split(':')
                cmdParams = cmdParams.replace(' ','').split(',')
                whatToDoNew = whatToDoNew.lower()
            except Exception:
                cmdParamsFound = False
            cmdFound = False
            for (command, params) in CHANGE_OPTIONS.items():
                if params != 0 and cmdParamsFound:
                    if whatToDoNew.lower() == command.lower() and len(cmdParams) == params:
                        paramsExport = f'"{cmdParams[0]}"'
                        for param in cmdParams[1:]:
                            paramsExport += f',"{param}"'
                        exec(f'{command}Cmd({paramsExport})')
                        cmdFound = True
                else:
                    if whatToDo.lower() == command.lower():
                        exec(f'{command}Cmd()')
                        cmdFound = True
            if not cmdFound:
                print('Action not found.')
    except KeyboardInterrupt:
        print('Exiting...')
        exit()
