# CSV Tool

## Description

This is a simple PyQt5-based GUI tool for working with CSV files. It offers multiple useful actions for session data processing and analysis.

## Features

- Update session statuses based on a report CSV  
- Count values in the `status` column  
- Find rows where `status == '-'`  
- Flag `real` rows if the same `person_id` has entries marked as `attack` or `virtual_camera`

## Requirements

- Python 3.x  
- pandas  
- PyQt5

## Installation

1. Clone or download the repository.
2. Install the required packages:

```bash
pip install pandas pyqt5
```

## Usage

Run the tool using:

```bash
python csv_tool.py
```

Once running:
- Select the desired action from the dropdown.
- Click **Select Files** to choose input files.
- Click **Run** to execute the selected action.
- View the results in the text area.

## Code Overview

The tool is built using:
- **QComboBox** for selecting the task
- **QFileDialog** for choosing files
- **QTextEdit** for displaying output
- **pandas** and **csv** modules for data processing

## Tasks Breakdown

1. **Update session status from report.csv**  
   Updates the `status` and `reason_for_status` fields in the session CSV based on failures found in the report file.

2. **Count statuses**  
   Counts and displays the number of occurrences for each unique value in the `status` column.

3. **Find sessions where status == '-'**  
   Identifies and lists the row numbers where the `status` field equals `'-'`.

4. **Flag 'real' rows if same person_id has attack or virtual_camera**  
   Marks rows with `status` = `real` as `need_revision` if the same `person_id` has `attack` or `virtual_camera` entries.
