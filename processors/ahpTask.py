from qgis.core import (QgsTask, Qgis, QgsMessageLog)
from abc import abstractmethod
import traceback
import time

class AhpTask(QgsTask):
    def __init__(self, description, MESSAGE_CATEGORY):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.result = None
        self.MESSAGE_CATEGORY = MESSAGE_CATEGORY

    def run(self):
        QgsMessageLog.logMessage('---------------------------------------------------------------------', self.MESSAGE_CATEGORY, Qgis.Info)
        time.sleep(2) # wait for the dependencies to load
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), self.MESSAGE_CATEGORY, Qgis.Info)
        
        try:
            self.execute()
        
        except Exception as ex:
            traceback.print_exc()
            QgsMessageLog.logMessage('AhpTask failed (core). Exception: {}'.format(ex), self.MESSAGE_CATEGORY, Qgis.Critical)
            self.exception = ex
            return False
        
        QgsMessageLog.logMessage('Finished task "{}"'.format(self.description()), self.MESSAGE_CATEGORY, Qgis.Success)
        
        return True
    
    def finished(self, success):
        if success:
            QgsMessageLog.logMessage('"{}" successfully completed'.format(self.description()), self.MESSAGE_CATEGORY, Qgis.Success)
            
            try:
                self.succeeded()
            except Exception as ex:
                QgsMessageLog.logMessage('Exception occured while running suceeded for {}.'.format(self.description()), self.MESSAGE_CATEGORY, Qgis.Critical)
                traceback.print_exc()
        else:
            QgsMessageLog.logMessage('"{}" not successful'.format(self.description()), self.MESSAGE_CATEGORY, Qgis.Critical)

    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def succeeded(self):
        pass
    