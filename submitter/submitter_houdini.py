import os
from datetime import datetime

import config
from .submitter_base import Submitter

import hou
from Qt.QtWidgets import QLineEdit


def get_houdini_window():
    return hou.qt.mainWindow()


class SubmitterHoudini(Submitter):

    def __init__(self, parent=get_houdini_window()):
        super(SubmitterHoudini, self).__init__(parent)
        self.output_node = QLineEdit()
        self.output_node.setPlaceholderText("Output Node : (ex: /out/mantra_ipr)")
        self.custom_layout.addWidget(self.output_node)
        self.input_job_name.setText(hou.getenv("FARM") or "")

    def get_path(self):
        return hou.hipFile.path()

    def pre_submit(self):
        path = hou.hipFile.path()
        start = int(hou.playbar.frameRange()[0])
        end = int(hou.playbar.frameRange()[1])
        # Test output_node
        if not hou.node(str(self.output_node.text())):
            self.error("Output node error ! please verify the node path")
        else:
            hou.hipFile.save()
            _renderer = hou.nodeType(str(self.output_node.text())).name()
            new_path = self.set_env_dirmap(path)
            if _renderer in ["redshift", "arnold"]:
                print("use {} renderer".format(_renderer))
                self.submit(new_path, start, end, "houdini", [_renderer])
            else:
                self.submit(new_path, start, end, "houdini")

    def task_command(self, is_linux, frame_start, frame_end, file_path, workspace=""):
        command = [
            config.batcher["houdini"]["hython"]["linux" if is_linux else "win"],
            config.batcher["houdini"]["hrender"]["linux" if is_linux else "win"],
            "%D({file_path})".format(file_path=file_path),
            "-e",
            "-d", str(self.output_node.text()),
            "-f", str(frame_start), str(frame_end),
        ]
        return command

    # Todo delete, weird thing
    def set_env_dirmap(self, path):
        """
        Replace dirmap env and create new file with correct location
        """
        #print(self.current_project)
        #print(self.get_project(path))
        proj = self.current_project or self.get_project(path)
        isLinux = self.is_linux()
        local_root = os.environ["ROOT_PIPE"] or "D:/SynologyDrive"
        local_project = '{}/{}'.format(local_root, proj["name"])
        template_server = '/{}/PFE_RN_2021/{}' if isLinux else '//{}/PFE_RN_2021/{}'
        server_project = template_server.format(proj["server"], proj["name"])
        # # # # ENV # # # #
        for var, env_job in [(v, hou.getenv(v)) for v in config.houdini_envs]:
            if not env_job:
                continue
            env_job = env_job.replace(local_project, server_project)
            hou.hscript('setenv {}={}'.format(var, env_job))

        # # # # OPCHANGE # # # #
        hou.hscript('opchange {local} {server}'.format(local=local_project, server=server_project))

        # # # # TEMP FILE # # # #
        file_name = hou.hipFile.basename()
        file_split = file_name.split(".")
        path_split = path.split("/")
        render_path = '/'.join(path_split[:-2]) + '/render'
        # Submission on the server directly
        # render_path = render_path.replace('I:/SynologyDrive/{project}'.format(project=current_project), root_path)
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
        new_name = "{version}_{file_name}_{timestamp}.{extension}".format(version=path_split[-2], file_name=file_split[0],
                                                                          timestamp=timestamp, extension=file_split[-1])
        new_name_path = os.path.join(render_path, new_name).replace(os.sep, '/')
        if not os.path.exists(render_path):
            if not os.path.exists(os.path.dirname(render_path)):
                if not hou.ui.displayConfirmation('The scene path does not exist on the server. \n{}\nAre you sure you want to create it ?'.format(render_path),
                                                  severity=hou.severityType.Message):
                    # reloading user file
                    hou.hipFile.load(hou.hipFile.name(), suppress_save_prompt=True)
                    return
                else:
                    os.makedirs(os.path.dirname(render_path))
            os.mkdir(render_path)

        hou.hipFile.setName(new_name_path)
        file_path = new_name_path
        hou.hipFile.save(file_name=None)
        return file_path


def run():
    for x in get_houdini_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterHoudini()
    win.show()


if __name__ == '__main__':

    sub = SubmitterHoudini()
    sub.show()
