import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QDialog, QCheckBox, QDialogButtonBox,
    QLabel, QScrollArea, QLineEdit, QFrame, QToolButton, QSpacerItem,
    QSizePolicy, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QIntValidator, QMouseEvent
import json
from collections import defaultdict
import os
from utils import show_message

# Global variable to detect change
on_change = False

class MultiSelectDialog(QDialog):
    def __init__(self, parent=None, current_data=None):
        super().__init__(parent)
        self.setWindowTitle("Select Interaction & Parameters")
        self.setFixedSize(400, 450)

        self.setStyleSheet("""
            QDialog {
                background-color: #3d4653;
                color: white;
                border: 1px solid #749BC2;
                border-radius: 5px;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
            QCheckBox {
                color: white;
                font-size: 14px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #749BC2;
                border-radius: 3px;
                background-color: #2f3542;
            }
            QCheckBox::indicator:checked {
                background-color: #70a1ff;
                border: 1px solid #70a1ff;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #a0c2e6;
            }
            QPushButton {
                background-color: #70a1ff;
                color: white;
                padding: 1px 15px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1e90ff;
            }
            QPushButton:pressed {
                background-color: #007bff;
            }
            QLineEdit {
                background-color: #2f3542;
                border: 1px solid #749BC2;
                color: white;
                padding: 4px;
                border-radius: 3px;
            }
        """)

        self.options = ["H", "P", "B"]
        self.selected_data = current_data if current_data else {'level': None, 'H': [], 'P': [], 'B': []}
        self.parameter_layouts = {}
        self.parameter_widgets = {}
        self.checkboxes = {}

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Define Interaction")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(title_label)

        # Interaction Level Input Field
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Interaction level:"))
        initial_level_text = str(self.selected_data['level']) if self.selected_data.get('level') is not None else ''
        self.level_input = QLineEdit(initial_level_text)
        self.level_input.setValidator(QIntValidator())
        self.level_input.setPlaceholderText("Enter a number")
        level_layout.addWidget(self.level_input)
        main_layout.addLayout(level_layout)

        # Scroll area for parameters
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(15)

        for option in self.options:
            option_frame = QFrame()
            option_layout = QVBoxLayout(option_frame)
            option_layout.setContentsMargins(0, 0, 0, 0)
            option_layout.setSpacing(5)

            # Checkbox and Add button
            checkbox_layout = QHBoxLayout()
            checkbox = QCheckBox(f"Parameters ({option})")
            checkbox.setObjectName(option)
            checkbox.setChecked(len(self.selected_data.get(option, [])) > 0)
            checkbox.stateChanged.connect(self.on_checkbox_state_changed)
            self.checkboxes[option] = checkbox
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.addStretch()

            add_btn = QPushButton("+ Add")
            add_btn.setObjectName(f"add_{option}")
            add_btn.clicked.connect(lambda _, opt=option: self.add_parameter_input(opt))
            add_btn.setStyleSheet("""
                QPushButton { background-color: #4CAF50; padding: 2px 8px; font-size: 12px; }
                QPushButton:hover { background-color: #45a049; }
            """)
            checkbox_layout.addWidget(add_btn)

            option_layout.addLayout(checkbox_layout)

            # Container for parameter input fields
            parameters_container = QWidget()
            parameters_layout = QVBoxLayout(parameters_container)
            parameters_layout.setContentsMargins(20, 0, 0, 0)
            parameters_layout.setSpacing(5)

            self.parameter_layouts[option] = parameters_layout
            self.parameter_widgets[option] = []

            option_layout.addWidget(parameters_container)
            scroll_layout.addWidget(option_frame)

            # Populate with existing data
            for param in self.selected_data.get(option, []):
                self.add_parameter_input(option, param)

            # Initially enable/disable based on checkbox state
            parameters_container.setEnabled(self.checkboxes[option].isChecked())
            add_btn.setEnabled(self.checkboxes[option].isChecked())

        scroll_layout.addStretch()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)

    def on_checkbox_state_changed(self, state):
        
        sender = self.sender()
        option = sender.objectName()
        parameters_container = self.parameter_layouts[option].parentWidget()
        add_btn = self.findChild(QPushButton, f"add_{option}")
        
        if state == Qt.Checked:
            parameters_container.setEnabled(True)
            add_btn.setEnabled(True)
            if not self.parameter_widgets[option]:
                self.add_parameter_input(option)
        else:
            parameters_container.setEnabled(False)
            add_btn.setEnabled(False)
            self.clear_parameters(option)

    def add_parameter_input(self, option, value=""):
        
        param_widget = QWidget()
        param_layout = QHBoxLayout(param_widget)
        param_layout.setContentsMargins(0, 0, 0, 0)

        line_edit = QLineEdit(value)
        line_edit.setPlaceholderText("Parameter Name")
        param_layout.addWidget(line_edit)

        remove_btn = QPushButton("Remove")
        remove_btn.setStyleSheet("""
            QPushButton { background-color: #E43636; padding: 2px 8px; font-size: 12px; }
            QPushButton:hover { background-color: #DC2525; }
        """)
        remove_btn.clicked.connect(lambda: self.remove_parameter_input(option, param_widget))
        param_layout.addWidget(remove_btn)

        self.parameter_layouts[option].addWidget(param_widget)
        self.parameter_widgets[option].append(param_widget)

    def remove_parameter_input(self, option, widget):
        
        self.parameter_layouts[option].removeWidget(widget)
        widget.deleteLater()
        self.parameter_widgets[option].remove(widget)

    def clear_parameters(self, option):
        
        for widget in self.parameter_widgets[option]:
            self.parameter_layouts[option].removeWidget(widget)
            widget.deleteLater()
        self.parameter_widgets[option] = []

    def accept(self):
        global on_change
        on_change = True
        self.selected_data = {}
        level_text = self.level_input.text().strip()
        self.selected_data['level'] = int(level_text) if level_text else None
        
        for option in self.options:
            if self.checkboxes[option].isChecked():
                params = [w.findChild(QLineEdit).text().strip() for w in self.parameter_widgets[option] if w.findChild(QLineEdit).text().strip()]
                self.selected_data[option] = params
            else:
                self.selected_data[option] = []
        super().accept()

    def get_selected_data(self):
        return self.selected_data


class APIMatrixApp(QWidget):
    def __init__(self, api_names, scenario_name, parent=None):
        super().__init__(parent)
        self.api_names = api_names
        self.matrix_buttons = {}
        self.cell_width = 120
        self.cell_height = 60
        self._adjusting_matrix = False
        self.scenario_name = scenario_name
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2f3542;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #57606f;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
                border: 1px solid #4a5364;
            }
            QPushButton:hover {
                background-color: #70a1ff;
                border: 1px solid #70a1ff;
            }
            QPushButton:pressed {
                background-color: #007bff;
            }
            QPushButton {
                background-color: #3d4653;
                border: 1px solid #4a5364;
                border-radius: 5px;
                color: #e0e0e0;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #57606f;
                border: 1px solid #749BC2;
            }
            QPushButton:pressed {
                background-color: #4a5364;
            }
            QPushButton.selected {
                background-color: #5cb85c;
                border: 1px solid #4cae4c;
                color: white;
                font-weight: bold;
            }
            QPushButton.selected:hover {
                background-color: #4cae4c;
            }
            QPushButton.selected:pressed {
                background-color: #3f903f;
            }
            QPushButton.no_selection {
                background-color: #3d4653;
                border: 1px solid #70a1ff;
                color: white;
                font-weight: normal;
            }
            QPushButton.no_selection:hover {
                background-color: #70a1ff;
            }
            QPushButton.no_selection:pressed {
                background-color: #c9302c;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        grid_container_layout = QHBoxLayout()
        grid_container_layout.setContentsMargins(0, 0, 0, 0)
        grid_container_layout.addStretch(1)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.x_axis_labels = []
        for col_idx, api_name in enumerate(self.api_names):
            label = QLabel(api_name)
            label.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
            label.setFont(QFont("Arial", 4, QFont.Bold))
            label.setContentsMargins(0, 0, 0, 0)
            label.setWordWrap(True)
            self.x_axis_labels.append(label)
            self.grid_layout.addWidget(label, 0, col_idx + 1)

        self.y_axis_labels = self.api_names

        for row_idx, output_api in enumerate(self.y_axis_labels):
            for col_idx, input_api in enumerate(self.api_names):
                button = QPushButton()
                button.setFont(QFont("Arial", 4))
                tooltip_text = f"Input: {input_api}\nOutput: {output_api}"
                button.setToolTip(tooltip_text)
                button.setProperty("class", "no_selection")
                button.setProperty("interaction_data", {'level': None, 'H': [], 'P': [], 'B': []})
                self.matrix_buttons[(row_idx, col_idx)] = button
                button.clicked.connect(lambda _, r=row_idx, c=col_idx: self.open_multi_select(r, c))
                self.grid_layout.addWidget(button, row_idx + 1, col_idx + 1)

        grid_container_layout.addLayout(self.grid_layout)
        grid_container_layout.addStretch(1)

        main_layout.addStretch(1)
        main_layout.addLayout(grid_container_layout)
        main_layout.addStretch(1)

    def adjust_matrix_size(self):
        if self._adjusting_matrix:
            return

        self._adjusting_matrix = True
        try:
            num_apis = len(self.api_names)
            if num_apis == 0:
                return
            available_width = self.parent().width() - 20
            available_height = self.parent().height() - 20
            max_x_label_height = 60
            max_y_label_width = 0
            total_horizontal_spacing = self.grid_layout.spacing() * (num_apis + 1)
            total_vertical_spacing = self.grid_layout.spacing() * (num_apis + 1)
            grid_available_width = available_width - max_y_label_width - total_horizontal_spacing
            grid_available_height = available_height - max_x_label_height - total_vertical_spacing
            min_cell_side = 75
            max_cell_side = 120
            calculated_horizontal_side = grid_available_width / max(1, num_apis)
            calculated_vertical_side = grid_available_height / max(1, num_apis)
            ideal_side_length = min(calculated_horizontal_side, calculated_vertical_side)
            self.cell_width = int(min(max(min_cell_side, ideal_side_length), max_cell_side))
            self.cell_height = self.cell_width
            for button in self.matrix_buttons.values():
                button.setFixedSize(self.cell_width, self.cell_height)
            for label in self.x_axis_labels:
                label.setFixedSize(self.cell_width, max_x_label_height)
        finally:
            self._adjusting_matrix = False

    def open_multi_select(self, row, col):
        button = self.matrix_buttons[(row, col)]
        current_data = button.property("interaction_data")
        
        dialog = MultiSelectDialog(self, current_data=current_data)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_data = dialog.get_selected_data()
            button.setProperty("interaction_data", selected_data)
            
            level = selected_data.get('level')
            categories = [key for key in ['H', 'P', 'B'] if selected_data.get(key)]
            
            if level is not None or categories:
                button_text_parts = []
                if level is not None:
                    button_text_parts.append(str(level))
                if categories:
                    button_text_parts.append(f"({' '.join(categories)})")
                
                button.setText(" ".join(button_text_parts))
                button.setProperty("class", "selected")
            else:
                button.setText("")
                button.setProperty("class", "no_selection")
                
            button.style().polish(button)

    def save_interactions(self):
        global on_change
        on_change = False
        output_data = {}
        
        interactions_by_input_api = {api: [] for api in self.api_names}
        
        for (row_idx, col_idx), button in self.matrix_buttons.items():
            interaction_data = button.property("interaction_data")
            level = interaction_data.get('level')
            
            if level is not None:
                output_api_name = self.api_names[row_idx]
                input_api_name = self.api_names[col_idx]

                interactions_by_input_api[input_api_name].append({
                    "level": level,
                    "output_api": output_api_name,
                    "data": interaction_data
                })

        for input_api, interactions in interactions_by_input_api.items():
            if not interactions:
                output_data[input_api] = {"response": {}, "level": []}
                continue

            # Group interactions by level
            grouped_levels = defaultdict(list)
            api_entry = {
                "response": {},
                "level": [],
            }

            for interaction in interactions:
                level = interaction['level']
                output_api = interaction['output_api']
                data = interaction['data']
                
                # Append the output API to the list for its level
                grouped_levels[level].append(output_api)
                
                # Also, add the data to the main dictionary, similar to your original code
                api_entry[output_api] = {
                    key: data.get(key, []) for key in ['H', 'P', 'B'] if data.get(key)
                }

            # Sort the levels numerically and then add the lists of APIs to the "level" key
            sorted_levels = sorted(grouped_levels.keys())
            api_entry["level"] = [grouped_levels[level] for level in sorted_levels]
            
            # The previous approach for `api_entry[output_api]` seems to be overwriting a key.
            # You might want to restructure this part depending on the desired final output.
            # Assuming you want the `level` list and the individual API data in the same dictionary.
            output_data[input_api] = api_entry
            
        print(json.dumps(output_data, indent=4))
        
        file_path = os.path.join("interactions",self.scenario_name + "_interactions.json")

        if not os.path.exists(file_path):
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
        with open(file_path, "w") as f:
            json.dump(output_data, f, indent=4)
        
        return output_data

class MainWindow(QMainWindow):
    def __init__(self, api_names, scenario_name):
        super().__init__()
        self.api_names = api_names
        self.scenario_name = scenario_name
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(200, 200, 1200, 900)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2f3542;
                border: 1px solid #749BC2;
                border-radius: 5px;
            }
            QFrame#ClientMenuBar {
                background-color: #3d4653;
                border-bottom: 1px solid #4a5364;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #70a1ff;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1e90ff;
            }
            QToolButton {
                background-color: transparent;
                padding: 6px 12px;
                border: none;
                border-radius: 6px;
                color: white;
            }
            QToolButton:hover {
                background-color: #70a1ff;
                border: 1px solid white;
            }
            QMenu {
                background-color: #57606f;
                color: white;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #70a1ff;
            }
            QFrame#ClientMenuBar {
                background-color: #D7D7D7;
                border-bottom: none;
                border-top: none;
                border-left: none;
                border-right: none;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.custom_title_bar = self.create_custom_menu_bar()
        main_layout.addWidget(self.custom_title_bar)
        self.client_menu_bar = self.create_client_menu_bar()
        main_layout.addWidget(self.client_menu_bar)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: #2f3542; border: none; }")
        
        self.matrix_widget = APIMatrixApp(self.api_names, self.scenario_name, scroll_area)
        scroll_area.setWidget(self.matrix_widget)
        main_layout.addWidget(scroll_area)
        self.old_pos = None
        self.load_interactions()

    def create_custom_menu_bar(self):
        menu_bar = QFrame()
        menu_bar.setFixedHeight(40)
        menu_bar.setStyleSheet("background-color: #57606f;")
        menu_bar.mousePressEvent = self.mousePressEvent
        menu_bar.mouseMoveEvent = self.mouseMoveEvent
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(10)
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        minimize = QToolButton()
        minimize.setText("–")
        minimize.setStyleSheet("font-size: 17px;")
        minimize.clicked.connect(self.showMinimized)
        layout.addWidget(minimize)
        maximize = QToolButton()
        maximize.setText("▭")
        maximize.setStyleSheet("font-size: 17px;")
        maximize.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        layout.addWidget(maximize)
        close = QToolButton()
        close.setText("x")
        close.setStyleSheet("font-size: 16px; padding-top: 5px;")
        close.clicked.connect(self.close)
        layout.addWidget(close)
        menu_bar.setLayout(layout)
        return menu_bar

    def create_client_menu_bar(self):
        client_menu_bar = QFrame()
        client_menu_bar.setFixedHeight(35)
        client_menu_bar.setObjectName("ClientMenuBar")
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(10)
        layout.addStretch()
        save_btn = QPushButton("Save")
        save_btn.setToolTip("Save interactions")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #328E6E; color: white; border: none;
                border-radius: 5px; padding: 6px 12px; font-size: 13px;
            }
            QPushButton:hover { background-color: #3F7D58; }
        """)
        
        save_btn.clicked.connect(self.save_data)

        layout.addWidget(save_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setToolTip("Cancel without saving")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #E43636; color: white; border: none;
                border-radius: 5px; padding: 6px 12px; font-size: 13px;
            }
            QPushButton:hover { background-color: #DC2525; }
        """)
        cancel_btn.clicked.connect(self.cancel_exit)
        layout.addWidget(cancel_btn)
        client_menu_bar.setLayout(layout)
        return client_menu_bar

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and event.y() < self.custom_title_bar.height():
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos is not None and self.isMaximized() == False:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    
    def showEvent(self, event):
        QTimer.singleShot(0, self.matrix_widget.adjust_matrix_size)
        super().showEvent(event)

    def resizeEvent(self, event):
        QTimer.singleShot(0, self.matrix_widget.adjust_matrix_size)
        super().resizeEvent(event)

    def save_data(self):
        self.matrix_widget.save_interactions()
        show_message("Save Successful", "API interactions have been saved.", level="info")        
        self.close()

    def cancel_exit(self):
        reply = show_message('Confirmation', 'Are you sure you want to exit?', level="question")

        if reply == QMessageBox.Yes:
            self.close()

    def closeEvent(self, event):
        global on_change
        if on_change == True:
            on_change = False
            reply = show_message("Confirmation", 'Are you sure you want to exit?', level="question")

            if reply == QMessageBox.Yes:  # Yes clicked
                event.accept()
            else:      # No clicked
                event.ignore()
        else:
            event.accept()

    def load_interactions(self):
        """Loads interactions from a JSON file and updates the matrix UI."""
        file_path = os.path.join("interactions", self.scenario_name + "_interactions.json")

        if not os.path.exists(file_path):
            return

        try:
            with open(file_path, "r") as f:
                saved_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            show_message("Load Error", f"Failed to load interactions: {e}", level="warning")
            return

        # Iterate through the API names to find corresponding buttons
        for col_idx, input_api_name in enumerate(self.api_names):
            if input_api_name in saved_data:
                api_data = saved_data[input_api_name]
                
                # Iterate through all other APIs that have an interaction
                for row_idx, output_api_name in enumerate(self.api_names):
                    # Check if the output API exists as a key in the loaded data
                    if output_api_name in api_data:
                        button = self.matrix_widget.matrix_buttons.get((row_idx, col_idx))
                        if button:
                            # Reconstruct the interaction_data dictionary
                            interaction_data = {
                                'level': None,
                                'H': api_data.get(output_api_name, {}).get('H', []),
                                'P': api_data.get(output_api_name, {}).get('P', []),
                                'B': api_data.get(output_api_name, {}).get('B', [])
                            }
                            
                            # Find the level from the 'level' list in the saved data
                            # This is a bit tricky due to the data structure
                            for level_list in api_data.get('level', []):
                                if output_api_name in level_list:
                                    # The level for this interaction is the index + 1
                                    interaction_data['level'] = api_data['level'].index(level_list) + 1
                                    break
                            
                            # Update the button's properties and appearance
                            button.setProperty("interaction_data", interaction_data)
                            
                            button_text_parts = []
                            if interaction_data['level'] is not None:
                                button_text_parts.append(str(interaction_data['level']))
                            
                            categories = [key for key in ['H', 'P', 'B'] if interaction_data.get(key)]
                            if categories:
                                button_text_parts.append(f"({' '.join(categories)})")
                            
                            if button_text_parts:
                                button.setText(" ".join(button_text_parts))
                                button.setProperty("class", "selected")
                            else:
                                button.setText("")
                                button.setProperty("class", "no_selection")
                                
                            button.style().polish(button)

if __name__ == '__main__':  
    app = QApplication(sys.argv)
    sys.exit(app.exec_())