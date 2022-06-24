class HelperLibraries:
    def getLocation(self, root, name):
        locations = root.find("locations").findall("GameLocation")
        farm_location = None
        for location in locations:
            if (
                location.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type")
                == name
            ):
                farm_location = location
                break
        if farm_location == None:
            raise AttributeError
        return farm_location
    
    def saveXml(xml, path):
        '''
        Save XML with 'UTF-8 with BOM' encoding.
        '''
        xml.write(path, encoding='utf-8-sig')
        with open(path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        content = content.replace("encoding='utf-8-sig'", "encoding='utf-8'").replace('\n', '')

        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(content)

class StardewSaveError(Exception):
    pass