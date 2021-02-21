import os
from datetime import datetime

import config
from .submitter_base import Submitter

import hou
from Qt.QtWidgets import QComboBox

from .frame_manager import frames_to_framerange

from shutil import copyfile

def get_houdini_window():
    return hou.qt.mainWindow()


class SubmitterHoudini(Submitter):

    def __init__(self, parent=get_houdini_window()):
        super(SubmitterHoudini, self).__init__(parent)
        self.output_node = QComboBox()
        self.output_node.setEditable(True)
        self.output_node.addItems(self.get_out_nodes())
        self.custom_layout.addWidget(self.output_node)
        self.rop_node = None
        self.list_rop = []

    def get_out_nodes(self):
        out_nodes = [out_node.path() for out_node in hou.node("out/").children()]
        return out_nodes

    def get_path(self):
        return hou.hipFile.path()

    def default_frame_range(self):
        start = int(hou.playbar.frameRange()[0])
        end = int(hou.playbar.frameRange()[1])
        step = 1
        return (start, end, step)

    def pre_submit(self):
        path = hou.hipFile.path()
        hou.hipFile.save(file_name=None)
        # Test output_node
        if not hou.node(str(self.output_node.text())):
            self.error("Output node error ! please verify the node path")
        else:
            # check node type
            # if merge:
            #    get number of connected node
            #    add it to an array
            # for i in array :
            #   submit
            self.rop_node = hou.node(self.output_node.text())
            if self.rop_node.type().name() == "merge":
                list_rop = self.rop_node.inputs()
                for rop in list_rop:
                    self.list_rop.append(rop.path())
                print("merge detected. Nodes = " + str(self.list_rop))
            else:
                self.list_rop = [self.rop_node.path()]
            for node in self.list_rop:
                print("start render for node " + node)
                self.rop_node = node
                hou.hipFile.save()
                _renderer = hou.node(self.rop_node).type().name().lower()
                use_renderer = False
                for renderer_loop in ["redshift", "arnold", "vray"]:
                    if _renderer.startswith(renderer_loop):
                        self.submit(path, "houdini", [renderer_loop])
                        use_renderer = True
                        break
                if not use_renderer:
                    self.submit(path, "houdini")

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace=""):
        command = [
            config.batcher["houdini"]["hython"]["linux" if is_linux else "win"],
            config.batcher["houdini"]["hrender"]["linux" if is_linux else "win"],
            "%D({file_path})".format(file_path=self.new_name),
            "-v",
            "-e",
            "-d", self.rop_node,
        ]
        if frame_start == frame_end:
            command.extend(["-F", str(frame_start)])
        else:
            command.extend(["-f", str(frame_start), str(frame_end)])
        if step != 1:
            command.extend(["-i", str(step)])
        return command

def run():
    for x in get_houdini_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterHoudini()
    win.show()


if __name__ == '__main__':

    sub = SubmitterHoudini()
    sub.show()
