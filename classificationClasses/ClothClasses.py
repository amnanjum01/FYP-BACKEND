from .ModelClasses import ModelClasses

class ClothClasses(ModelClasses):
    #class variables
    classLabelsDict = {
        0: "m-button-down",
        1: "m-formal-trousers",
        2: "m-informal-pants",
        3: "m-kurta",
        4: "m-shalwar",
        5: "m-shirts",
        6: "outerwear",
        7: "w-dress",
        8: "w-dupatta",
        9: "w-eastern-trouser",
        10: "w-kameez",
        11: "w-shalwar",
        12: "w-western-shirt",
        13: "w-western-trouser"
    }
    
    #class method to obtain the required data
    @classmethod
    def getClassLabels(cls, classCodes):
        classNames = []
        for classCode in classCodes:
            classNames.append(cls.classLabelsDict[classCode])
        return classNames