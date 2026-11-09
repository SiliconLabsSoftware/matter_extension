#!/usr/bin/env python3
"""
Code Size Viewer - Analyze and visualize embedded application code size.

This script provides a PyQt-based interface for analyzing code size data from CSV files,
allowing users to explore memory usage by category and component.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from csv_parser import find_csv_file, parse_csv
from html_report import generate_diff_report
from map_parser import parse_map_file


class ObjectWidget(QWidget):
    """Widget representing an object file with expandable function details."""
    
    def __init__(
        self,
        obj_name: str,
        obj_size: int,
        folder_path: Path,
        functions: Optional[List[Tuple[str, int]]] = None
    ) -> None:
        """
        Initialize object widget.
        
        Args:
            obj_name: Name of the object file.
            obj_size: Total size of the object.
            folder_path: Path to folder containing object files.
            functions: Pre-computed (function_name, size) list; objdump is used when None.
        """
        super().__init__()
        self.obj_name: str = obj_name
        self.obj_size: int = obj_size
        self.folder_path: Path = folder_path
        self.expanded: bool = False
        self.details_widget: Optional[QWidget] = None
        self.function_data: Optional[List[Tuple[str, int]]] = functions
        
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the widget UI."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Object header button
        self.header_button = QPushButton(f"{self.obj_name}: {self.obj_size:,} bytes")
        self.header_button.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #d4d4d4;
                border: 1px solid #555;
                border-left: 2px solid #555;
                padding: 8px;
                text-align: left;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #353535;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
        """)
        self.header_button.clicked.connect(self.toggle_expand)
        self.layout.addWidget(self.header_button)
    
    def toggle_expand(self) -> None:
        """Toggle expansion of function details."""
        if self.expanded:
            self.collapse()
        else:
            self.expand()
    
    def expand(self) -> None:
        """Expand to show top functions in this object."""
        if self.details_widget is not None:
            return
        
        self.expanded = True
        
        # Parse functions if not already cached
        if self.function_data is None:
            self.function_data = self.parse_object_functions()
        
        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(40, 5, 5, 5)
        details_layout.setSpacing(2)
        
        if not self.function_data:
            # No functions found
            no_func_label = QLabel("No functions found or objdump unavailable")
            no_func_label.setStyleSheet("color: #999; font-size: 13pt; font-style: italic; padding: 5px;")
            details_layout.addWidget(no_func_label)
        else:
            # Display top 10 functions
            for func_name, func_size in self.function_data[:10]:
                func_widget = QWidget()
                func_layout = QHBoxLayout(func_widget)
                func_layout.setContentsMargins(5, 2, 5, 2)
                
                name_label = QLabel(func_name)
                name_label.setStyleSheet("color: #b4b4b4; font-size: 13pt;")
                func_layout.addWidget(name_label)
                
                func_layout.addStretch()
                
                size_label = QLabel(f"{func_size:,} bytes")
                size_label.setStyleSheet("color: #2196F3; font-size: 13pt; font-weight: bold;")
                func_layout.addWidget(size_label)
                
                func_widget.setStyleSheet("""
                    QWidget {
                        background-color: #1e1e1e;
                        border-left: 2px solid #444;
                    }
                    QWidget:hover {
                        background-color: #282828;
                    }
                """)
                
                details_layout.addWidget(func_widget)
        
        self.layout.addWidget(self.details_widget)
        self.header_button.setText(f"▼ {self.obj_name}: {self.obj_size:,} bytes")
    
    def collapse(self) -> None:
        """Collapse to hide function details."""
        if self.details_widget is None:
            return
        
        self.expanded = False
        self.layout.removeWidget(self.details_widget)
        self.details_widget.deleteLater()
        self.details_widget = None
        self.header_button.setText(f"{self.obj_name}: {self.obj_size:,} bytes")
    
    def parse_object_functions(self) -> List[Tuple[str, int]]:
        """
        Parse object file to extract function sizes using objdump.
        
        Returns:
            List of (function_name, size_in_bytes) tuples sorted by size descending.
        """
        # Find the .o file
        obj_file = self.find_object_file()
        if not obj_file:
            return []
        
        try:
            # Run objdump
            result = subprocess.run(
                ['arm-none-eabi-objdump', '-d', str(obj_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            # Parse objdump output
            return self.parse_objdump_output(result.stdout)
            
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return []
    
    def find_object_file(self) -> Optional[Path]:
        """
        Find the object file matching this object name in the folder.
        
        Returns:
            Path to object file if found, None otherwise.
        """
        # Search recursively for .o file
        obj_files = list(self.folder_path.rglob(self.obj_name))
        if obj_files:
            return obj_files[0]
        
        # If exact match not found, try without extension and add .o
        if not self.obj_name.endswith('.o'):
            obj_files = list(self.folder_path.rglob(f"{self.obj_name}.o"))
            if obj_files:
                return obj_files[0]
        
        return None
    
    def parse_objdump_output(self, output: str) -> List[Tuple[str, int]]:
        """
        Parse objdump output to extract function names and sizes.
        
        Args:
            output: Output from objdump command.
            
        Returns:
            List of (function_name, instruction_count * 4) tuples sorted by size.
        """
        functions = {}
        current_function = None
        instruction_count = 0
        
        # Pattern to match function headers in .text section
        func_pattern = re.compile(r'^([0-9a-f]+)\s+<(.+?)>:')
        # Pattern to match instruction lines
        instr_pattern = re.compile(r'^\s*[0-9a-f]+:\s+[0-9a-f]+')
        
        in_text_section = False
        
        for line in output.split('\n'):
            # Check if we're entering .text section
            if '.text' in line:
                in_text_section = True
                continue
            
            # Check if we're leaving .text section
            if in_text_section and line.startswith('Disassembly of section'):
                if '.text' not in line:
                    in_text_section = False
                    continue
            
            if not in_text_section:
                continue
            
            # Check for function header
            func_match = func_pattern.match(line)
            if func_match:
                # Save previous function if exists
                if current_function and instruction_count > 0:
                    # Approximate size: instruction_count * 4 bytes (ARM instruction size)
                    functions[current_function] = instruction_count * 4
                
                # Start new function
                current_function = func_match.group(2)
                instruction_count = 0
                continue
            
            # Count instructions
            if current_function and instr_pattern.match(line):
                instruction_count += 1
        
        # Save last function
        if current_function and instruction_count > 0:
            functions[current_function] = instruction_count * 4
        
        # Convert to list and sort by size descending
        sorted_functions = sorted(functions.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_functions


class ComparisonCategoryWidget(QWidget):
    """Widget for displaying category comparison with three columns."""
    
    def __init__(
        self,
        category_name: str,
        size_a: int,
        size_b: int,
        delta: int,
        objects_a: List[Tuple[str, int]],
        objects_b: List[Tuple[str, int]],
        folder_path: Path,
        total_code_size_a: int,
        total_code_size_b: int,
        color_index: int
    ) -> None:
        """
        Initialize comparison category widget.
        
        Args:
            category_name: Name of the category.
            size_a: Total code size for first CSV.
            size_b: Total code size for second CSV.
            delta: Difference (size_a - size_b).
            objects_a: List of (object_name, size) tuples from first CSV.
            objects_b: List of (object_name, size) tuples from second CSV.
            folder_path: Path to folder containing object files.
            total_code_size_a: Total code size across all categories in first CSV.
            total_code_size_b: Total code size across all categories in second CSV.
            color_index: Index for color selection.
        """
        super().__init__()
        self.category_name: str = category_name
        self.size_a: int = size_a
        self.size_b: int = size_b
        self.delta: int = delta
        self.objects_a: List[Tuple[str, int]] = objects_a
        self.objects_b: List[Tuple[str, int]] = objects_b
        self.folder_path: Path = folder_path
        self.total_code_size_a: int = total_code_size_a
        self.total_code_size_b: int = total_code_size_b
        self.color: str = "#E57373" if color_index % 2 == 0 else "#CCCCCC"
        self.expanded: bool = False
        self.details_widget: Optional[QWidget] = None
        
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the widget UI."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Calculate percentages
        percentage_a = (self.size_a / self.total_code_size_a * 100) if self.total_code_size_a > 0 else 0
        percentage_b = (self.size_b / self.total_code_size_b * 100) if self.total_code_size_b > 0 else 0
        
        # Determine delta color
        delta_color = "#F44336" if self.delta > 0 else "#4CAF50" if self.delta < 0 else "#999"
        delta_sign = "+" if self.delta > 0 else ""
        
        # Create header widget with three columns
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)
        
        # Category name button
        obj_count_a = len(self.objects_a)
        obj_count_b = len(self.objects_b)
        self.header_button = QPushButton(f"{self.category_name} ({obj_count_a}/{obj_count_b})")
        self.header_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #3c3c3c;
                color: {self.color};
                border: 1px solid #555;
                border-left: 3px solid {self.color};
                padding: 10px;
                text-align: left;
                font-size: 15pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #4c4c4c;
            }}
            QPushButton:pressed {{
                background-color: #2c2c2c;
            }}
        """)
        self.header_button.clicked.connect(self.toggle_expand)
        self.header_button.setMinimumWidth(200)
        header_layout.addWidget(self.header_button, 2)
        
        # File A column
        label_a = QLabel(f"{self.size_a:,} bytes\\n({percentage_a:.1f}%)")
        label_a.setAlignment(Qt.AlignCenter)
        label_a.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 14pt;
                padding: 5px;
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
        """)
        header_layout.addWidget(label_a, 1)
        
        # File B column
        label_b = QLabel(f"{self.size_b:,} bytes\\n({percentage_b:.1f}%)")
        label_b.setAlignment(Qt.AlignCenter)
        label_b.setStyleSheet("""
            QLabel {
                color: #CCCCCC;
                font-size: 14pt;
                padding: 5px;
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
        """)
        header_layout.addWidget(label_b, 1)
        
        # Delta column
        label_delta = QLabel(f"{delta_sign}{self.delta:,} bytes")
        label_delta.setAlignment(Qt.AlignCenter)
        label_delta.setStyleSheet(f"""
            QLabel {{
                color: {delta_color};
                font-size: 14pt;
                font-weight: bold;
                padding: 5px;
                background-color: #2b2b2b;
                border: 1px solid #555;
            }}
        """)
        header_layout.addWidget(label_delta, 1)
        
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #3c3c3c;
            }
        """)
        
        self.layout.addWidget(header_widget)
    
    def toggle_expand(self) -> None:
        """Toggle expansion of object details."""
        if self.expanded:
            self.collapse()
        else:
            self.expand()
    
    def expand(self) -> None:
        """Expand to show object comparisons."""
        if self.details_widget is not None:
            return
        
        self.expanded = True
        obj_count_a = len(self.objects_a)
        obj_count_b = len(self.objects_b)
        self.header_button.setText(f"▼ {self.category_name} ({obj_count_a}/{obj_count_b})")
        
        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(20, 5, 5, 5)
        details_layout.setSpacing(2)
        
        # Create object dictionaries for lookup
        objects_a_dict = dict(self.objects_a)
        objects_b_dict = dict(self.objects_b)
        
        # Get all unique object names
        all_objects = set(objects_a_dict.keys()) | set(objects_b_dict.keys())
        
        # Create comparison entries
        object_comparisons = []
        for obj_name in all_objects:
            size_a = objects_a_dict.get(obj_name, 0)
            size_b = objects_b_dict.get(obj_name, 0)
            delta = size_a - size_b
            object_comparisons.append((obj_name, size_a, size_b, delta))
        
        # Sort by absolute delta (largest changes first), then take top 15
        object_comparisons.sort(key=lambda x: abs(x[3]), reverse=True)
        object_comparisons = object_comparisons[:15]
        
        for obj_name, size_a, size_b, delta in object_comparisons:
            obj_widget = QWidget()
            obj_layout = QHBoxLayout(obj_widget)
            obj_layout.setContentsMargins(5, 3, 5, 3)
            obj_layout.setSpacing(10)
            
            # Object name
            name_label = QLabel(obj_name)
            name_label.setStyleSheet("color: #d4d4d4; font-size: 13pt;")
            name_label.setMinimumWidth(200)
            obj_layout.addWidget(name_label, 2)
            
            # Size A
            size_a_label = QLabel(f"{size_a:,} bytes" if size_a > 0 else "-")
            size_a_label.setAlignment(Qt.AlignCenter)
            size_a_label.setStyleSheet("color: #b4b4b4; font-size: 13pt;")
            obj_layout.addWidget(size_a_label, 1)
            
            # Size B
            size_b_label = QLabel(f"{size_b:,} bytes" if size_b > 0 else "-")
            size_b_label.setAlignment(Qt.AlignCenter)
            size_b_label.setStyleSheet("color: #b4b4b4; font-size: 13pt;")
            obj_layout.addWidget(size_b_label, 1)
            
            # Delta
            delta_color = "#F44336" if delta > 0 else "#4CAF50" if delta < 0 else "#999"
            delta_sign = "+" if delta > 0 else ""
            delta_label = QLabel(f"{delta_sign}{delta:,} bytes")
            delta_label.setAlignment(Qt.AlignCenter)
            delta_label.setStyleSheet(f"color: {delta_color}; font-size: 13pt; font-weight: bold;")
            obj_layout.addWidget(delta_label, 1)
            
            obj_widget.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    border-left: 2px solid #555;
                }
                QWidget:hover {
                    background-color: #353535;
                }
            """)
            
            details_layout.addWidget(obj_widget)
        
        self.layout.addWidget(self.details_widget)
    
    def collapse(self) -> None:
        """Collapse to hide object details."""
        if self.details_widget is None:
            return
        
        self.expanded = False
        obj_count_a = len(self.objects_a)
        obj_count_b = len(self.objects_b)
        self.header_button.setText(f"{self.category_name} ({obj_count_a}/{obj_count_b})")
        self.layout.removeWidget(self.details_widget)
        self.details_widget.deleteLater()
        self.details_widget = None


class CategoryWidget(QWidget):
    """Widget representing a code size category with expandable details."""
    
    def __init__(
        self,
        category_name: str,
        total_size: int,
        objects: List[Tuple[str, int]],
        folder_path: Path,
        total_code_size: int,
        color_index: int,
        function_data: Optional[Dict[str, List[Tuple[str, int]]]] = None
    ) -> None:
        """
        Initialize category widget.
        
        Args:
            category_name: Name of the category.
            total_size: Total code size for this category.
            objects: List of (object_name, size) tuples.
            folder_path: Path to folder containing object files.
            total_code_size: Total code size across all categories.
            color_index: Index for color selection (used for alternating colors).
            function_data: Optional mapping of object name to (function_name, size) list.
        """
        super().__init__()
        self.category_name: str = category_name
        self.total_size: int = total_size
        self.objects: List[Tuple[str, int]] = objects
        self.folder_path: Path = folder_path
        self.function_data: Optional[Dict[str, List[Tuple[str, int]]]] = function_data
        self.total_code_size: int = total_code_size
        self.color: str = "#E57373" if color_index % 2 == 0 else "#CCCCCC"
        self.expanded: bool = False
        self.details_widget: Optional[QWidget] = None
        
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize the widget UI."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Calculate percentage
        percentage = (self.total_size / self.total_code_size * 100) if self.total_code_size > 0 else 0
        
        # Category header button
        self.header_button = QPushButton(
            f"{self.category_name}: {self.total_size:,} bytes ({percentage:.1f}%)"
        )
        self.header_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #3c3c3c;
                color: {self.color};
                border: 1px solid #555;
                border-left: 3px solid {self.color};
                padding: 10px;
                text-align: left;
                font-size: 15pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #4c4c4c;
            }}
            QPushButton:pressed {{
                background-color: #2c2c2c;
            }}
        """)
        self.header_button.clicked.connect(self.toggle_expand)
        self.layout.addWidget(self.header_button)
    
    def toggle_expand(self) -> None:
        """Toggle expansion of category details."""
        if self.expanded:
            self.collapse()
        else:
            self.expand()
    
    def expand(self) -> None:
        """Expand to show top objects in this category."""
        if self.details_widget is not None:
            return
        
        self.expanded = True
        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(20, 5, 5, 5)
        details_layout.setSpacing(2)
        
        # Sort objects by size (descending) and take top 15
        sorted_objects = sorted(self.objects, key=lambda x: x[1], reverse=True)[:15]
        
        for obj_name, obj_size in sorted_objects:
            functions = self.function_data.get(obj_name, []) if self.function_data is not None else None
            obj_widget = ObjectWidget(obj_name, obj_size, self.folder_path, functions)
            details_layout.addWidget(obj_widget)
        
        self.layout.addWidget(self.details_widget)
        percentage = (self.total_size / self.total_code_size * 100) if self.total_code_size > 0 else 0
        self.header_button.setText(f"▼ {self.category_name}: {self.total_size:,} bytes ({percentage:.1f}%)")
    
    def collapse(self) -> None:
        """Collapse to hide object details."""
        if self.details_widget is None:
            return
        
        self.expanded = False
        self.layout.removeWidget(self.details_widget)
        self.details_widget.deleteLater()
        self.details_widget = None
        percentage = (self.total_size / self.total_code_size * 100) if self.total_code_size > 0 else 0
        self.header_button.setText(f"{self.category_name}: {self.total_size:,} bytes ({percentage:.1f}%)")


class CodeSizeViewer(QMainWindow):
    """Main application window for code size analysis."""
    
    def __init__(
        self,
        folder_path: Optional[str] = None,
        second_folder_path: Optional[str] = None,
        map_mode: bool = False
    ) -> None:
        """
        Initialize the code size viewer.
        
        Args:
            folder_path: Optional path to folder containing first CSV file (or map file in map mode).
            second_folder_path: Optional path to second folder (or map file) for comparison.
            map_mode: Treat inputs as GNU ld .map files instead of CSV folders.
        """
        super().__init__()
        self.current_folder: Optional[Path] = None
        self.second_folder: Optional[Path] = None
        self.category_data: Dict[str, List[Tuple[str, int]]] = {}
        self.second_category_data: Dict[str, List[Tuple[str, int]]] = {}
        self.function_data: Optional[Dict[str, List[Tuple[str, int]]]] = None
        self.comparison_mode: bool = False
        self.map_mode: bool = map_mode
        
        self.init_ui()
        
        # Load folders if provided
        if folder_path:
            self.load_folder(Path(folder_path))
        if second_folder_path:
            self.load_second_folder(Path(second_folder_path))
    
    def init_ui(self) -> None:
        """Initialize the main window UI."""
        self.setWindowTitle("Code Size Viewer")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create toolbar
        toolbar = QToolBar()
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2b2b2b;
                border-bottom: 1px solid #555;
                spacing: 5px;
                padding: 5px;
            }
        """)
        self.addToolBar(toolbar)
        
        # Open Folder button
        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #45a049;
                padding: 8px 16px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        open_folder_btn.clicked.connect(self.open_folder_dialog)
        toolbar.addWidget(open_folder_btn)
        
        # Compare button (placeholder)
        compare_btn = QPushButton("Compare")
        compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 1px solid #1976D2;
                padding: 8px 16px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        compare_btn.clicked.connect(self.compare_placeholder)
        toolbar.addWidget(compare_btn)
        
        # Central widget with scroll area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(5)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Welcome message
        self.show_welcome_message()
        
        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)
        
        # Status bar
        self.statusBar().showMessage("Ready - Click 'Open Folder' to begin")
        self.statusBar().setStyleSheet("background-color: #2b2b2b; color: white;")
    
    def set_dark_theme(self) -> None:
        """Apply dark theme to the application."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)
    
    def show_welcome_message(self) -> None:
        """Display welcome message when no data is loaded."""
        welcome_label = QLabel("Welcome to Code Size Viewer\n\nClick 'Open Folder' to analyze a CSV file")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14pt;
                padding: 50px;
            }
        """)
        self.content_layout.addWidget(welcome_label)
        self.content_layout.addStretch()
    
    def clear_content(self) -> None:
        """Clear all content widgets."""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def select_map_file(self, title: str) -> str:
        """Open a file dialog to select a .map file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, title, "", "Map files (*.map);;All files (*)"
        )
        return file_path
    
    def open_folder_dialog(self) -> None:
        """Open folder selection dialog."""
        if self.map_mode:
            file_path = self.select_map_file("Select Map File")
            if file_path:
                self.load_folder(Path(file_path))
            return
        
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder Containing CSV File",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder_path:
            self.load_folder(Path(folder_path))
    
    def load_folder(self, folder_path: Path) -> None:
        """
        Load and analyze CSV file from the specified folder.
        
        Args:
            folder_path: Path to folder containing CSV file.
        """
        self.current_folder = folder_path
        
        try:
            if self.map_mode:
                self.category_data, self.function_data = parse_map_file(folder_path)
                source_name = folder_path.name
            else:
                csv_file = find_csv_file(folder_path)
                self.category_data = parse_csv(csv_file)
                self.function_data = None
                source_name = csv_file.name
            self.display_categories()
            self.statusBar().showMessage(f"Loaded: {source_name}")
        except FileNotFoundError as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
            self.statusBar().showMessage("Error: No input file found")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to parse input file:\n{e}"
            )
            self.statusBar().showMessage(f"Error: {e}")
    
    def load_second_folder(self, folder_path: Path) -> None:
        """
        Load second CSV file for comparison.
        
        Args:
            folder_path: Path to folder containing second CSV file.
        """
        self.second_folder = folder_path
        
        try:
            if self.map_mode:
                self.second_category_data, _ = parse_map_file(folder_path)
            else:
                self.second_category_data = parse_csv(find_csv_file(folder_path))
            self.comparison_mode = True
            self.display_categories()
            self.statusBar().showMessage(
                f"Comparing: {self.current_folder.name} vs {self.second_folder.name}"
            )
        except FileNotFoundError as e:
            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
            self.statusBar().showMessage("Error: No input file found for comparison")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to parse second input file:\n{e}"
            )
            self.statusBar().showMessage(f"Error: {e}")
    
    def display_categories(self) -> None:
        """Display parsed category data in the UI."""
        self.clear_content()
        
        if not self.category_data:
            no_data_label = QLabel("No valid data found in CSV file")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: #ff6464; font-size: 16pt; padding: 50px;")
            self.content_layout.addWidget(no_data_label)
            return
        
        if self.comparison_mode:
            self.display_comparison_view()
        else:
            self.display_single_view()
    
    def display_single_view(self) -> None:
        """Display single CSV view."""
        # Calculate total size for each category and overall total
        category_totals = []
        total_code_size = 0
        for category, objects in self.category_data.items():
            total_size = sum(size for _, size in objects)
            category_totals.append((category, total_size, objects))
            total_code_size += total_size
        
        # Add total row
        total_widget = QWidget()
        total_layout = QHBoxLayout(total_widget)
        total_layout.setContentsMargins(10, 10, 10, 10)
        
        total_label = QLabel("TOTAL CODE SIZE")
        total_label.setStyleSheet("""
            QLabel {
                color: #1768EB;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
            }
        """)
        total_layout.addWidget(total_label)
        
        total_layout.addStretch()
        
        size_label = QLabel(f"{total_code_size:,} bytes (100.0%)")
        size_label.setStyleSheet("""
            QLabel {
                color: #1768EB;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
            }
        """)
        total_layout.addWidget(size_label)
        
        total_widget.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border: 2px solid #1768EB;
                border-radius: 5px;
            }
        """)
        
        # Sort categories alphabetically
        category_totals.sort(key=lambda x: x[0])
        
        # Create category widgets
        for index, (category, total_size, objects) in enumerate(category_totals):
            category_widget = CategoryWidget(
                category, total_size, objects, self.current_folder, total_code_size, index,
                self.function_data
            )
            self.content_layout.addWidget(category_widget)
        
        self.content_layout.addStretch()
        self.content_layout.addWidget(total_widget)
    
    def display_comparison_view(self) -> None:
        """Display comparison view with three columns."""
        # Get all unique categories from both datasets
        all_categories = set(self.category_data.keys()) | set(self.second_category_data.keys())
        
        # Calculate totals
        total_code_size_a = sum(sum(size for _, size in objects) for objects in self.category_data.values())
        total_code_size_b = sum(sum(size for _, size in objects) for objects in self.second_category_data.values())
        total_delta = total_code_size_a - total_code_size_b
        
        # Calculate total object counts
        total_obj_count_a = sum(len(objects) for objects in self.category_data.values())
        total_obj_count_b = sum(len(objects) for objects in self.second_category_data.values())
        
        # Column headers: first input is always the latest, second the reference
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setSpacing(10)
        header_style = "color: #999; font-size: 13pt; font-weight: bold; padding: 5px;"
        def header_name(path: Optional[Path]) -> str:
            # Map file names are usually identical between builds, so they add no information.
            return f"\n{path.name}" if path and not self.map_mode else ""
        
        for text, stretch in (
            ("", 2),
            (f"Latest{header_name(self.current_folder)}", 1),
            (f"Reference{header_name(self.second_folder)}", 1),
            ("Delta", 1),
        ):
            header_label = QLabel(text)
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setWordWrap(True)
            header_label.setStyleSheet(header_style)
            if stretch == 2:
                header_label.setMinimumWidth(200)
            header_layout.addWidget(header_label, stretch)
        self.content_layout.addWidget(header_widget)
        
        # Add total row
        total_widget = QWidget()
        total_layout = QHBoxLayout(total_widget)
        total_layout.setContentsMargins(10, 10, 10, 10)
        total_layout.setSpacing(10)
        
        # Total label
        total_label = QLabel(f"TOTAL CODE SIZE ({total_obj_count_a}/{total_obj_count_b})")
        total_label.setStyleSheet("""
            QLabel {
                color: #1768EB;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
            }
        """)
        total_label.setMinimumWidth(200)
        total_layout.addWidget(total_label, 2)
        
        # File A total
        label_a = QLabel(f"{total_code_size_a:,} bytes\n(100.0%)")
        label_a.setAlignment(Qt.AlignCenter)
        label_a.setStyleSheet("""
            QLabel {
                color: #1768EB;
                font-size: 15pt;
                font-weight: bold;
                padding: 5px;
            }
        """)
        total_layout.addWidget(label_a, 1)
        
        # File B total
        label_b = QLabel(f"{total_code_size_b:,} bytes\n(100.0%)")
        label_b.setAlignment(Qt.AlignCenter)
        label_b.setStyleSheet("""
            QLabel {
                color: #1768EB;
                font-size: 15pt;
                font-weight: bold;
                padding: 5px;
            }
        """)
        total_layout.addWidget(label_b, 1)
        
        # Delta total
        delta_color = "#F44336" if total_delta > 0 else "#4CAF50" if total_delta < 0 else "#999"
        delta_sign = "+" if total_delta > 0 else ""
        label_delta = QLabel(f"{delta_sign}{total_delta:,} bytes")
        label_delta.setAlignment(Qt.AlignCenter)
        label_delta.setStyleSheet(f"""
            QLabel {{
                color: {delta_color};
                font-size: 15pt;
                font-weight: bold;
                padding: 5px;
            }}
        """)
        total_layout.addWidget(label_delta, 1)
        
        total_widget.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border: 2px solid #1768EB;
                border-radius: 5px;
            }
        """)
        self.content_layout.addWidget(total_widget)
        
        # Prepare category data
        category_comparisons = []
        for category in all_categories:
            objects_a = self.category_data.get(category, [])
            objects_b = self.second_category_data.get(category, [])
            size_a = sum(size for _, size in objects_a)
            size_b = sum(size for _, size in objects_b)
            delta = size_a - size_b
            category_comparisons.append((category, size_a, size_b, delta, objects_a, objects_b))
        
        # Sort categories alphabetically
        category_comparisons.sort(key=lambda x: x[0])
        
        # Create comparison widgets
        for index, (category, size_a, size_b, delta, objects_a, objects_b) in enumerate(category_comparisons):
            comparison_widget = ComparisonCategoryWidget(
                category, size_a, size_b, delta, objects_a, objects_b,
                self.current_folder, total_code_size_a, total_code_size_b, index
            )
            self.content_layout.addWidget(comparison_widget)
        
        self.content_layout.addStretch()
    
    def compare_placeholder(self) -> None:
        """Open dialog to select second folder for comparison."""
        if not self.current_folder:
            QMessageBox.warning(
                self,
                "No Base Data",
                "Please load the first CSV file before comparing."
            )
            return
        
        if self.map_mode:
            file_path = self.select_map_file("Select Second Map File for Comparison")
            if file_path:
                self.load_second_folder(Path(file_path))
            return
        
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Second Folder for Comparison",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if folder_path:
            self.load_second_folder(Path(folder_path))


def main() -> None:
    """Main entry point for the Code Size Viewer application."""
    parser = argparse.ArgumentParser(
        description="Code Size Viewer - Analyze embedded application code size from CSV files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool provides a visual interface for analyzing code size data exported from
embedded build systems. It categorizes and displays memory usage by component.

Usage:
  code_size_viewer.py                  # Open GUI and select folder manually
  code_size_viewer.py /path/to/folder  # Open GUI with pre-loaded folder
  code_size_viewer.py LATEST REFERENCE          # Compare two folders in the GUI
  code_size_viewer.py LATEST REFERENCE --html   # Write a portable HTML comparison report
  code_size_viewer.py app.map --map    # Analyze a GNU ld map file (flash usage)
  code_size_viewer.py latest.map reference.map --map [--html]  # Compare two map files

Comparison:
  The first folder/map file is always the "Latest" build and the second one is
  the "Reference" build. Delta = Latest - Reference (positive means growth).

CSV Format:
  The CSV file must contain the following columns:
    - UC Category 1: Category name for grouping
    - File Name: Name of the object/file
    - Code Size: Size in bytes
        """
    )
    
    parser.add_argument(
        "folder",
        nargs="?",
        help="Latest: folder containing the CSV file (or .map file with --map) (optional)"
    )
    
    parser.add_argument(
        "second_folder",
        nargs="?",
        help="Reference: folder containing the CSV file (or .map file with --map) to compare against (optional)"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate a static HTML comparison report instead of opening the GUI"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="code_size_diff.html",
        help="Output HTML file for --html (default: code_size_diff.html)"
    )
    
    parser.add_argument(
        "--map",
        action="store_true",
        help="Treat positional arguments as GNU ld .map files instead of CSV folders"
    )
    
    args = parser.parse_args()
    
    if args.map and not args.folder:
        parser.error("--map requires a path to a .map file")
    
    if args.html:
        if not args.folder or not args.second_folder:
            parser.error("--html requires two inputs")
        folder_a = Path(args.folder).resolve()
        folder_b = Path(args.second_folder).resolve()
        try:
            if args.map:
                data_a, _ = parse_map_file(folder_a)
                data_b, _ = parse_map_file(folder_b)
            else:
                data_a = parse_csv(find_csv_file(folder_a))
                data_b = parse_csv(find_csv_file(folder_b))
        except (FileNotFoundError, ValueError) as e:
            sys.exit(f"Error: {e}")
        name_a, name_b = ("", "") if args.map else (folder_a.name, folder_b.name)
        output = generate_diff_report(
            data_a, data_b, name_a, name_b, Path(args.output)
        )
        print(f"Report written to {output.resolve()}")
        return
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    viewer = CodeSizeViewer(args.folder, args.second_folder, args.map)
    viewer.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
