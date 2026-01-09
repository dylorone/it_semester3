from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStatusBar, QColorDialog, QGraphicsItem, QMessageBox, \
    QFileDialog
from PySide6.QtGui import QAction, QKeySequence, QBrush, QColor

from logic.factory import ShapeFactory
from logic.file_manager import FileManager
from logic.save_strategies import ImageSaveStrategy, JsonSaveStrategy
from logic.shapes import ShapeMixin
from ui.properties_panel import PropertiesPanel
from widgets.canvas import EditorCanvas
from ui.tool_panel import ToolPanel


class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vector Editor v0.1")
        self.resize(1024, 768)

        self._setup_layout()
        self._init_menu()

        self._connect_signals()

        self.set_active_tool("line")

        self.statusBar().showMessage("Готов к работе")

    def _init_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        load_action = QAction("Open", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_project)
        file_menu.addAction(load_action)

        edit_menu = menubar.addMenu("&Edit")

        stack = self.canvas.undo_stack

        undo_action = stack.createUndoAction(self, "&Undo")
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)

        redo_action = stack.createRedoAction(self, "&Redo")
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()

        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.canvas.delete_selection)

        edit_menu.addAction(delete_action)
        self.addAction(delete_action)

        group_action = QAction("Group", self)
        group_action.setShortcut(QKeySequence("Ctrl+G"))
        group_action.setStatusTip("Сгруппировать выделенные объекты")
        group_action.triggered.connect(self.canvas.group_selection)
        edit_menu.addAction(group_action)

        ungroup_action = QAction("Ungroup", self)
        ungroup_action.setShortcut(QKeySequence("Ctrl+U"))
        ungroup_action.setStatusTip("Разгруппировать объекты")
        ungroup_action.triggered.connect(self.canvas.ungroup_selection)
        edit_menu.addAction(ungroup_action)

    def _setup_layout(self):
        central_container = QWidget()
        self.setCentralWidget(central_container)

        main_layout = QHBoxLayout(central_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tool_panel = ToolPanel()
        self.canvas = EditorCanvas()

        self.props_panel = PropertiesPanel(self.canvas.scene)

        main_layout.addWidget(self.tool_panel)
        main_layout.addWidget(self.canvas)

        main_layout.addWidget(self.props_panel)


    def _connect_signals(self):
        """Здесь мы подписываемся на события кнопок из панели инструментов"""

        self.tool_panel.btn_select.clicked.connect(lambda: self.set_active_tool("select"))
        self.tool_panel.btn_line.clicked.connect(lambda: self.set_active_tool("line"))
        self.tool_panel.btn_rect.clicked.connect(lambda: self.set_active_tool("rect"))
        self.tool_panel.btn_ellipse.clicked.connect(lambda: self.set_active_tool("ellipse"))

        self.tool_panel.btn_color.clicked.connect(self.open_color_dialog)

        if hasattr(self.tool_panel, 'btn_group'):
            self.tool_panel.btn_group.clicked.connect(self.canvas.group_selection)
            self.tool_panel.btn_ungroup.clicked.connect(self.canvas.ungroup_selection)

    def open_color_dialog(self):
        """Открывает системное окно выбора цвета"""
        color = QColorDialog.getColor()

        if color.isValid():
            color_hex = color.name()

            self.canvas.set_color(color_hex)

            self.tool_panel.btn_color.setStyleSheet(
                f"background-color: {color_hex}; border: 2px solid #555; color: black;"
            )

            for item in self.canvas.scene.selectedItems():
                if hasattr(item, 'set_active_color'):
                    item.set_active_color(color_hex)

            self.statusBar().showMessage(f"Выбран цвет: {color_hex}")

    def set_active_tool(self, tool_name):
        """Слот, который срабатывает при нажатии кнопок"""
        print(f"Window: Выбран инструмент {tool_name}")

        self.canvas.set_tool(tool_name)

        self._update_button_visuals(tool_name)

        self.statusBar().showMessage(f"Инструмент: {tool_name}")

    def _update_button_visuals(self, active_name):
        """Делаем кнопки 'залипающими' вручную (или можно использовать setCheckable)"""
        style_normal = """
                    QPushButton {
                        background-color: #454545;
                        color: #d0d0d0;
                        border: 1px solid #555555;
                        border-radius: 4px;
                        padding: 6px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                    }
                """

        style_active = """
                    QPushButton {
                        background-color: #2b5c96; 
                        color: #ffffff;
                        border: 1px solid #4a90e2;
                        border-radius: 4px;
                        padding: 6px;
                    }
                """
        buttons = {
            "select": self.tool_panel.btn_select,
            "line": self.tool_panel.btn_line,
            "rect": self.tool_panel.btn_rect,
            "ellipse": self.tool_panel.btn_ellipse
        }

        for name, btn in buttons.items():
            if name == active_name:
                btn.setStyleSheet(style_active)
            else:
                btn.setStyleSheet(style_normal)

    def test_save_load(self):
        scene_data = []
        for item in self.canvas.scene.items():
            if isinstance(item, ShapeMixin) and isinstance(item, QGraphicsItem):
                if item.parentItem() is None:
                    scene_data.append(item.to_dict())

        import json
        json_str = json.dumps(scene_data, indent=2)
        print("--- JSON ---")
        print(json_str)
        print("------------")

        self.canvas.scene.clear()

        data_list = json.loads(json_str)
        for shape_data in data_list:
            item = ShapeFactory.from_dict(shape_data)
            if item:
                self.canvas.scene.addItem(item)

        print("Сцена восстановлена!")

    def save_project(self):
        filters = "Vector Project (*.json);;PNG Image (*.png);;JPEG Image (*.jpg)"
        filename, selected_filter = QFileDialog.getSaveFileName(
            self, "Save File", "", filters
        )

        if not filename:
            return

        strategy = None

        if filename.lower().endswith(".png"):
            strategy = ImageSaveStrategy("PNG", bg_color="transparent")

        elif filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            strategy = ImageSaveStrategy("JPG", bg_color="white")

        else:
            strategy = JsonSaveStrategy()

        try:
            strategy.save(filename, self.canvas.scene)

            self.statusBar().showMessage(f"Файл сохранен: {filename}", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", str(e))


    def load_project(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Vector Files (*.json *.vec)"
        )
        if not filename:
            return

        try:
            project_data = FileManager.load_from_file(filename)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось прочитать файл:\n{str(e)}")
            return

        if "shapes" not in project_data:
            QMessageBox.warning(self, "Ошибка формата", "Файл не содержит данных о фигурах")
            return

        self.canvas.scene.clear()
        self.canvas.undo_stack.clear()
        self.canvas.scene.addRect(0, 0, 800, 600, brush=QBrush(QColor("white")))

        scene_info = project_data.get("scene", {})

        shapes_list = project_data.get("shapes", [])
        error_count = 0


        for shape_dict in shapes_list:
            try:
                item = ShapeFactory.from_dict(shape_dict)
                if item:
                    self.canvas.scene.addItem(item)
            except Exception as e:
                print(f"Failed to load item: {e}")
                error_count += 1


        msg = f"Проект загружен: {filename}"
        if error_count > 0:
            msg += f" (пропущено фигур с ошибками: {error_count})"

        self.statusBar().showMessage(msg, 5000)