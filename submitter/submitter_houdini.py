import config
from .submitter_base import Submitter
import os
import hou
from Qt.QtWidgets import QLineEdit


def get_houdini_window():
    return hou.qt.mainWindow()


class SubmitterHoudini(Submitter):

    def __init__(self, parent=get_houdini_window()):
        super(SubmitterHoudini, self).__init__(parent)
        self.output_node = QLineEdit()
        self.output_node.setPlaceholderText("Output Node : (ex: /out/mantra1)")
        self.custom_layout.addWidget(self.output_node)
        self.input_job_name.setText(hou.getenv("FARM") or "")

    def pre_submit(self):
        path = hou.hipFile.path()
        start = int(hou.playbar.frameRange()[0])
        end = int(hou.playbar.frameRange()[1])
        # Test output_node
        if not hou.node(str(self.output_node.text())):
            self.error("Output node error ! please verify the node path")
        hou.hipFile.save()
        self.submit(path, start, end, "houdini")

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

    def get_env_var(self, path):
        """
        Get the env variable in the current path
        :return: A dictionary with key: env name and value: env value
        :rtype: dict
        """
        env_dict = {}
        workspace_path = path.split('/scenes')[0]
        pnum = ''
        snum = ''
        name = ''
        if '02_SHOT' in path.split('/'):
            shot_path = path.split('02_SHOT')[0] + '02_SHOT/3d'
            asset_path = path.split('02_SHOT')[0] + '01_ASSET_3D'
            pnum = path.split('/')[8]
            snum = path.split('/')[7]
            wipcache_path = os.path.join(path.split('02_SHOT/3d/scenes')[0],
                                         '03_WIP_CACHE_FX', pnum, snum).replace(os.sep, '/')
            pubcache_path = os.path.join(path.split('02_SHOT/3d/scenes')[0],
                                         '04_PUBLISH_CACHE_FX', pnum, snum).replace(os.sep, '/')
        else:
            shot_path = path.split('01_ASSET_3D')[0] + '02_SHOT/3d'
            asset_path = path.split('01_ASSET_3D')[0] + '01_ASSET_3D'
            name = path.split('/')[6]
            wipcache_path = os.path.join(path.split('01_ASSET_3D')[
                                         0], '03_WIP_CACHE_FX', name).replace(os.sep, '/')
            pubcache_path = os.path.join(path.split('01_ASSET_3D')[
                                         0], '04_PUBLISH_CACHE_FX', name).replace(os.sep, '/')

        project = path.split('/03_WORK_PIPE')[0]

        env_dict['JOB'] = workspace_path
        env_dict['WIPCACHE'] = wipcache_path
        env_dict['PUBCACHE'] = pubcache_path
        env_dict['ASSET'] = asset_path
        env_dict['SHOT'] = shot_path
        env_dict['PNUM'] = pnum
        env_dict['SNUM'] = snum
        env_dict['ASSET_NAME'] = name
        env_dict['PROJECT'] = project
        return env_dict


def run():
    for x in get_houdini_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterHoudini()
    win.show()


if __name__ == '__main__':

    sub = SubmitterHoudini()
    sub.show()
