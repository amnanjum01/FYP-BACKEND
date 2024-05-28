from .ModelClasses import ModelClasses

class ClothClasses(ModelClasses):
    #class variables
    classLabelsDict = {
        0: "m-button-down", #done
        1: "m-formal-trousers", #done
        2: "m-informal-pants", #done
        3: "m-kurta", #done 
        4: "m-shalwar", #done
        5: "m-shirts",
        6: "outerwear", #done
        7: "w-dress", #done
        8: "w-dupatta", #done
        9: "w-eastern-trouser", #done
        10: "w-kameez", #done
        11: "w-shalwar", #done
        12: "w-western-shirt", #done
        13: "w-western-trouser" #done
    }
    
    #class method to obtain the required data
    @classmethod
    def getClassLabels(cls, classCodes):
        classNames = []
        for classCode in classCodes:
            classNames.append(cls.classLabelsDict[classCode])
        return classNames