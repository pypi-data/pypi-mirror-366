import os
import logging
from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui import smart_logic

class FileTreeManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def on_item_expanded(self, item):
        dir_path = item.data(0, QtCore.Qt.UserRole)
        if not dir_path or not os.path.isdir(dir_path): 
            return
        if item.childCount() > 0 and item.child(0).data(0, QtCore.Qt.UserRole) is not None:
            return
        try:
            item.takeChildren()
            for name in sorted(os.listdir(dir_path)):
                abs_path = os.path.join(dir_path, name)
                try:
                    rel_path = os.path.relpath(abs_path, os.getcwd())
                except ValueError:
                    logging.warning(f"Skipping {abs_path}: not on current drive.")
                    continue
                if rel_path in self.main_window.path_to_item:
                    continue
                new_item = QtWidgets.QTreeWidgetItem(item, [name])
                new_item.setData(0, QtCore.Qt.UserRole, abs_path)
                new_item.setFlags(new_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                self.main_window.path_to_item[rel_path] = new_item
                is_excluded = smart_logic.exclude_spec.match_file(rel_path) or smart_logic.exclude_spec.match_file(rel_path + '/')
                if os.path.isdir(abs_path):
                    new_item.setIcon(0, self.main_window.folder_icon)
                    if is_excluded:
                        new_item.setCheckState(0, QtCore.Qt.Unchecked)
                    else:
                        new_item.setCheckState(0, item.checkState(0))
                else:
                    new_item.setIcon(0, self.main_window.file_icon)
                    if smart_logic.is_binary_file(abs_path):
                        is_excluded = True
                    if is_excluded:
                        new_item.setCheckState(0, QtCore.Qt.Unchecked)
                    elif self.main_window.preferences_manager.prefs_loaded and rel_path in self.main_window.preferences_manager.checked_files_from_prefs:
                        new_item.setCheckState(0, QtCore.Qt.Checked)
                    else:
                        new_item.setCheckState(0, item.checkState(0))
        except OSError as e:
            logging.error(f"Error scanning directory {dir_path}: {e}")

    def handle_item_changed(self, item, column):
        if column == 0:
            self.main_window.tree_widget.blockSignals(True)
            try:
                new_state = item.checkState(0)
                def apply_to_children(parent_item, state):
                    for i in range(parent_item.childCount()):
                        child = parent_item.child(i)
                        if child.flags() & QtCore.Qt.ItemIsUserCheckable and child.flags() & QtCore.Qt.ItemIsEnabled:
                            abs_path = child.data(0, QtCore.Qt.UserRole)
                            if state == QtCore.Qt.Checked and abs_path and os.path.isfile(abs_path) and smart_logic.is_binary_file(abs_path):
                                child.setCheckState(0, QtCore.Qt.Unchecked)
                            else:
                                child.setCheckState(0, state)
                            if os.path.isdir(abs_path):
                                apply_to_children(child, state)
                apply_to_children(item, new_state)
                parent = item.parent()
                while parent:
                    all_children_checked = True
                    all_children_unchecked = True
                    has_checkable_children = False
                    for i in range(parent.childCount()):
                        child = parent.child(i)
                        if child.flags() & QtCore.Qt.ItemIsUserCheckable and child.flags() & QtCore.Qt.ItemIsEnabled:
                            has_checkable_children = True
                            if child.checkState(0) == QtCore.Qt.Checked:
                                all_children_unchecked = False
                            elif child.checkState(0) == QtCore.Qt.Unchecked:
                                all_children_checked = False
                            else:
                                all_children_checked = False
                                all_children_unchecked = False
                    if has_checkable_children:
                        if all_children_checked:
                            parent.setCheckState(0, QtCore.Qt.Checked)
                        elif all_children_unchecked:
                            parent.setCheckState(0, QtCore.Qt.Unchecked)
                        else:
                            parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
                    else:
                        parent.setCheckState(0, QtCore.Qt.Unchecked)
                    parent = parent.parent()
            finally:
                self.main_window.tree_widget.blockSignals(False)
            if item.checkState(0) == QtCore.Qt.Checked:
                file_path = item.data(0, QtCore.Qt.UserRole)
                if file_path and os.path.isfile(file_path):
                    QtCore.QTimer.singleShot(0, lambda: self.expand_parents_of_item(item))
            self.main_window.update_token_counter()

    def expand_parents_of_item(self, item):
        parent = item.parent()
        while parent is not None:
            self.main_window.tree_widget.expandItem(parent)
            parent = parent.parent()
    
    def get_selected_files(self):
        selected = []
        iterator = QtWidgets.QTreeWidgetItemIterator(self.main_window.tree_widget)
        while iterator.value():
            item = iterator.value()
            file_path = item.data(0, QtCore.Qt.UserRole)
            if file_path and os.path.isfile(file_path) and item.checkState(0) == QtCore.Qt.Checked:
                selected.append(file_path)
            iterator += 1
        return selected

    def select_all(self):
        def check_all(item):
            abs_path = item.data(0, QtCore.Qt.UserRole)
            rel_path = os.path.relpath(abs_path, os.getcwd()) if abs_path else None
            is_excluded = False
            if rel_path:
                is_excluded = smart_logic.exclude_spec.match_file(rel_path) or smart_logic.exclude_spec.match_file(rel_path + '/')
                if os.path.isfile(abs_path) and smart_logic.is_binary_file(abs_path):
                    is_excluded = True
            if item.flags() & QtCore.Qt.ItemIsUserCheckable and item.flags() & QtCore.Qt.ItemIsEnabled and not is_excluded:
                item.setCheckState(0, QtCore.Qt.Checked)
            else:
                item.setCheckState(0, QtCore.Qt.Unchecked)
            for i in range(item.childCount()):
                if os.path.isdir(abs_path):
                    self.on_item_expanded(item)
                check_all(item.child(i))
        self.main_window.tree_widget.blockSignals(True)
        try:
            for i in range(self.main_window.tree_widget.topLevelItemCount()):
                check_all(self.main_window.tree_widget.topLevelItem(i))
        finally:
            self.main_window.tree_widget.blockSignals(False)
        self.main_window.update_token_counter()

    def deselect_all(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(self.main_window.tree_widget)
        self.main_window.tree_widget.blockSignals(True)
        try:
            while iterator.value():
                item = iterator.value()
                if item.flags() & QtCore.Qt.ItemIsUserCheckable:
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                iterator += 1
        finally:
            self.main_window.tree_widget.blockSignals(False)
        self.main_window.update_token_counter()

    def _expand_folders_for_paths(self, checked_paths):
        folders_to_expand = set()
        for checked_path in checked_paths:
            path_parts = checked_path.split(os.sep)
            current_path = ""
            for i, part in enumerate(path_parts):
                if i == 0:
                    current_path = part
                else:
                    current_path = os.path.join(current_path, part)
                if current_path in self.main_window.path_to_item and os.path.isdir(self.main_window.path_to_item[current_path].data(0, QtCore.Qt.UserRole)):
                    folders_to_expand.add(self.main_window.path_to_item[current_path])
        for item in folders_to_expand:
            self.main_window.tree_widget.expandItem(item)

    def auto_expand_common_folders(self):
        common_folders = ['src', 'lib', 'app', 'components', 'utils', 'helpers', 'models', 'views', 'controllers']
        for folder_name in common_folders:
            if folder_name in self.main_window.path_to_item:
                item = self.main_window.path_to_item[folder_name]
                self.main_window.tree_widget.expandItem(item)
