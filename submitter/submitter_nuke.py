from Qt.QtWidgets import QRadioButton
import nuke
import config
from .submitter_base import Submitter
from Qt.QtGui import QApplication

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

    def pre_submit(self):
        path = nuke.root()["name"].value()
        start = int(nuke.root().firstFrame())
        end = int(nuke.root().lastFrame()) + 1
        nuke.scriptSave()
        self.submit(path, start, end, "nuke")

    def task_command(self, is_linux, frame_start, frame_end, file_path, workspace=""):
        command = [
            config.batcher["nuke"]["render"]["linux" if is_linux else "win"],
            "-x",
            # "-remap", "{source},%D({target})".format(source=file_path_start, target=file_path_start),
            "-F", "{start} {end}".format(start=str(frame_start), end=str(frame_end)),
            "%D({file_path})".format(file_path=file_path)
        ]
        return command


def run():
    for x in get_nuke_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterNuke()
    win.show()


if __name__ == '__main__':

    sub = SubmitterNuke()
    sub.show()
