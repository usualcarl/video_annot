#Developed by usualcarl
import sys
import pandas as pd
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QTextEdit, QComboBox
)

class CSVToolApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Tool")

        self.layout = QVBoxLayout()

        self.task_selector = QComboBox()
        self.task_selector.addItems([
            "Select an action",
            "1. Update session status from report.csv",
            "2. Count statuses",
            "3. Find sessions where status == '-'",
            "4. Flag 'real' rows if same person_id has attack or virtual_camera"
        ])
        self.layout.addWidget(self.task_selector)

        self.select_files_btn = QPushButton("Select Files")
        self.select_files_btn.clicked.connect(self.select_files)
        self.layout.addWidget(self.select_files_btn)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_selected_task)
        self.layout.addWidget(self.run_btn)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.layout.addWidget(self.result_area)

        self.setLayout(self.layout)

        self.selected_paths = {}

    def select_files(self):
        task = self.task_selector.currentIndex()
        self.selected_paths.clear()

        if task == 1:
            report_path, _ = QFileDialog.getOpenFileName(self, "Select report file")
            sessions_path, _ = QFileDialog.getOpenFileName(self, "Select sessions CSV file")
            output_path, _ = QFileDialog.getSaveFileName(self, "Save updated CSV as")
            if report_path and sessions_path and output_path:
                self.selected_paths = {
                    "report": report_path,
                    "sessions": sessions_path,
                    "output": output_path
                }
        elif task in [2, 3, 4]:
            csv_path, _ = QFileDialog.getOpenFileName(self, "Select CSV file")
            if csv_path:
                self.selected_paths["csv"] = csv_path

    def run_selected_task(self):
        task = self.task_selector.currentIndex()

        if task == 1:
            self.update_session_status()
        elif task == 2:
            self.count_status_values()
        elif task == 3:
            self.find_empty_status_rows()
        elif task == 4:
            self.flag_persons_with_conflicts()
        else:
            self.result_area.setText("Please select an action.")

    def update_session_status(self):
        try:
            report_df = pd.read_csv(self.selected_paths["report"])
            sessions_df = pd.read_csv(self.selected_paths["sessions"])

            failed_reports = report_df[report_df["Result"] == "fail"]
            failures = dict(zip(failed_reports["Session ID"], failed_reports["Reason"]))

            sessions_df["status"] = sessions_df.apply(
                lambda row: "download_error" if row["session_id"] in failures else row.get("status", ""), axis=1
            )
            sessions_df["reason_for_status"] = sessions_df.apply(
                lambda row: failures.get(row["session_id"], row.get("reason_for_status", "")), axis=1
            )

            sessions_df.to_csv(self.selected_paths["output"], index=False)
            self.result_area.setText(f"File successfully updated and saved to:\n{self.selected_paths['output']}")
        except Exception as e:
            self.result_area.setText(f"Error: {e}")

    def count_status_values(self):
        try:
            df = pd.read_csv(self.selected_paths["csv"], dtype=str)
            if "status" in df.columns:
                counts = df["status"].value_counts(dropna=False)
                self.result_area.setText("Value counts in 'status' column:\n\n" + counts.to_string())
            else:
                self.result_area.setText("The file does not contain a 'status' column.")
        except Exception as e:
            self.result_area.setText(f"Error: {e}")

    def find_empty_status_rows(self):
        try:
            empty_rows = []
            with open(self.selected_paths["csv"], newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader, start=2):
                    if row.get('status', '').strip() == '-':
                        empty_rows.append(i)

            if empty_rows:
                result = "⚠️ Rows where status == '-' found at:\n" + \
                         "\n".join(map(str, empty_rows))
            else:
                result = "No rows with status == '-' found."
            self.result_area.setText(result)
        except Exception as e:
            self.result_area.setText(f"❌ Error: {e}")

    def flag_persons_with_conflicts(self):
        try:
            df = pd.read_csv(self.selected_paths["csv"], dtype=str)

            suspicious = df[df["status"].isin(["attack", "virtual_camera"])]
            person_to_reason = {}

            for _, row in suspicious.iterrows():
                pid = row["person_id"]
                if row["status"] == "attack":
                    person_to_reason[pid] = "attacks from this person_id"
                elif pid not in person_to_reason:
                    person_to_reason[pid] = "virtualcamera attacks from this person_id"

            updated_rows = 0
            for i, row in df.iterrows():
                pid = row.get("person_id")
                if row.get("status") == "real" and pid in person_to_reason:
                    df.at[i, "status"] = "need_revision"
                    df.at[i, "reason_for_status"] = person_to_reason[pid]
                    updated_rows += 1

            save_path, _ = QFileDialog.getSaveFileName(self, "Save updated CSV as")
            if save_path:
                df.to_csv(save_path, index=False)
                self.result_area.setText(f"Updated {updated_rows} 'real' rows.\nSaved to:\n{save_path}")
            else:
                self.result_area.setText("Operation cancelled. No file saved.")
        except Exception as e:
            self.result_area.setText(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVToolApp()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())
