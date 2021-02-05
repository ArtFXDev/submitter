from Qt.QtWidgets import QRadioButton
import nuke
import config
from .submitter_base import Submitter
from Qt.QtWidgets import QApplication

app = QApplication.instance()


def get_nuke_window():
    for widget in app.topLevelWidgets():
        if widget.metaObject().className() == 'Foundry::UI::DockMainWindow':
            return widget
    return None


class SubmitterNuke(Submitter):

    def __init__(self, parent=get_nuke_window()):
        super(SubmitterNuke, self).__init__(parent)
        self._rb_render_default = QRadioButton("Default")
        self._rb_render_redshift = QRadioButton("Redshift")
        self.custom_layout.addWidget(self._rb_render_default)
        self.custom_layout.addWidget(self._rb_render_redshift)

    def get_path(self):
        return nuke.root()["name"].value()

    def default_frame_range(self):
        start = int(nuke.root().firstFrame())
        end = int(nuke.root().lastFrame()) + 1
        step = 1
        return (start, end, step)

    def pre_submit(self):
        path = nuke.root()["name"].value()
        nuke.scriptSave()
        self.submit(path, "nuke")

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace=""):
        command = [
            config.batcher["nuke"]["render"]["linux" if is_linux else "win"],
            "-i",
            "-x",
            "%D({file_path})".format(file_path=file_path),
            "-F", "{start}-{end}x{step}".format(start=str(frame_start), end=str(frame_end), step=str(step)),
        ]
        return command

    def set_dirmap(self, local_project, server_project, new_name_path, path):
        nuke.scriptSaveAs(path)
        # # # # DIRNAME # # # #
        nuke.scriptSaveAs(new_name_path)
        print("Save file : " + str(new_name_path))
        nuke.scriptOpen(path)


def run():
    for x in get_nuke_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterNuke()
    win.show()


if __name__ == '__main__':

    sub = SubmitterNuke()
    sub.show()
