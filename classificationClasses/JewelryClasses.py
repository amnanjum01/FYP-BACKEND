from .ModelClasses import ModelClasses

class JewelryClasses(ModelClasses):
    classLabelsDict = {
        0: "bracelet",
        1: "earrings",
        2:"necklace",
        3: "rings",
    }
    
    
    @classmethod
    def getClassLabels(cls, classCodes):
        classNames = []
        for classCode in classCodes:
            classNames.append(cls.classLabelsDict[classCode])
        return classNames