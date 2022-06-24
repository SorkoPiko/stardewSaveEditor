import shutil, os
from stardewLibs import HelperLibraries, StardewSaveError
from types import NoneType
import xml.etree.ElementTree as ET

backup = True
changeOptions = {'name':1,
                'invObj':2,
                'questView':0,
                'itemView':0,
                'buildingView':0,
                'monstersSlayed':0,
                'changeSave':0,}

savePath = input('Please drag save folder here: ')

def initialize(savePath):
    '''
    Initialize the XML trees and set global variables
    '''
    global dirName, root, split, parsedXml, parsedSaveGameInfo, sGIRoot, root
    if not os.path.isdir(savePath):
        raise StardewSaveError('Doesn\'t seem to be a Stardew Valley save, or the folder structure is invalid.')

    dirName = os.path.basename(os.path.normpath(savePath))

    split = dirName.split('_')

    if not os.path.exists(os.path.join(savePath, 'SaveGameInfo')) and not os.path.exists(os.path.join(savePath, dirName)):
        raise StardewSaveError('Doesn\'t seem to be a Stardew Valley save, or the folder structure is invalid.')

    parsedXml = ET.parse(os.path.join(savePath, dirName))
    parsedSaveGameInfo = ET.parse(os.path.join(savePath, 'SaveGameInfo'))
    sGIRoot = parsedSaveGameInfo.getroot()
    root = parsedXml.getroot()
    #postInit()

def postInit():
    global root, split
    '''
    Post-Initialization
    '''
    if root.find('player').find('name').text != split[0]:
        print(root.find('player').find('name').text)
        print('invalid xml file')
        exit()

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
    for item in root.find("player").find("stats").find('specificMonstersKilled'):
        name = item.get('key').get('string').text
        amount = item.get('value').get('int').text
        print(f'{name}: {amount}')

def buildingviewCmd():
    community_center = HelperLibraries.getLocation(root, "CommunityCenter")
    for element in community_center:
        print(element.text)
    areasComplete = community_center.find("areasComplete").findall("boolean")
    for area in areasComplete:
        print(area.text)

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