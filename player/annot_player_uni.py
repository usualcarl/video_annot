#Developed by usualcarl
import sys
import os
import csv
from PyQt5 import QtWidgets, QtCore, QtGui, QtMultimedia, QtMultimediaWidgets

STATUSES = {
    QtCore.Qt.Key_1: "attack",
    QtCore.Qt.Key_2: "need_revision",
    QtCore.Qt.Key_3: "real",
    QtCore.Qt.Key_4: "virtual_camera",
}

class VideoWidget(QtMultimediaWidgets.QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setAspectRatioMode(QtCore.Qt.KeepAspectRatio)

class WelcomeDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome!")
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.setFixedSize(int(screen.width() * 0.2), int(screen.height() * 0.15))

        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Welcome to Video Annotator!\n\nChoose CSV-file and folder with sessions.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        self.start_button = QtWidgets.QPushButton("Choose")
        self.start_button.clicked.connect(self.accept)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

class VideoAnnotator(QtWidgets.QMainWindow):
    def __init__(self, csv_path, video_folder):
        super().__init__()
        self.setWindowTitle("Video Annotator")
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))

        self.csv_path = csv_path
        self.video_folder = video_folder

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.video_widget = VideoWidget()
        self.video_widget.setStyleSheet("background-color: black;")
        self.main_layout.addWidget(self.video_widget, stretch=6)

        self.media_player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)
        self.main_layout.addWidget(self.slider)

        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItem("All")
        self.filter_combo.addItems(["attack", "need_revision", "real", "virtual_camera"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        self.main_layout.addWidget(self.filter_combo)

        self.info_label = QtWidgets.QLabel(self)
        self.main_layout.addWidget(self.info_label)

        self.jump_input = QtWidgets.QLineEdit(self)
        self.jump_input.setPlaceholderText("Enter session_id to jump to video")
        self.jump_input.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.jump_input.returnPressed.connect(self.jump_to_session)
        self.main_layout.addWidget(self.jump_input)

        nav_buttons = QtWidgets.QHBoxLayout()
        self.prev_button = QtWidgets.QPushButton("Previous Video")
        self.next_button = QtWidgets.QPushButton("Next Video")
        self.prev_button.clicked.connect(self.play_previous_video)
        self.next_button.clicked.connect(self.play_next_video)
        nav_buttons.addWidget(self.prev_button)
        nav_buttons.addWidget(self.next_button)
        self.main_layout.addLayout(nav_buttons)

        speed_layout = QtWidgets.QHBoxLayout()
        self.playback_speed = 1.0
        self.speed_info = QtWidgets.QLabel(f"Speed: {self.playback_speed:.2f}x")
        self.speed_info.setAlignment(QtCore.Qt.AlignCenter)
        self.speed_down_button = QtWidgets.QPushButton("− Speed")
        self.speed_down_button.clicked.connect(lambda: self.change_speed(-0.25))
        self.speed_up_button = QtWidgets.QPushButton("+ Speed")
        self.speed_up_button.clicked.connect(lambda: self.change_speed(+0.25))
        speed_layout.addWidget(self.speed_down_button)
        speed_layout.addWidget(self.speed_info)
        speed_layout.addWidget(self.speed_up_button)
        self.main_layout.addLayout(speed_layout)

        self.play_pause_button = QtWidgets.QPushButton("Pause")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.main_layout.addWidget(self.play_pause_button)

        self.loop_button = QtWidgets.QPushButton("Toggle Loop")
        self.loop_button.setCheckable(True)
        self.loop_button.clicked.connect(self.toggle_loop)
        self.main_layout.addWidget(self.loop_button)

        status_buttons = QtWidgets.QHBoxLayout()
        for status in ["attack", "need_revision", "real", "virtual_camera"]:
            button = QtWidgets.QPushButton(status)
            button.clicked.connect(lambda checked, s=status: self.set_status(s))
            status_buttons.addWidget(button)
        self.main_layout.addLayout(status_buttons)

        self.current_index = 0
        self.rows = []
        self.filtered_indices = []
        self.loop_enabled = False

        self.load_csv()
        self.media_player.mediaStatusChanged.connect(self.check_video_end)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.apply_filter()

    def load_csv(self):
        with open(self.csv_path, newline='') as f:
            reader = csv.DictReader(f)
            self.fieldnames = reader.fieldnames
            self.rows = list(reader)

    def save_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)

    def apply_filter(self):
        selected = self.filter_combo.currentText()
        if selected == "All":
            self.filtered_indices = list(range(len(self.rows)))
        else:
            self.filtered_indices = [i for i, row in enumerate(self.rows) if row.get('status') == selected]
        self.current_index = 0
        self.play_current_video()

    def play_current_video(self):
        while self.current_index < len(self.filtered_indices):
            real_index = self.filtered_indices[self.current_index]
            row = self.rows[real_index]
            if row.get('status', '').strip() == "download_error":
                self.current_index += 1
                continue

            session_id = row['session_id']
            filename = f"{session_id}__alt_video.mp4"
            filepath = os.path.join(self.video_folder, filename)
            if os.path.exists(filepath):
                media = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(filepath))
                self.media_player.setMedia(media)
                self.media_player.setPlaybackRate(self.playback_speed)
                self.media_player.play()
                self.play_pause_button.setText("Pause")
                self.update_info_label()
                return
            else:
                self.current_index += 1

    def update_info_label(self):
        if self.filtered_indices:
            real_index = self.filtered_indices[self.current_index]
            row = self.rows[real_index]
            session_id = row['session_id']
            person_id = row['person_id']
            status = row.get('status', '')
            loop_text = "Loop: ON" if self.loop_enabled else "Loop: OFF"
            self.info_label.setText(
                f"Session: {session_id} | Person: {person_id} | Status: {status} | {loop_text} | Speed: {self.playback_speed:.2f}x | Video {self.current_index + 1} of {len(self.filtered_indices)}"
            )
            self.speed_info.setText(f"Speed: {self.playback_speed:.2f}x")

    def set_status(self, status):
        reason = ""
        if status in ["attack", "need_revision", "virtual_camera"]:
            reason, ok = QtWidgets.QInputDialog.getText(self, "Enter reason", f"Reason for status '{status}':")
            if not ok:
                return
        real_index = self.filtered_indices[self.current_index]
        self.rows[real_index]['status'] = status
        self.rows[real_index]['reason_for_status'] = reason
        self.save_csv()
        QtCore.QTimer.singleShot(300, self.advance_after_status)

    def advance_after_status(self):
        self.current_index += 1
        self.play_current_video()

    def keyPressEvent(self, event):
        key = event.key()
        if key in STATUSES:
            self.set_status(STATUSES[key])
        elif key == QtCore.Qt.Key_Backspace:
            self.play_previous_video()
        elif key in (QtCore.Qt.Key_Right, QtCore.Qt.Key_Up):
            self.play_next_video()
        elif key in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Down):
            self.play_previous_video()
        elif key == QtCore.Qt.Key_L:
            self.toggle_loop()
        elif key == QtCore.Qt.Key_Space:
            self.toggle_play_pause()
        elif key == QtCore.Qt.Key_BracketLeft:
            self.change_speed(-0.25)
        elif key == QtCore.Qt.Key_BracketRight:
            self.change_speed(+0.25)

    def change_speed(self, delta):
        new_speed = self.playback_speed + delta
        new_speed = max(0.25, min(4.0, new_speed))
        self.playback_speed = new_speed
        self.media_player.setPlaybackRate(self.playback_speed)
        self.update_info_label()

    def toggle_loop(self):
        self.loop_enabled = not self.loop_enabled
        self.update_info_label()

    def toggle_play_pause(self):
        if self.media_player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_button.setText("Pause")

    def check_video_end(self, status):
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            if self.loop_enabled:
                self.media_player.setPosition(0)
                self.media_player.play()
            else:
                self.play_pause_button.setText("Play")

    def play_previous_video(self):
        self.media_player.stop()
        self.current_index = max(0, self.current_index - 1)
        self.play_current_video()

    def play_next_video(self):
        self.media_player.stop()
        self.current_index = min(len(self.filtered_indices) - 1, self.current_index + 1)
        self.play_current_video()

    def jump_to_session(self):
        session_id = self.jump_input.text().strip()
        for i, idx in enumerate(self.filtered_indices):
            if self.rows[idx]['session_id'] == session_id:
                self.current_index = i
                self.play_current_video()
                self.jump_input.clearFocus()
                return
        QtWidgets.QMessageBox.warning(self, "Not Found", f"Session ID {session_id} not found.")
        self.jump_input.clearFocus()

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def position_changed(self, position):
        self.slider.setValue(position)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def closeEvent(self, event):
        self.media_player.stop()
        super().closeEvent(event)

def main():
    app = QtWidgets.QApplication(sys.argv)

    welcome = WelcomeDialog()
    if welcome.exec_() != QtWidgets.QDialog.Accepted:
        sys.exit()

    csv_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        None, "Choose the CSV file", "", "CSV Files (*.csv)"
    )
    if not csv_path:
        sys.exit()

    video_folder = QtWidgets.QFileDialog.getExistingDirectory(
        None, "Choose the folder with videos"
    )
    if not video_folder:
        sys.exit()

    player = VideoAnnotator(csv_path, video_folder)
    player.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
