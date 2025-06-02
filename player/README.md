
# Video Annotator

**PyQt5 Video Annotation Tool**

This project is a handy tool for annotating videos using a PyQt5 interface and QtMultimedia module.  
It allows you to browse video files, assign a status to each session (e.g., `attack`, `need_revision`, `real`, `virtual_camera`), and save the results back into a CSV file.

---

## Main Features

CSV session support  
Status filtering  
Hotkeys for quick annotation  
Seek bar and playback speed adjustment  
Loop playback support  
Reason input for specific statuses  
Jump directly to a `session_id`

---

## Installation

Make sure you have Python 3.9+ installed  
Install dependencies:
```bash
pip install PyQt5
```

---

## Project Structure

- **main.py** — main executable file  
- **CSV file** — list of sessions and statuses  
- **video folder** — should contain files named `<session_id>__alt_video.mp4`

---

## Usage

Run the application:
```bash
python main.py
```

In the opened window:
- select the CSV file  
- select the folder with videos  

Start annotating:
- keys **1-4** → assign statuses (`attack`, `need_revision`, `real`, `virtual_camera`)  
- **Previous/Next** buttons → navigate between videos  
- **L** → toggle loop playback  
- **Spacebar** → play/pause  
- **[ / ]** → decrease/increase speed  
- input field → jump to a specific `session_id`

All changes are automatically saved back to the selected CSV file.

---

## Hotkeys

| Key                  | Action                               |
|----------------------|-------------------------------------|
| 1                   | Set status `attack`                 |
| 2                   | Set status `need_revision`          |
| 3                   | Set status `real`                  |
| 4                   | Set status `virtual_camera`        |
| Backspace / ← / ↑   | Previous video                     |
| → / ↓              | Next video                          |
| L                  | Toggle loop mode                    |
| Spacebar           | Pause/resume video                  |
| [ / ]              | Adjust playback speed               |

---

## CSV Format

The CSV file is expected to have at least the following columns:
- `session_id`
- `person_id`
- `status`
- `reason_for_status`
