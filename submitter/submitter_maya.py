import maya.OpenMayaUI as mui
import maya.cmds as cmds
from shiboken2 import wrapInstance
from Qt import QtCore
from Qt.QtWidgets import QMainWindow
from Qt.QtWidgets import QRadioButton

import config
from .submitter_base import Submitter


def get_maya_window():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QMainWindow)


class SubmitterMaya(Submitter):

    def __init__(self, parent=get_maya_window()):
        super(SubmitterMaya, self).__init__(parent)
        self._rb_render_default = QRadioButton("Default")
        self._rb_render_redshift = QRadioButton("Redshift")
        self.custom_layout.addWidget(self._rb_render_default)
        self.custom_layout.addWidget(self._rb_render_redshift)
        self._rb_render_default.setChecked(True)

    def get_path(self):
        return cmds.file(q=True, sceneName=True)

    def pre_submit(self):
        path = cmds.file(q=True, sceneName=True)
        start = int(cmds.currentTime(query=True))
        end = int(cmds.currentTime(query=True)) + 1
        cmds.file(save=True)
        self.submit(path, start, end, "maya")

    def task_command(self, is_linux, frame_start, frame_end, file_path, workspace=""):
        command = [
            config.batcher["maya"]["render"]["linux" if is_linux else "win"],
            "-r", "redshift" if self._rb_render_redshift.isChecked() else "file",
            "-s", "{start}".format(start=str(frame_start)),
            "-e", "{end}".format(end=str(frame_end)),
            "-proj", "%D({proj})".format(proj=workspace),
            "%D({file_path})".format(file_path=file_path)
        ]
        return command


def run():
    for x in get_maya_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterMaya()
    win.show()


if __name__ == '__main__':

    sub = SubmitterMaya()
    sub.show()
