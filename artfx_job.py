import os
import sys
import json

import config

for path in config.tractor_lib_paths:
    sys.path.append(path)

import tractor.api.author as author

from submitter.frame_manager import framerange_to_frames
from ocio_path import config_ocio_path, default_ocio


class ArtFxJob(author.Job):

    def __init__(self, *args, **kwargs):
        super(ArtFxJob, self).__init__(*args, **kwargs)
        self.dirmap_tractor()

    def add_task(self, name, command, services, path, project, frames_pattern, engine=None, plugins=None, is_linux=False, pre_command=""):
        """
        Add a task in the job
        :param str name: Name of the task
        :param str or list command: Command of the task
        :param str services: Services of the task
        :param bool is_linux: If is linux
        :param str or list pre_command: Command before the task
        """
        task = author.Task(title=name, service=services)
        cmd = author.Command(argv=command)
        # Build envkeys
        if project["server"] == "ana":
            root_pipe = "//{}" if not is_linux else "/{}"
        else:
            root_pipe = "//{}/PFE_RN_2021" if not is_linux else "/{}"
        root_pipe = root_pipe.format(project["server"])
        ocio = config_ocio_path[project["name"]] if project["name"] in config_ocio_path.keys() else default_ocio
        ocio = ocio.replace("/PFE_RN_2021", "")[1:] if is_linux else ocio
        _envkey = [
            "setenv ROOT_PIPE={} OCIO={}".format(root_pipe, ocio),
        ]
        if project["name"] == "BACKSTAGE":
            _envkey.append('setenv ARNOLD_PLUGIN_PATH=//tars/PFE_RN_2021/BACKSTAGE/03_WORK_PIPE/01_ASSET_3D/04_sets/empire_state_building/3d/Scripts')
        if engine:
            if engine == "houdini":
                import hou
                _envkey.append('setenv OUT={}'.format(hou.getenv("OUT").replace(config.output_server_win, config.output_server_lin) if is_linux else hou.getenv("OUT")))
                _envkey.append('setenv JOB={}'.format(hou.getenv("JOB").replace(os.getenv("ROOT_PIPE"), root_pipe)))
            _envkey.append(engine)
            if plugins:
                for plugin in plugins:
                    _envkey.append("{}-{}".format(engine, plugin))
                    if plugin == "arnold":
                        _envkey.append('setenv ARNOLD_PATHMAP={}/03_WORK_PIPE/04_TOOLS/02_FARM/path_mapping.json'.format(root_pipe + "/" + project["name"]))
                # _envkey.append('setenv HOUDINI_PATHMAP=\"{ "D:/SynologyDrive": "{' + root_pipe + '}" }\"')
        cmd.envkey = _envkey
        # Pre command
        if pre_command:
            pre_cmd = author.Command(argv=pre_command)
            pre_cmd.envkey = _envkey
            task.addCommand(pre_cmd)
        metadata = {"frames": framerange_to_frames(frames_pattern)}
        task.metadata = json.dumps(metadata)
        task.addCommand(cmd)
        self.addChild(task)

    def dirmap_tractor(self):
        """
        Tractor dirmap with config.project
        """
        local_root = os.environ["ROOT_PIPE"] or "D:/SynologyDrive"

        for project in config.projects:
            local_project = local_root + "/" + project["name"]
            if project["server"] == "ana":
                srv_project_win = "//{server}/{name}".format(server=project["server"], name=project["name"])
                srv_project_linux = "/{server}/{name}".format(server=project["server"], name=project["name"])
            else:
                srv_project_win = "//{server}/PFE_RN_2021/{name}".format(server=project["server"], name=project["name"])
                srv_project_linux = "/{server}/{name}".format(server=project["server"], name=project["name"])

            self.newDirMap(src=local_project, dst=srv_project_win, zone="UNC")
            self.newDirMap(src=local_project, dst=srv_project_linux, zone="NFS")

def command(*args, **kwargs):
    return author.Command(*args, **kwargs)

def set_engine_client(user):
    author.setEngineClientParam(user=user, debug=True)
