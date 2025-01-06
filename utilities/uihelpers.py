import os

from qgis.PyQt import uic

def get_ui_class(uiFile):
    FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'forms', 'ui', uiFile))
    return FORM_CLASS

def print_widget_names(self, layout):
    for i in range(layout.count()):
        item = layout.itemAt(i).widget()  # Get the widget
        if item:
            print(item)  # Print the widget's name