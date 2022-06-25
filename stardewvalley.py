import shutil, os, datetime
from stardewLibs import HelperLibraries, StardewSaveError
from types import NoneType
from csRandom import Random
import xml.etree.ElementTree as ET

backup = True
changeOptions = {'name':1,
                'invObj':2,
                'questView':0,
                'itemView':0,
                'buildingView':0,
                'monstersSlayed':0,
                'nextTrain':0,
                'changeSave':0,}

savePath = input('Please drag save folder here: ')

def initialize(savePath):
    '''
    Initialize the XML trees and set global variables
    '''
    global dirName, root, split, parsedXml, parsedSaveGameInfo, sGIRoot, root
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

    gameID = root.find('uniqueIDForThisGame').text

    #print(root.find('player').find('uniqueIDForThisGame').text)
    if split[1] != gameID:
        raise StardewSaveError('Game IDs do not match.')
    
    print(f'Season: {root.find("currentSeason").text}  Day: {root.find("dayOfMonth").text}')


def nameCmd(name:list):
    global savePath, backup
    '''
    Change the name of the player.
    '''
    if backup:
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
    if backup:
        print(f' Backup saved to {backupPath}')
    else:
        print('')

def questviewCmd():
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

def itemviewCmd():
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

def monstersslayedCmd():
    '''
    Lists the monsters you have slayed.
    '''
    for item in root.find("player").find("stats").find('specificMonstersKilled'):
        if item != NoneType:
            name = item.get('key').get('string').text
            amount = item.get('value').get('int').text
            print(f'{name}: {amount}')

def buildingviewCmd():
    '''
    Lists the '''
    for item in root.find("player").find("stats").find('buildings').findall('Item'):
        if item != NoneType:
            name = item.find('Name').text
            amount = item.find('Amount').text
            print(f'{name}: {amount}')

def nexttrainCmd():
    #Thanks to MouseyPounds, https://github.com/MouseyPounds/stardew-predictor/blob/b32d9ad2e7de177c4b67136bbb88843e4258b11b/stardew-predictor.js#L4251
    '''
    Shows the next time a train will appear.
    '''
    gameID = int(root.find('uniqueIDForThisGame').text)
    daysPlayed = int(root.find('player').find('stats').find('daysPlayed').text)
    dayOfMonth = int(root.find('dayOfMonth').text)
    foundTrain:bool = False
    offset = 0
    days = 0
    while not foundTrain and offset < 28-int(root.find('dayOfMonth').text):
        days = daysPlayed + offset
        gen = Random(int(gameID/2+days))
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



def changesaveCmd(savePathLocal:str=None):
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
            for (command, params) in changeOptions.items():
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
            for (command, params) in changeOptions.items():
                if params != 0 and cmdParamsFound:
                    if whatToDoNew.lower() == command.lower() and len(cmdParams) == params:
                        paramsExport = f'"{cmdParams[0]}"'
                        for param in cmdParams[1:]:
                            paramsExport += f',"{param}"'
                        exec(f'{whatToDoNew}Cmd({paramsExport})')
                        cmdFound = True
                else:
                    if whatToDo.lower() == command.lower():
                        exec(f'{whatToDo.lower()}Cmd()')
                        cmdFound = True
            if not cmdFound:
                print('Action not found.')
    except KeyboardInterrupt:
        print('Exiting...')
        exit()