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
        self.rop_node = None
        self.list_rop = []
        
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
            print("#######pre submit#########")
            print("node = "+self.output_node.text())
            self.rop_node = hou.node(self.output_node.text())
            #print("self.output_node.type().name() = "+self.output_node.type().name())
            if(self.rop_node.type().name() == "merge"):
                list_rop = self.rop_node.inputs()
                for rop in list_rop:
                    self.list_rop.append(rop.path())
                print("merge detected. Nodes = "+str(self.list_rop))
            else :
                self.list_rop = [self.rop_node.path()]

            for node in self.list_rop:
                print("start render for node "+node)
                #self.output_node.setText(node.path())
                self.rop_node=node
                hou.hipFile.save()
                print("self.rop_node.type() = "+str(hou.node(self.rop_node).type().name()))
                _renderer = hou.node(self.rop_node).type().name().lower()
                # new_path = self.set_env_dirmap(path)
                use_renderer = False
                for renderer_loop in ["redshift", "arnold", "vray"]:
                    if _renderer.startswith(renderer_loop):
                        self.submit(path, "houdini", [renderer_loop])
                        use_renderer = True
                        break
                if not use_renderer:
                    self.submit(path, "houdini")
                print( "######### "+node + " submitted ############")

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

    def set_dirmap(self, local_project, server_project, new_name_path, path):
        hou_node = hou.node(self.rop_node)
        print("set_dirmap : new_name_path = "+new_name_path+" | rop node = "+hou_node.name())
        new_name_path = new_name_path.replace(".hipnc","_"+hou_node.name()+".hipnc") #add the rop name to handle rendering with merge node
        print("set_dirmap : new_name_path = "+new_name_path)
        
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
        self.new_name = new_name_path
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
