from abc import ABC, abstractmethod

class ModelClasses(ABC):
    
    @classmethod
    @abstractmethod
    def getClassLabels(cls, classCodes):
        pass