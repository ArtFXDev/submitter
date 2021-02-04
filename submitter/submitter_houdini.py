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

    def default_frame_range(self):
        start = int(hou.playbar.frameRange()[0])
        end = int(hou.playbar.frameRange()[1])
        return (start, end)

    def pre_submit(self):
        path = hou.hipFile.path()
        # Test output_node
        if not hou.node(str(self.output_node.text())):
            self.error("Output node error ! please verify the node path")
        else:
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

    # Todo delete, weird thing
    def set_env_dirmap(self, path):
        """
        Replace dirmap env and create new file with correct location
        """
        # print(self.current_project)
        # print(self.get_project(path))
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
        file_name = hou.hipFile.basename().replace(os.sep, "/")
        file_split = file_name.split(".")
        path_split = path.split("/")
        render_path = '/'.join(path_split[:-2]) + '/render'
        # Submission on the server directly
        # Use windows path becose only windows use submitter
        server_project_win = '//{}/PFE_RN_2021/{}'.format(proj["server"], proj["name"])
        render_path = render_path.replace('D:/SynologyDrive/{}'.format(proj["name"]), server_project_win)
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
        new_name = "{version}_{file_name}_{timestamp}.{extension}".format(version=path_split[-2], file_name=file_split[0],
                                                                          timestamp=timestamp, extension=file_split[-1])
        new_name_path = os.path.join(render_path, new_name).replace(os.sep, '/')
        print("check if path exist : "+render_path )
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
        hou.hipFile.save(file_name=None)
        print("Save file : " + str(new_name_path))
        hou.hipFile.load(path, suppress_save_prompt=True)
        # Remap to local path for comand dirmap by tractor
        new_name_path = new_name_path.replace(server_project_win, 'D:/SynologyDrive/{}'.format(proj["name"]))
        return new_name_path

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
