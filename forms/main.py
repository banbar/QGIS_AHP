from .createOrOpenProjectDialog import CreateOrOpenProjectDialog
from PyQt5 import QtWidgets
from ..utilities.uihelpers import get_ui_class
from .projectSetupWidget import ProjectSetupWidget
from .criteriaDefinitionWidget import CriteriaDefinitionWidget
from .ahpParametersParentWidget import AhpParametersParentWidget
from .summaryWidget import SummaryWidget
from PyQt5.QtWidgets import QMessageBox

class Ui_mainWindow(QtWidgets.QDialog, get_ui_class('window.ui')):
    def __init__(self, parent=None):
        """Constructor."""
        super(Ui_mainWindow, self).__init__(parent)
        self.setupUi(self)
        self.createOrOpenProject()
        if self.terminate:
            return

        self.connectSignalsSlots()

        # prepare initial page
        self.currentPageIndex = 1        
        self.currentWidget = None
        self.setPage()

        self.start_btn.hide()
        self.project = None

    def connectSignalsSlots(self):
        self.nextPage_btn.clicked.connect(self.nextPage)
        self.prevPage_btn.clicked.connect(self.previousPage)
        self.start_btn.clicked.connect(self.analyse)

    def createOrOpenProject(self):
        """Opens a blocking dialog to select the project file, or create a new project"""
        dialog = CreateOrOpenProjectDialog()
        if dialog.exec():
            if(dialog.project is not None):
                self.project = dialog.project
                self.terminate = False
                return
            else:
                print("dialog returned null")
        else:
            print("dialog rejected")

        self.terminate = True
            
    def nextPage(self):
        """Increases the currentPageIndex and loads the page onto the container accordingly"""
        if self.currentPageIndex == 4:
            print("at end already")
            return
        self.currentPageIndex+=1
        return self.setPage()
    
    def previousPage(self):
        """Decreases the currentPageIndex and loads the page onto the container accordingly"""
        if self.currentPageIndex == 1:
            print("at start already")
            return
        self.currentPageIndex-=1
        return self.setPage()

    def setPage(self):
        """Removes the current page, creates the next page and loads it to the page. 
        Also handles the highlighting of the wizard step labels"""
        if self.project is not None:
            self.project.save_to_file()

        if self.currentWidget is not None:
            # remove highlighting of the current label
            self.currentWidget.relatedLabel.setStyleSheet('')
            # pull the project from widget # todo: isn't sending the ref possible?
            self.project = self.currentWidget.project
            # remove the page widget
            self.currentWidget.deleteLater()

        if self.currentPageIndex == 1:
            self.currentWidget = ProjectSetupWidget(self)
        elif self.currentPageIndex == 2:
            self.currentWidget = CriteriaDefinitionWidget(self)
        elif self.currentPageIndex == 3:
            self.currentWidget = AhpParametersParentWidget(self)
        elif self.currentPageIndex == 4:
            self.currentWidget = SummaryWidget(self)
        else:
            print("Invalid Page index")
            return
        
        self.pageContainer.addWidget(self.currentWidget)

        # highlight the current label
        self.currentWidget.relatedLabel.setStyleSheet("background-color: lightgreen")
        
        self.handleNavigationButtonsVisibility()

    def handleNavigationButtonsVisibility(self):
        """Hides back button on first page, next button on last page, and shows Start! button on last page"""
        if  self.currentPageIndex == 1:
            self.prevPage_btn.hide()
        elif self.currentPageIndex == 4:
            self.start_btn.show()
            self.nextPage_btn.hide()
        else:
            self.start_btn.hide()
            self.nextPage_btn.show()
            self.prevPage_btn.show()
 
    def analyse(self):
        """Starts calculations"""
        # todo: data validation
        # todo: are you sure dialog
        validation_message = self.project.is_valid()
        if validation_message == "":
            self.accept()
        else:            
            QMessageBox.warning(None, "Warning", validation_message)

    