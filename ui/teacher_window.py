from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLineEdit, QLabel, QMessageBox, QColorDialog,
                             QComboBox, QGroupBox, QCheckBox, QGridLayout,
                             QTabWidget, QWidget, QScrollArea, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

PERIODS_PER_DAY = 6  # Kuniga maksimal 6 dars (7-dars yo'q)


class TeacherWindow(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self.db = db_manager
        self.selected_color = "#3498DB"
        self.edit_selected_color = "#3498DB"
        self.current_teacher_id = None
        self.unavailable_buttons = {}  # (day, period) -> QPushButton

        self.setWindowTitle("👨‍🏫 O'qituvchilar boshqaruvi")
        self.setGeometry(100, 80, 1200, 750)

        self.init_ui()
        self.load_teachers()
        self.load_classes_combo()  # ← BU QATORNI QO'SHING

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        title = QLabel("👨‍🏫 O'QITUVCHILAR BOSHQARUVI")
        title.setStyleSheet("""
            font-size: 20px; font-weight: bold; color: white;
            background-color: #2C3E50; padding: 15px; border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Tablar
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #2C3E50;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ECF0F1;
                padding: 10px 20px;
                font-weight: bold;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2C3E50;
                color: white;
            }
        """)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Tab 1: Ro'yxat
        self.tabs.addTab(self._create_list_tab(), "📋 Ro'yxat")

        # Tab 2: Yangi qo'shish
        self.tabs.addTab(self._create_add_tab(), "➕ Qo'shish")

        # Tab 3: Tahrirlash
        self.tabs.addTab(self._create_edit_tab(), "✏️ Tahrirlash")

        # Tab 4: Band soatlar
        self.tabs.addTab(self._create_unavailable_tab(), "⏰ Band soatlar")

        main_layout.addWidget(self.tabs)

    def _create_list_tab(self):
        """O'qituvchilar ro'yxati"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "F.I.O", "Qisqa nom", "Telefon", "Rang",
            "Sinf rahbari", "Metodik kun", "Band soatlar"
        ])

        self.table.setColumnHidden(0, True)  # ID yashirilgan
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 70)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 120)
        self.table.setColumnWidth(7, 110)

        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; gridline-color: #ddd;
                font-size: 12px; color: #000000;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected {
                background-color: #3498DB; color: white;
            }
            QHeaderView::section {
                background-color: #2C3E50; color: white;
                padding: 8px; font-weight: bold; border: none;
            }
        """)

        self.table.itemSelectionChanged.connect(self.on_teacher_selected)
        self.table.itemDoubleClicked.connect(self.edit_teacher)
        layout.addWidget(self.table)

        # Tugmalar
        btn_layout = QHBoxLayout()

        btn_edit = QPushButton("✏️ Tahrirlash")
        btn_edit.clicked.connect(self.edit_teacher)
        btn_edit.setStyleSheet(self._btn_style("#3498DB", "#2980B9"))
        btn_layout.addWidget(btn_edit)

        btn_unavailable = QPushButton("⏰ Band soatlar")
        btn_unavailable.clicked.connect(self.show_unavailable)
        btn_unavailable.setStyleSheet(self._btn_style("#F39C12", "#E67E22"))
        btn_layout.addWidget(btn_unavailable)

        btn_assignments = QPushButton("📝 Dars biriktirish")
        btn_assignments.clicked.connect(self.open_assignments)
        btn_assignments.setStyleSheet(self._btn_style("#16A085", "#138D75"))
        btn_layout.addWidget(btn_assignments)

        btn_delete = QPushButton("🗑️ O'chirish")
        btn_delete.clicked.connect(self.delete_teacher)
        btn_delete.setStyleSheet(self._btn_style("#E74C3C", "#C0392B"))
        btn_layout.addWidget(btn_delete)

        btn_refresh = QPushButton("🔄 Yangilash")
        btn_refresh.clicked.connect(self.load_teachers)
        btn_refresh.setStyleSheet(self._btn_style("#16A085", "#138D75"))
        btn_layout.addWidget(btn_refresh)

        btn_clear_all = QPushButton("🗑️ Tozalash")
        btn_clear_all.clicked.connect(self.clear_all_teachers)
        btn_clear_all.setStyleSheet(self._btn_style("#E74C3C", "#C0392B"))
        btn_layout.addWidget(btn_clear_all)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return widget

    def _create_add_tab(self):
        """Faqat yangi qo'shish"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Ma'lumotlar
        info_group = QGroupBox("📝 Asosiy ma'lumotlar")
        info_group.setStyleSheet(self._group_style())
        info_layout = QGridLayout()
        info_group.setLayout(info_layout)

        # F.I.O
        info_layout.addWidget(QLabel("F.I.O:"), 0, 0)
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Karimov Akmal Soliyevich")
        self.input_name.setStyleSheet(self._input_style())
        info_layout.addWidget(self.input_name, 0, 1, 1, 3)

        # Qisqa nom
        info_layout.addWidget(QLabel("Qisqa nom:"), 1, 0)
        self.input_short_name = QLineEdit()
        self.input_short_name.setPlaceholderText("K.A.S. (dars jadvalida ko'rinadi)")
        self.input_short_name.setStyleSheet(self._input_style())
        info_layout.addWidget(self.input_short_name, 1, 1)

        # Telefon
        info_layout.addWidget(QLabel("Telefon:"), 1, 2)
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("+998 90 123 45 67")
        self.input_phone.setStyleSheet(self._input_style())
        info_layout.addWidget(self.input_phone, 1, 3)

        # Rang
        info_layout.addWidget(QLabel("🎨 Rang:"), 2, 0)
        color_layout = QHBoxLayout()

        self.color_preview = QLabel()
        self.color_preview.setFixedSize(50, 30)
        self.color_preview.setStyleSheet(f"""
            background-color: {self.selected_color};
            border: 2px solid #2C3E50; border-radius: 5px;
        """)
        color_layout.addWidget(self.color_preview)

        btn_color = QPushButton("Tanlash")
        btn_color.clicked.connect(self.choose_color)
        btn_color.setStyleSheet(self._btn_style("#9B59B6", "#8E44AD"))
        color_layout.addWidget(btn_color)

        info_layout.addLayout(color_layout, 2, 1, 1, 3)

        # Tez ranglar
        info_layout.addWidget(QLabel("Tez ranglar:"), 3, 0)
        colors_widget = QWidget()
        colors_layout = QHBoxLayout()
        colors_widget.setLayout(colors_layout)

        ready_colors = [
            "#E74C3C", "#2980B9", "#27AE60", "#F1C40F",
            "#8E44AD", "#E67E22", "#1ABC9C", "#E84393",
            "#0984E3", "#6C7A3D", "#C0392B", "#A29BFE",
            "#00B894", "#D35400", "#2C3E50", "#FD79A8",
        ]

        for color in ready_colors:
            btn = QPushButton()
            btn.setFixedSize(25, 25)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 1px solid #ddd; border-radius: 12px;
                }}
                QPushButton:hover {{ border: 2px solid #2C3E50; }}
            """)
            btn.clicked.connect(lambda checked, c=color: self.set_color(c))
            colors_layout.addWidget(btn)

        colors_layout.addStretch()
        info_layout.addWidget(colors_widget, 3, 1, 1, 3)

        layout.addWidget(info_group)

        # Qo'shimcha ma'lumotlar
        extra_group = QGroupBox("📋 Qo'shimcha ma'lumotlar")
        extra_group.setStyleSheet(self._group_style())
        extra_layout = QGridLayout()
        extra_group.setLayout(extra_layout)

        # Sinf rahbarligi
        extra_layout.addWidget(QLabel("Sinf rahbari:"), 0, 0)
        self.class_combo = QComboBox()
        self.class_combo.setStyleSheet(self._input_style())
        self.load_classes_combo()
        extra_layout.addWidget(self.class_combo, 0, 1)

        # Metodik kun
        extra_layout.addWidget(QLabel("Metodik kun:"), 0, 2)
        self.methodic_combo = QComboBox()
        self.methodic_combo.addItem("Yo'q", None)
        kunlar = ["Dushanba", "Seshanba", "Chorshanba",
                  "Payshanba", "Juma", "Shanba"]
        for i, kun in enumerate(kunlar):
            self.methodic_combo.addItem(kun, i)
        self.methodic_combo.setStyleSheet(self._input_style())
        extra_layout.addWidget(self.methodic_combo, 0, 3)

        layout.addWidget(extra_group)

        # Saqlash tugmalari
        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("➕ Qo'shish")
        self.btn_save.clicked.connect(self.add_teacher)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; color: white;
                padding: 15px 30px; font-size: 15px;
                border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        btn_layout.addWidget(self.btn_save)

        btn_clear = QPushButton("🗑️ Tozalash")
        btn_clear.clicked.connect(self.clear_add_form)
        btn_clear.setStyleSheet(self._btn_style("#95A5A6", "#7F8C8D"))
        btn_layout.addWidget(btn_clear)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

        return widget

    def _create_edit_tab(self):
        """Faqat tahrirlash"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Info
        self.edit_info = QLabel("⚠️ Avval Ro'yxat tabidan o'qituvchini tanlang!")
        self.edit_info.setStyleSheet("""
            font-size: 14px; font-weight: bold;
            color: white; background-color: #E67E22;
            padding: 12px; border-radius: 5px;
        """)
        layout.addWidget(self.edit_info)

        # Ma'lumotlar
        info_group = QGroupBox("📝 Asosiy ma'lumotlar")
        info_group.setStyleSheet(self._group_style())
        info_layout = QGridLayout()
        info_group.setLayout(info_layout)

        # F.I.O
        info_layout.addWidget(QLabel("F.I.O:"), 0, 0)
        self.edit_input_name = QLineEdit()
        self.edit_input_name.setPlaceholderText("Karimov Akmal Soliyevich")
        self.edit_input_name.setStyleSheet(self._input_style())
        info_layout.addWidget(self.edit_input_name, 0, 1, 1, 3)

        # Qisqa nom
        info_layout.addWidget(QLabel("Qisqa nom:"), 1, 0)
        self.edit_input_short_name = QLineEdit()
        self.edit_input_short_name.setPlaceholderText("K.A.S.")
        self.edit_input_short_name.setStyleSheet(self._input_style())
        info_layout.addWidget(self.edit_input_short_name, 1, 1)

        # Telefon
        info_layout.addWidget(QLabel("Telefon:"), 1, 2)
        self.edit_input_phone = QLineEdit()
        self.edit_input_phone.setPlaceholderText("+998 90 123 45 67")
        self.edit_input_phone.setStyleSheet(self._input_style())
        info_layout.addWidget(self.edit_input_phone, 1, 3)

        # Rang
        info_layout.addWidget(QLabel("🎨 Rang:"), 2, 0)
        color_layout = QHBoxLayout()

        self.edit_color_preview = QLabel()
        self.edit_color_preview.setFixedSize(50, 30)
        self.edit_color_preview.setStyleSheet(f"""
            background-color: {self.selected_color};
            border: 2px solid #2C3E50; border-radius: 5px;
        """)
        color_layout.addWidget(self.edit_color_preview)

        btn_color = QPushButton("Tanlash")
        btn_color.clicked.connect(self.choose_edit_color)
        btn_color.setStyleSheet(self._btn_style("#9B59B6", "#8E44AD"))
        color_layout.addWidget(btn_color)

        info_layout.addLayout(color_layout, 2, 1, 1, 3)

        # Tez ranglar
        info_layout.addWidget(QLabel("Tez ranglar:"), 3, 0)
        colors_widget = QWidget()
        colors_layout = QHBoxLayout()
        colors_widget.setLayout(colors_layout)

        ready_colors = [
            "#E74C3C", "#2980B9", "#27AE60", "#F1C40F",
            "#8E44AD", "#E67E22", "#1ABC9C", "#E84393",
            "#0984E3", "#6C7A3D", "#C0392B", "#A29BFE",
            "#00B894", "#D35400", "#2C3E50", "#FD79A8",
        ]

        for color in ready_colors:
            btn = QPushButton()
            btn.setFixedSize(25, 25)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 1px solid #ddd; border-radius: 12px;
                }}
                QPushButton:hover {{ border: 2px solid #2C3E50; }}
            """)
            btn.clicked.connect(lambda checked, c=color: self.set_edit_color(c))
            colors_layout.addWidget(btn)

        colors_layout.addStretch()
        info_layout.addWidget(colors_widget, 3, 1, 1, 3)

        layout.addWidget(info_group)

        # Qo'shimcha ma'lumotlar
        extra_group = QGroupBox("📋 Qo'shimcha ma'lumotlar")
        extra_group.setStyleSheet(self._group_style())
        extra_layout = QGridLayout()
        extra_group.setLayout(extra_layout)

        # Sinf rahbarligi
        extra_layout.addWidget(QLabel("Sinf rahbari:"), 0, 0)
        self.edit_class_combo = QComboBox()
        self.edit_class_combo.setStyleSheet(self._input_style())
        self.load_edit_classes_combo()
        extra_layout.addWidget(self.edit_class_combo, 0, 1)

        # Metodik kun
        extra_layout.addWidget(QLabel("Metodik kun:"), 0, 2)
        self.edit_methodic_combo = QComboBox()
        self.edit_methodic_combo.addItem("Yo'q", None)
        kunlar = ["Dushanba", "Seshanba", "Chorshanba",
                  "Payshanba", "Juma", "Shanba"]
        for i, kun in enumerate(kunlar):
            self.edit_methodic_combo.addItem(kun, i)
        self.edit_methodic_combo.setStyleSheet(self._input_style())
        extra_layout.addWidget(self.edit_methodic_combo, 0, 3)

        layout.addWidget(extra_group)

        # Saqlash tugmalari
        btn_layout = QHBoxLayout()

        self.btn_edit_save = QPushButton("💾 Yangilash")
        self.btn_edit_save.clicked.connect(self.update_teacher)
        self.btn_edit_save.setStyleSheet("""
            QPushButton {
                background-color: #F39C12; color: white;
                padding: 15px 30px; font-size: 15px;
                border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E67E22; }
        """)
        btn_layout.addWidget(self.btn_edit_save)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

        return widget

    def _create_unavailable_tab(self):
        """Band soatlar belgilash"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Info
        self.unavail_info = QLabel("⚠️ Avval o'qituvchini ro'yxatdan tanlang!")
        self.unavail_info.setStyleSheet("""
            font-size: 14px; font-weight: bold;
            color: white; background-color: #E67E22;
            padding: 12px; border-radius: 5px;
        """)
        layout.addWidget(self.unavail_info)

        # Tushuntirish
        legend_widget = QWidget()
        legend_widget.setStyleSheet("""
            background-color: #ECF0F1;
            border-radius: 8px;
            padding: 10px;
        """)
        legend_layout = QHBoxLayout()
        legend_widget.setLayout(legend_layout)
        
        # Legend - Bo'sh
        legend_layout.addWidget(QLabel("📌 Belgi turlari:"))
        
        legend_empty = QLabel("⬜ Bo'sh (dars mumkin)")
        legend_empty.setStyleSheet("""
            background-color: white;
            border: 2px solid #BDC3C7;
            padding: 8px 12px;
            border-radius: 5px;
            font-weight: bold;
            color: #2C3E50;
        """)
        legend_layout.addWidget(legend_empty)
        
        # Legend - Sariq
        legend_soft = QLabel("🟡 Imkon qadar yo'q")
        legend_soft.setStyleSheet("""
            background-color: #F39C12;
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            font-weight: bold;
        """)
        legend_layout.addWidget(legend_soft)
        
        # Legend - Qizil
        legend_strict = QLabel("🔴 Qat'iy yo'q")
        legend_strict.setStyleSheet("""
            background-color: #E74C3C;
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            font-weight: bold;
        """)
        legend_layout.addWidget(legend_strict)
        
        legend_layout.addStretch()
        layout.addWidget(legend_widget)

        # Instruksiya
        instructions = QLabel(
            "💡 Katakni bosing: ⬜ Bo'sh → 🟡 Sariq → 🔴 Qizil → ⬜ Bo'sh\n"
            "🔴 Qizil: Hech qachon dars qo'yilmaydi (qat'iy cheklov)\n"
            "🟡 Sariq: Iloji bo'lsa qo'yilmaydi (yumshoq cheklov)"
        )
        instructions.setStyleSheet("""
            font-size: 12px; color: #2C3E50; 
            padding: 10px; background-color: #FEF9E7;
            border-radius: 5px; border-left: 4px solid #F39C12;
        """)
        layout.addWidget(instructions)

        # Jadval (tugmalar bilan)
        grid_widget = QWidget()
        grid_widget.setStyleSheet("background-color: #ECF0F1;")
        grid_layout = QGridLayout()
        grid_layout.setSpacing(3)
        grid_widget.setLayout(grid_layout)

        # Header
        kunlar = ["Dushanba", "Seshanba", "Chorshanba",
                  "Payshanba", "Juma", "Shanba"]

        empty = QLabel("")
        empty.setStyleSheet("background-color: #2C3E50;")
        grid_layout.addWidget(empty, 0, 0)

        for col, kun in enumerate(kunlar):
            kun_label = QLabel(kun)
            kun_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            kun_label.setStyleSheet("""
                background-color: #2C3E50; color: white;
                padding: 12px; font-weight: bold; font-size: 13px;
            """)
            grid_layout.addWidget(kun_label, 0, col + 1)

        # Darslar va tugmalar
        for row in range(PERIODS_PER_DAY):
            # Dars raqami
            dars_label = QLabel(f"{row + 1}-dars")
            dars_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dars_label.setStyleSheet("""
                background-color: #34495E; color: white;
                padding: 12px; font-weight: bold; font-size: 13px;
            """)
            grid_layout.addWidget(dars_label, row + 1, 0)

            # Tugmalar
            for col in range(6):
                btn = QPushButton("")
                btn.setMinimumHeight(45)
                btn.setMinimumWidth(120)
                btn.setStyleSheet(self._get_button_style(None))  # Bo'sh
                btn.clicked.connect(
                    lambda checked, d=col, p=row: self.toggle_unavailable(d, p)
                )
                
                self.unavailable_buttons[(col, row)] = btn
                grid_layout.addWidget(btn, row + 1, col + 1)

        layout.addWidget(grid_widget)

        # Statistika
        self.stats_label = QLabel("📊 Statistika: 🔴 0 qat'iy | 🟡 0 yumshoq")
        self.stats_label.setStyleSheet("""
            font-size: 13px; font-weight: bold;
            color: white; background-color: #2C3E50;
            padding: 10px; border-radius: 5px;
        """)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)

        # Tugmalar
        btn_layout = QHBoxLayout()

        btn_all_strict = QPushButton("🔴 Hammasini qat'iy qil")
        btn_all_strict.clicked.connect(lambda: self.set_all('strict'))
        btn_all_strict.setStyleSheet(self._btn_style("#E74C3C", "#C0392B"))
        btn_layout.addWidget(btn_all_strict)
        
        btn_all_soft = QPushButton("🟡 Hammasini yumshoq qil")
        btn_all_soft.clicked.connect(lambda: self.set_all('soft'))
        btn_all_soft.setStyleSheet(self._btn_style("#F39C12", "#E67E22"))
        btn_layout.addWidget(btn_all_soft)

        btn_clear = QPushButton("⬜ Hammasini tozalash")
        btn_clear.clicked.connect(self.clear_unavailable)
        btn_clear.setStyleSheet(self._btn_style("#95A5A6", "#7F8C8D"))
        btn_layout.addWidget(btn_clear)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return widget
    
    # =========== YORDAMCHI ===========

    def _input_style(self):
        return """
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px; font-size: 13px;
                border: 2px solid #bdc3c7; border-radius: 5px;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #3498DB; }
        """

    def _btn_style(self, color, hover):
        return f"""
            QPushButton {{
                background-color: {color}; color: white;
                padding: 8px 15px; font-size: 12px;
                border-radius: 5px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
        """

    def _get_button_style(self, availability_type):
        """Tugma stilini olish (bandlik turiga qarab)"""
        if availability_type == 'strict':
            # Qat'iy - QIZIL
            return """
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border: 2px solid #C0392B;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                    border: 2px solid #A93226;
                }
            """
        elif availability_type == 'soft':
            # Yumshoq - SARIQ
            return """
                QPushButton {
                    background-color: #F39C12;
                    color: white;
                    border: 2px solid #E67E22;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E67E22;
                    border: 2px solid #D35400;
                }
            """
        else:
            # Bo'sh - OQ
            return """
                QPushButton {
                    background-color: white;
                    color: #2C3E50;
                    border: 2px solid #BDC3C7;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ECF0F1;
                    border: 2px solid #95A5A6;
                }
            """

    def _get_button_text(self, availability_type):
        """Tugma matnini olish"""
        if availability_type == 'strict':
            return "🔴"
        elif availability_type == 'soft':
            return "🟡"
        else:
            return ""

    def _group_style(self):
        return """
            QGroupBox {
                font-size: 14px; font-weight: bold;
                border: 2px solid #3498DB; border-radius: 8px;
                margin-top: 10px; padding-top: 15px;
            }
        """

    def load_classes_combo(self):
        """Sinflar ro'yxatini yuklash"""
        self.class_combo.clear()
        self.class_combo.addItem("Yo'q", None)
        classes = self.db.get_all_classes()
        for cls in classes:
            self.class_combo.addItem(cls[1], cls[0])

    # =========== RANG ===========

    def _on_tab_changed(self, index):
        """Tab o'zgarganda — Qo'shish tabiga o'tganda avtomatik rang"""
        if index == 1:  # Qo'shish tabi
            self.clear_add_form()

    def _generate_unique_color(self):
        """Mavjud o'qituvchilarga biriktirilgan ranglardan eng uzoq yangi rang"""
        import colorsys

        # Mavjud ranglarni olish
        teachers = self.db.get_all_teachers()
        existing_colors = []
        for t in teachers:
            if t[3]:
                hex_color = t[3].lstrip('#')
                try:
                    r = int(hex_color[0:2], 16) / 255.0
                    g = int(hex_color[2:4], 16) / 255.0
                    b = int(hex_color[4:6], 16) / 255.0
                    h, s, v = colorsys.rgb_to_hsv(r, g, b)
                    existing_colors.append((h, s, v))
                except (ValueError, IndexError):
                    pass

        if not existing_colors:
            return "#3498DB"

        # 16 ta Maksimal Ajraluvchi Rang — HSV makonida teng masofada
        candidates = [
            "#E74C3C", "#2980B9", "#27AE60", "#F1C40F",
            "#8E44AD", "#E67E22", "#1ABC9C", "#E84393",
            "#0984E3", "#6C7A3D", "#C0392B", "#A29BFE",
            "#00B894", "#D35400", "#2C3E50", "#FD79A8",
        ]

        best_color = candidates[0]
        best_min_dist = -1

        for candidate in candidates:
            hex_c = candidate.lstrip('#')
            try:
                r = int(hex_c[0:2], 16) / 255.0
                g = int(hex_c[2:4], 16) / 255.0
                b = int(hex_c[4:6], 16) / 255.0
                h_c, s_c, v_c = colorsys.rgb_to_hsv(r, g, b)
            except (ValueError, IndexError):
                continue

            # Eng yaqin mavjud rangga masofa
            min_dist = float('inf')
            for h_e, s_e, v_e in existing_colors:
                # HSV da rang farqi (h 0-1, s 0-1, v 0-1)
                dh = min(abs(h_c - h_e), 1 - abs(h_c - h_e))
                ds = abs(s_c - s_e)
                dv = abs(v_c - v_e)
                dist = dh * 2 + ds + dv  # Rangga ko'proq ahamiyat
                min_dist = min(min_dist, dist)

            if min_dist > best_min_dist:
                best_min_dist = min_dist
                best_color = candidate

        return best_color

    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self)
        if color.isValid():
            self.set_color(color.name())

    def set_color(self, color_hex):
        self.selected_color = color_hex
        self.color_preview.setStyleSheet(f"""
            background-color: {color_hex};
            border: 2px solid #2C3E50; border-radius: 5px;
        """)

    # =========== O'QITUVCHI AMALLAR ===========

    def add_teacher(self):
        """Faqat yangi o'qituvchi qo'shish"""
        name = self.input_name.text().strip()
        short_name = self.input_short_name.text().strip()
        phone = self.input_phone.text().strip()

        if not name:
            QMessageBox.warning(self, "Xatolik", "F.I.O kiritish shart!")
            return

        # Agar qisqa nom kiritilmagan bo'lsa, avtomatik yaratish
        if not short_name:
            parts = name.split()
            short_name = "".join(p[0] for p in parts if p)

        class_id = self.class_combo.currentData()
        methodic = self.methodic_combo.currentData()

        teacher_id = self.db.add_teacher(
            name, phone, self.selected_color, class_id, methodic, short_name
        )
        if teacher_id:
            QMessageBox.information(
                self, "Muvaffaqiyat",
                f"O'qituvchi qo'shildi!\nF.I.O: {name}\nQisqa nom: {short_name}"
            )

            # Sinf rahbari bo'lsa — Kelajak soatini avtomatik qo'shish
            if class_id:
                self._add_kelajak_soati(class_id, teacher_id)

        self.clear_add_form()
        self.load_teachers()
        self.tabs.setCurrentIndex(0)

    def update_teacher(self):
        """O'qituvchini yangilash (tahrirlash tabidan)"""
        if not self.current_teacher_id:
            QMessageBox.warning(self, "Xatolik", "O'qituvchi tanlanmagan!")
            return

        name = self.edit_input_name.text().strip()
        short_name = self.edit_input_short_name.text().strip()
        phone = self.edit_input_phone.text().strip()

        if not name:
            QMessageBox.warning(self, "Xatolik", "F.I.O kiritish shart!")
            return

        # Agar qisqa nom kiritilmagan bo'lsa, avtomatik yaratish
        if not short_name:
            parts = name.split()
            short_name = "".join(p[0] for p in parts if p)

        class_id = self.edit_class_combo.currentData()
        methodic = self.edit_methodic_combo.currentData()

        self.db.update_teacher(
            self.current_teacher_id, name, phone,
            self.edit_selected_color, class_id, methodic, short_name
        )

        QMessageBox.information(self, "Muvaffaqiyat", "Ma'lumotlar yangilandi!")

        # Sinf rahbari bo'lsa — Kelajak soatini avtomatik qo'shish
        if class_id:
            self._add_kelajak_soati(class_id, self.current_teacher_id)

        self.clear_edit_form()
        self.load_teachers()
        self.tabs.setCurrentIndex(0)

    def _add_kelajak_soati(self, class_id, teacher_id):
        """Sinf rahbariga Kelajak soatini avtomatik biriktirish (1 soat/hafta)"""
        # "Kelajak soati" fanini topish
        subjects = self.db.get_all_subjects()
        kelajak_id = None
        for s in subjects:
            if s[1].lower() == 'kelajak soati':
                kelajak_id = s[0]
                break

        if not kelajak_id:
            return  # Fan topilmadi

        # allaqachon biriktirilganligini tekshirish
        existing = self.db.get_class_assignments(class_id)
        for a in existing:
            if a[1] == 'Kelajak soati' and a[6] == teacher_id:
                return  # allaqachon bor

        # Kelajak soatini qo'shish
        self.db.add_lesson_assignment(class_id, kelajak_id, teacher_id, 1)

    def clear_add_form(self):
        """Qo'shish formani tozalash"""
        self.input_name.clear()
        self.input_short_name.clear()
        self.input_phone.clear()
        # Mavjud ranglardan eng uzoq rangni avtomatik tanlash
        new_color = self._generate_unique_color()
        self.set_color(new_color)
        self.class_combo.setCurrentIndex(0)
        self.methodic_combo.setCurrentIndex(0)

    def clear_edit_form(self):
        """Tahrirlash formani tozalash"""
        self.current_teacher_id = None
        self.edit_input_name.clear()
        self.edit_input_short_name.clear()
        self.edit_input_phone.clear()
        self.set_edit_color("#3498DB")
        self.edit_class_combo.setCurrentIndex(0)
        self.edit_methodic_combo.setCurrentIndex(0)
        self.edit_info.setText("⚠️ Avval Ro'yxat tabidan o'qituvchini tanlang!")
        self.edit_info.setStyleSheet("""
            font-size: 14px; font-weight: bold;
            color: white; background-color: #E67E22;
            padding: 12px; border-radius: 5px;
        """)

    def load_edit_classes_combo(self):
        """Tahrirlash tabi uchun sinflar ro'yxatini yuklash"""
        self.edit_class_combo.clear()
        self.edit_class_combo.addItem("Yo'q", None)
        classes = self.db.get_all_classes()
        for cls in classes:
            self.edit_class_combo.addItem(cls[1], cls[0])

    def choose_edit_color(self):
        """Tahrirlash tabi uchun rang tanlash"""
        color = QColorDialog.getColor(QColor(self.edit_selected_color), self)
        if color.isValid():
            self.set_edit_color(color.name())

    def set_edit_color(self, color_hex):
        """Tahrirlash tabi uchun rang o'rnatish"""
        self.edit_selected_color = color_hex
        self.edit_color_preview.setStyleSheet(f"""
            background-color: {color_hex};
            border: 2px solid #2C3E50; border-radius: 5px;
        """)

    def load_teachers(self):
        """O'qituvchilarni yuklash"""
        teachers = self.db.get_all_teachers()
        self.table.setRowCount(0)

        kunlar = ["Dush", "Sesh", "Chor", "Pay", "Jum", "Sha"]

        for row_num, teacher in enumerate(teachers):
            self.table.insertRow(row_num)

            # ID
            self.table.setItem(row_num, 0, QTableWidgetItem(str(teacher[0])))
            # F.I.O
            self.table.setItem(row_num, 1, QTableWidgetItem(teacher[1]))
            # Qisqa nom (short_name — indeks 6)
            short = teacher[6] if len(teacher) > 6 and teacher[6] else ""
            self.table.setItem(row_num, 2, QTableWidgetItem(short))
            # Telefon
            self.table.setItem(row_num, 3, QTableWidgetItem(teacher[2] or ""))

            # Rang
            color_item = QTableWidgetItem("")
            color_item.setBackground(QColor(teacher[3]))
            self.table.setItem(row_num, 4, color_item)

            # Sinf rahbari (class_name — indeks 8 after JOIN)
            class_name = teacher[8] if len(teacher) > 8 and teacher[8] else "—"
            class_item = QTableWidgetItem(class_name)
            if class_name != "—":
                class_item.setForeground(QColor("#27AE60"))
            self.table.setItem(row_num, 5, class_item)

            # Metodik kun
            methodic = teacher[5]
            if methodic is not None and methodic != '':
                try:
                    methodic = int(methodic)
                except (ValueError, TypeError):
                    methodic = None
            if methodic is not None and 0 <= methodic < len(kunlar):
                methodic_text = kunlar[methodic]
            else:
                methodic_text = "—"
            self.table.setItem(row_num, 6, QTableWidgetItem(methodic_text))

            # Band soatlar (qat'iy va yumshoq alohida)
            counts = self.db.get_teacher_unavailable_count(teacher[0])
            strict = counts.get('strict', 0)
            soft = counts.get('soft', 0)
            
            if strict == 0 and soft == 0:
                unavail_text = "—"
            else:
                unavail_text = f"🔴{strict} 🟡{soft}"
            
            unavail_item = QTableWidgetItem(unavail_text)
            if strict > 0:
                unavail_item.setForeground(QColor("#E74C3C"))
            elif soft > 0:
                unavail_item.setForeground(QColor("#F39C12"))
            self.table.setItem(row_num, 7, unavail_item)

    def on_teacher_selected(self):
        """O'qituvchi tanlanganda"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return

        teacher_id = int(self.table.item(current_row, 0).text())
        teacher_name = self.table.item(current_row, 1).text()

        self.current_teacher_id = teacher_id

        # Band soatlar tab info
        self.unavail_info.setText(
            f"✅ Tanlangan: {teacher_name} (ID: {teacher_id})"
        )
        self.unavail_info.setStyleSheet("""
            font-size: 14px; font-weight: bold;
            color: white; background-color: #27AE60;
            padding: 12px; border-radius: 5px;
        """)

        # Band soatlarni yuklash
        self.load_unavailable()

    def edit_teacher(self):
        """O'qituvchini tahrirlash — tahrirlash tabiga o'tkazish"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval jadvaldan o'qituvchini tanlang!")
            return

        teacher_id = int(self.table.item(current_row, 0).text())
        self.current_teacher_id = teacher_id

        teacher = self.db.get_teacher_by_id(teacher_id)
        if not teacher:
            return

        # Tahrirlash tabini to'ldirish
        self.edit_input_name.setText(teacher[1])
        short = teacher[6] if len(teacher) > 6 and teacher[6] else ""
        self.edit_input_short_name.setText(short)
        self.edit_input_phone.setText(teacher[2] or "")
        self.set_edit_color(teacher[3])

        class_id = teacher[4]
        for i in range(self.edit_class_combo.count()):
            if self.edit_class_combo.itemData(i) == class_id:
                self.edit_class_combo.setCurrentIndex(i)
                break

        methodic = teacher[5]
        for i in range(self.edit_methodic_combo.count()):
            if self.edit_methodic_combo.itemData(i) == methodic:
                self.edit_methodic_combo.setCurrentIndex(i)
                break

        # Info label yangilash
        self.edit_info.setText(f"✅ Tanlangan: {teacher[1]} (ID: {teacher_id})")
        self.edit_info.setStyleSheet("""
            font-size: 14px; font-weight: bold;
            color: white; background-color: #27AE60;
            padding: 12px; border-radius: 5px;
        """)

        # Tahrirlash tabiga o'tish (index 2)
        self.tabs.setCurrentIndex(2)

    def show_unavailable(self):
        """Band soatlar tabini ochish"""
        if not self.current_teacher_id:
            QMessageBox.warning(self, "Xatolik", "Avval o'qituvchini tanlang!")
            return
        self.tabs.setCurrentIndex(3)

    def open_assignments(self):
        """Dars biriktirish oynasini ochish"""
        from ui.assignment_window import AssignmentWindow
        win = AssignmentWindow(self.db)
        win.exec()

    def delete_teacher(self):
        """O'qituvchini o'chirish"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Xatolik", "Avval o'qituvchi tanlang!")
            return

        teacher_id = int(self.table.item(current_row, 0).text())
        teacher_name = self.table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"{teacher_name} ni o'chirmoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_teacher(teacher_id)
            QMessageBox.information(self, "Muvaffaqiyat", "O'chirildi! ✅")
            self.current_teacher_id = None
            self.load_teachers()

    def clear_all_teachers(self):
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "Barcha o'qituvchilar o'chiriladi! Davom etasizmi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_teachers()
            QMessageBox.information(self, "Muvaffaqiyat", "Barcha o'qituvchilar o'chirildi! ✅")
            self.current_teacher_id = None
            self.load_teachers()

    # =========== BAND SOATLAR ===========

    def load_unavailable(self):
        """Band soatlarni yuklash"""
        if not self.current_teacher_id:
            return

        # Avval barcha tugmalarni tozalash
        for btn in self.unavailable_buttons.values():
            btn.setStyleSheet(self._get_button_style(None))
            btn.setText("")

        # Band soatlarni belgilash
        unavail = self.db.get_teacher_unavailable(self.current_teacher_id)
        for day, period, avail_type in unavail:
            if (day, period) in self.unavailable_buttons:
                btn = self.unavailable_buttons[(day, period)]
                btn.setStyleSheet(self._get_button_style(avail_type))
                btn.setText(self._get_button_text(avail_type))

        # Metodik kunni avtomatik "qat'iy band" qilib belgilash
        teacher = self.db.get_teacher_by_id(self.current_teacher_id)
        if teacher:
            methodic_day = teacher[5]  # methodic_day indeksi
            if methodic_day is not None and 0 <= methodic_day < 6:
                kunlar = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]
                for period in range(PERIODS_PER_DAY):
                    if (methodic_day, period) in self.unavailable_buttons:
                        btn = self.unavailable_buttons[(methodic_day, period)]
                        btn.setStyleSheet(self._get_button_style("strict"))
                        btn.setText(self._get_button_text("strict"))

        # Statistikani yangilash
        self.update_stats()

    def toggle_unavailable(self, day, period):
        """Band soatni o'zgartirish (3 holat: bo'sh → sariq → qizil → bo'sh)"""
        if not self.current_teacher_id:
            QMessageBox.warning(self, "Xatolik", "Avval o'qituvchini tanlang!")
            return

        # Hozirgi holatni olish
        current_unavail = self.db.get_teacher_unavailable(self.current_teacher_id)
        current_type = None
        for d, p, t in current_unavail:
            if d == day and p == period:
                current_type = t
                break

        # Keyingi holatni aniqlash
        if current_type is None:
            # Bo'sh → Sariq
            new_type = 'soft'
        elif current_type == 'soft':
            # Sariq → Qizil
            new_type = 'strict'
        else:
            # Qizil → Bo'sh
            new_type = None

        # Bazaga yozish
        self.db.set_teacher_unavailable(
            self.current_teacher_id, day, period, new_type
        )

        # Tugma ko'rinishini yangilash
        btn = self.unavailable_buttons[(day, period)]
        btn.setStyleSheet(self._get_button_style(new_type))
        btn.setText(self._get_button_text(new_type))
        
        # Statistikani yangilash
        self.update_stats()

    def clear_unavailable(self):
        """Barcha band soatlarni tozalash"""
        if not self.current_teacher_id:
            QMessageBox.warning(self, "Xatolik", "Avval o'qituvchini tanlang!")
            return

        reply = QMessageBox.question(
            self, "Tasdiqlash",
            "Barcha band soatlarni tozalashni xohlaysizmi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_teacher_unavailable(self.current_teacher_id)
            self.load_unavailable()
            QMessageBox.information(self, "Muvaffaqiyat", "Tozalandi! ✅")

    def update_stats(self):
        """Statistikani yangilash"""
        if not self.current_teacher_id:
            self.stats_label.setText("📊 Statistika: 🔴 0 qat'iy | 🟡 0 yumshoq")
            return
        
        counts = self.db.get_teacher_unavailable_count(self.current_teacher_id)
        strict = counts.get('strict', 0)
        soft = counts.get('soft', 0)
        total = strict + soft
        
        self.stats_label.setText(
            f"📊 Statistika: 🔴 {strict} qat'iy | 🟡 {soft} yumshoq | "
            f"Jami: {total} ta band soat"
        )

    def set_all(self, availability_type):
        """Barcha kataklarni belgilash"""
        if not self.current_teacher_id:
            QMessageBox.warning(self, "Xatolik", "Avval o'qituvchini tanlang!")
            return
        
        type_text = "qat'iy (qizil)" if availability_type == 'strict' else "yumshoq (sariq)"
        
        reply = QMessageBox.question(
            self, "Tasdiqlash",
            f"Barcha kataklarni {type_text} qilib belgilamoqchimisiz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for day in range(6):
                for period in range(PERIODS_PER_DAY):
                    self.db.set_teacher_unavailable(
                        self.current_teacher_id, day, period, availability_type
                    )
            self.load_unavailable()            