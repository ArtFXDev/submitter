import os
from datetime import datetime

import config
from .submitter_base import Submitter

import hou
from Qt.QtWidgets import QLineEdit

from .frame_manager import frames_to_framerange

def get_houdini_window():
    return hou.qt.mainWindow()


class SubmitterHoudini(Submitter):

    def __init__(self, parent=get_houdini_window()):
        super(SubmitterHoudini, self).__init__(parent)
        self.output_node = QLineEdit()
        self.output_node.setPlaceholderText("Output Node : (ex: /out/mantra_ipr)")
        self.custom_layout.addWidget(self.output_node)

    def get_path(self):
        return hou.hipFile.path()

    def default_frame_range(self):
        start = int(hou.playbar.frameRange()[0])
        end = int(hou.playbar.frameRange()[1])
        step = 1
        return (start, end, step)

    def pre_submit(self):
        path = hou.hipFile.path()
        # Test output_node
        if not hou.node(str(self.output_node.text())):
            self.error("Output node error ! please verify the node path")
        else:
            #check node type
            #if merge:
            #   get number of connected node
            #   add it to an array
            #for i in array :
            #   submit
            list_rop = []
            if(self.output_node.type().name() == "merge"):
                list_rop = self.output_node.inputs()
                print("merge detected. Nodes = "+str(list_rop))
            else :
                list_rop = [self.output_node]

            for node in list_rop:
                self.output_node = node
                hou.hipFile.save()
                _renderer = hou.nodeType(str(self.output_node.text())).name().lower()
                # new_path = self.set_env_dirmap(path)
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
            "%D({file_path})".format(file_path=file_path),
            "-v",
            "-e",
            "-d", str(self.output_node.text()),
        ]
        if frame_start == frame_end:
            command.extend(["-F", str(frame_start)])
        else:
            command.extend(["-f", str(frame_start), str(frame_end)])
        if step != 1:
            command.extend(["-i", str(step)])
        return command

    def set_dirmap(self, local_project, server_project, new_name_path, path):
        hou.hipFile.save(file_name=None)
        # # # # ENV # # # #
        for var, env_job in [(v, hou.getenv(v)) for v in config.houdini_envs]:
            if not env_job:
                continue
            env_job = env_job.replace(local_project, server_project)
            hou.hscript('setenv {}={}'.format(var, env_job))

        # # # # OPCHANGE # # # #
        hou.hscript('opchange {local} {server}'.format(local=local_project, server=server_project))
        hou.hipFile.setName(new_name_path)
        hou.hipFile.save(file_name=None)
        print("Save file : " + str(new_name_path))
        hou.hipFile.load(path, suppress_save_prompt=True)


def run():
    for x in get_houdini_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterHoudini()
    win.show()


if __name__ == '__main__':

    sub = SubmitterHoudini()
    sub.show()
