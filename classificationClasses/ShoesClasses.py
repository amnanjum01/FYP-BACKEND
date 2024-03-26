from .ModelClasses import ModelClasses

class ShoesClasses(ModelClasses):
    classLabelsDict = {
        0: "boots",
        1: "heels",
        2:"loafers",
        3: "sandals",
        4: "slippers",
        5: "sneakers"
    }
    
    
    @classmethod
    def getClassLabels(cls, classCodes):
        classNames = []
        for classCode in classCodes:
            classNames.append(cls.classLabelsDict[classCode])
        return classNames