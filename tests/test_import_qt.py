from tk_build import qt


def test_import_qt():

    if qt.is_pyside1_required():
        from PySide import QtGui, QtCore
        QApplication = QtGui.QApplication
        QDialog = QtGui.QDialog
    elif qt.is_pyside2_required():
        from PySide2 import QtWidgets, QtCore
        QApplication = QtWidgets.QApplication
        QDialog = QtWidgets.QDialog
    else:
        return

    QTimer = QtCore.QTimer

    app = QApplication([]) # noqa
    dlg = QDialog()
    dlg.show()
    QTimer.singleShot(1000, lambda: dlg.close())
    dlg.exec_()
