import os
import maya.OpenMayaUI as mui
import maya.cmds as cmds
from shiboken2 import wrapInstance
from Qt import QtCore
from Qt.QtWidgets import QMainWindow
from Qt.QtWidgets import QRadioButton
from shutil import copyfile

import config
from .submitter_base import Submitter


def get_maya_window():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QMainWindow)


class SubmitterMaya(Submitter):

    def __init__(self, parent=get_maya_window(), sid=None):
        super(SubmitterMaya, self).__init__(parent, sid)
        self._rb_render_default = QRadioButton("Default")
        self._rb_render_redshift = QRadioButton("Redshift")
        self._rb_render_default.setChecked(True)
        self.renderer = "maya"

    def get_path(self):
        return cmds.file(q=True, sceneName=True)

    def default_frame_range(self):
        start = int(cmds.getAttr("defaultRenderGlobals.startFrame"))
        end = int(cmds.getAttr("defaultRenderGlobals.endFrame"))
        step = int(cmds.getAttr("defaultRenderGlobals.byFrame"))
        return (start, end, step)

    def pre_submit(self):
        path = cmds.file(q=True, sceneName=True)
        cmds.file(save=True)
        self.renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")
        if not cmds.getAttr("defaultRenderGlobals.imageFilePrefix"):
            cmds.setAttr("defaultRenderGlobals.imageFilePrefix", os.path.basename(path).split(".")[0], type="string")
        if self.renderer in ["redshift", "arnold", "vray"]:
            print("use {} renderer".format(self.renderer))
            self.submit(path, "maya", [self.renderer])
        else:
            self.submit(path, "maya")

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace=""):
        command = [
            config.batcher["maya"]["render"]["linux" if is_linux else "win"],
            "-r", "file",
            "-s", str(frame_start),
            "-e", str(frame_end),
            "-b", str(step),
            "-proj", "%D({proj})".format(proj=workspace),
            "%D({file_path})".format(file_path=file_path)
        ]
        return command


def run(sid=None):
    for x in get_maya_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterMaya(sid=sid)
    win.show()


if __name__ == '__main__':

    sub = SubmitterMaya()
    sub.show()
