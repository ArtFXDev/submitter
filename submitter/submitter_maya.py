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
            cmds.setAttr("defaultRenderGlobals.imageFilePrefix", os.path.basename(path).split(".")[0])
        if self.renderer in ["redshift", "arnold", "vray"]:
            print("use {} renderer".format(self.renderer))
            self.submit(path, "maya", [self.renderer])
        else:
            self.submit(path, "maya")

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace=""):
        # project = self.get_project()
        # dirmap_server = "//" + project["server"] if is_linux else "//" + project["server"] + "/PFE_RN_2020/"
        command = [
            config.batcher["maya"]["render"]["linux" if is_linux else "win"],
            "-r", "redshift" if self.renderer == "redshift" else "file",
            "-s", str(frame_start),
            "-e", str(frame_end),
            "-b", str(step),
            # "-preRender", 'dirmap -en true; dirmap -m "D:/SynologyDrive/" "' + dirmap_server + '";',
            "-proj", "%D({proj})".format(proj=workspace),
            "%D({file_path})".format(file_path=file_path)
        ]
        return command

    def set_dirmap(self, local_project, server_project, new_name_path, path):
        cmds.file(save=True)
        # # # # DIRNAME # # # #
        # Edit file in text mode is .ma else do modification and reopen the scene
        if path.split(".") == "ma":
            copyfile(path, new_name_path)
            file_data = ""
            with open(new_name_path, "rt") as file:
                file_data = file.read()
            file_data = file_data.replace(local_project, server_project)
            file_data = file_data.replace("%ROOT_PIPE%", server_project)
            with open(new_name_path, "wt") as file:
                file.write(file_data)
        else:
            for type in cmds.filePathEditor(query=True, listRegisteredTypes=True):
                for node in cmds.ls(type=type):
                    cmds.filePathEditor(node, replaceString=(local_project, server_project), replaceField="pathOnly", replaceAll=True)
                    cmds.filePathEditor(node, replaceString=("%ROOT_PIPE%", server_project), replaceField="pathOnly", replaceAll=True)
            cmds.file(rename=new_name_path)
            cmds.file(save=True)
            print("Save file : " + str(new_name_path))
            cmds.file(path, open=True, force=True)


def run():
    for x in get_maya_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterMaya()
    win.show()


if __name__ == '__main__':

    sub = SubmitterMaya()
    sub.show()
