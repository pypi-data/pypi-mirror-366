from __future__ import annotations

import numbers
import typing
from collections.abc import Sequence

from qt_material_icons import MaterialIcon
from qtpy import QtCore, QtGui, QtWidgets

from .resizegrip import ResizeGrip
from .widgets import FloatParameter, IntParameter, ParameterWidget


class StyledItemDelegate(QtWidgets.QStyledItemDelegate):
    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QtCore.QAbstractItemModel,
        index: QtCore.QModelIndex,
    ) -> None:
        indexes = self.selected_indexes(index)
        model.blockSignals(True)
        for index in indexes:
            if index == indexes[-1]:
                model.blockSignals(False)
            super().setModelData(editor, model, index)

    def selected_indexes(self, current_index: QtCore.QModelIndex | None):
        indexes = []
        if (parent := self.parent()) and isinstance(parent, QtWidgets.QTreeView):
            indexes = parent.selectedIndexes()
        if current_index is not None and current_index not in indexes:
            indexes.append(current_index)
        return indexes

    def set_edit_data(
        self,
        value: typing.Any,
        model: QtCore.QAbstractItemModel,
        index: QtCore.QModelIndex,
    ) -> None:
        indexes = self.selected_indexes(index)
        model.blockSignals(True)
        for index in indexes:
            if index == indexes[-1]:
                model.blockSignals(False)
            model.setData(index, value, QtCore.Qt.ItemDataRole.EditRole)


class IntegerDelegate(StyledItemDelegate):
    def displayText(self, value: typing.Any, locale: QtCore.QLocale) -> str:
        return str(value)

    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> QtWidgets.QWidget:
        editor = IntParameter(parent=parent)
        editor.set_slider_visible(False)
        editor.set_commit_on_edit(True)
        editor.line.setFrame(False)
        return editor

    def setEditorData(
        self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex
    ) -> None:
        value = index.model().data(index, QtCore.Qt.ItemDataRole.EditRole)
        if value and isinstance(editor, IntParameter):
            editor.set_value(value)

    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QtCore.QAbstractItemModel,
        index: QtCore.QModelIndex,
    ) -> None:
        if isinstance(editor, IntParameter):
            value = editor.value()
            self.set_edit_data(value, model, index)

    def updateEditorGeometry(
        self,
        editor: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        editor.setGeometry(option.rect)


class FloatDelegate(StyledItemDelegate):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.decimals = None

    def displayText(self, value: typing.Any, locale: QtCore.QLocale) -> str:
        if self.decimals is not None:
            return f'{value:.{self.decimals}f}'.rstrip('0').rstrip('.')
        else:
            return f'{value}'.rstrip('0').rstrip('.')

    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> QtWidgets.QWidget:
        editor = FloatParameter(parent=parent)
        editor.set_slider_visible(False)
        editor.set_decimals(6)
        editor.set_commit_on_edit(True)
        editor.line.setFrame(False)
        return editor

    def setEditorData(
        self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex
    ) -> None:
        value = index.model().data(index, QtCore.Qt.ItemDataRole.EditRole)
        if value and isinstance(editor, FloatParameter):
            editor.set_value(value)

    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QtCore.QAbstractItemModel,
        index: QtCore.QModelIndex,
    ) -> None:
        if isinstance(editor, FloatParameter):
            value = editor.value()
            self.set_edit_data(value, model, index)

    def updateEditorGeometry(
        self,
        editor: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ) -> None:
        editor.setGeometry(option.rect)


class DataTableModel(QtGui.QStandardItemModel):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.types = []

    def setData(
        self,
        index: QtCore.QModelIndex,
        value: typing.Any,
        role: int = QtCore.Qt.ItemDataRole.EditRole,
    ) -> bool:
        if role == QtCore.Qt.ItemDataRole.EditRole:
            column = index.column()
            typ = self.types[column] if column < len(self.types) else None
            if typ is not None:
                try:
                    value = typ(value)
                except (ValueError, TypeError):
                    value = None
        return super().setData(index, value, role)


class DataTableView(QtWidgets.QTableView):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self) -> None:
        mode = QtWidgets.QAbstractItemView.SelectionMode.ContiguousSelection
        self.setSelectionMode(mode)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setSortingEnabled(True)

        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setStretchLastSection(True)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )

        # Context menu
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.context_menu = QtWidgets.QMenu(self)

        action = QtGui.QAction("Edit", self)
        action.triggered.connect(self.edit_selected)
        self.addAction(action)
        self.context_menu.addAction(action)

        action = QtGui.QAction("Copy", self)
        action.setShortcut(QtGui.QKeySequence.StandardKey.Copy)
        action.setShortcutContext(QtCore.Qt.ShortcutContext.WidgetShortcut)
        action.triggered.connect(self.copy_selected)
        self.addAction(action)
        self.context_menu.addAction(action)

        action = QtGui.QAction("Paste", self)
        action.setShortcut(QtGui.QKeySequence.StandardKey.Paste)
        action.setShortcutContext(QtCore.Qt.ShortcutContext.WidgetShortcut)
        action.triggered.connect(self.paste_selected)
        self.addAction(action)
        self.context_menu.addAction(action)

    def copy_selected(self) -> None:
        selected_indexes = self.selectedIndexes()
        if not self.model():
            return

        # Create a nested list from the data
        data = []
        row_data = []
        row = 0
        for index in selected_indexes:
            if row != index.row() and row_data:
                data.append(row_data)
                row_data = []
            row = index.row()
            row_data.append(self.model().data(index))
        if row_data:
            data.append(row_data)

        # Copy to clipboard
        text = '\n'.join('\t'.join(str(d) for d in row_data) for row_data in data)
        clipboard = QtGui.QClipboard()
        clipboard.setText(text)

    def edit_selected(self) -> None:
        index = self.currentIndex()
        if index.isValid():
            self.edit(index)

    def paste_selected(self) -> None:
        selected_indexes = self.selectedIndexes()
        current_index = self.currentIndex()
        if not current_index and not selected_indexes or not self.model():
            return

        # Get top left index
        for index in selected_indexes:
            if (
                index.row() <= current_index.row()
                and index.column() <= current_index.column()
            ):
                current_index = index

        # Get data
        text = QtGui.QClipboard().text()
        data = (row_text.split('\t') for row_text in text.split('\n'))

        # Set data
        for row, row_data in enumerate(data):
            row_index = current_index.siblingAtRow(current_index.row() + row)
            if not row_index.isValid():
                continue
            for column, d in enumerate(row_data):
                index = row_index.siblingAtColumn(current_index.column() + column)
                if not index.isValid():
                    continue
                self.model().setData(index, d)

    def show_menu(self, position: QtCore.QPoint) -> None:
        self.context_menu.exec_(self.viewport().mapToGlobal(position))


class TabDataParameter(ParameterWidget):
    """Parameter to display tabular data in a QTreeWidget."""

    value_changed: QtCore.Signal = QtCore.Signal(tuple)

    _value: tuple = ()
    _default: tuple = ()
    _headers: tuple[str, ...] = ()
    _types: tuple[type, ...] = ()
    _start_index: int = 0
    _decimals: int = 3

    def __init__(
        self, name: str | None = None, parent: QtWidgets.QWidget | None = None
    ) -> None:
        self._delegates = []
        super().__init__(name, parent)

    def _init_ui(self) -> None:
        QtWidgets.QWidget().setLayout(self.layout())
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        # TableView
        self.model = DataTableModel(parent=self)
        self.model.itemChanged.connect(self._item_change)
        self.view = DataTableView(parent=self)
        self.view.setModel(self.model)
        self.view.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.layout().addWidget(self.view)

        # Toolbar
        self.toolbar = QtWidgets.QToolBar()
        size = self.toolbar.style().pixelMetric(
            QtWidgets.QStyle.PixelMetric.PM_SmallIconSize
        )
        self.toolbar.setIconSize(QtCore.QSize(size, size))
        self.layout().addWidget(self.toolbar)

        icon = MaterialIcon('add')
        action = QtGui.QAction(icon, 'Add Row', self)
        action.triggered.connect(self.add_row)
        self.toolbar.addAction(action)

        icon = MaterialIcon('remove')
        action = QtGui.QAction(icon, 'Remove Row', self)
        action.triggered.connect(self.remove_row)
        self.toolbar.addAction(action)

        icon = MaterialIcon('delete')
        action = QtGui.QAction(icon, 'Clear', self)
        action.triggered.connect(self.clear)
        self.toolbar.addAction(action)

        self.resize_grip = ResizeGrip(self.view)
        self.resize_grip.can_resize_horizontal = True

    def clear(self) -> None:
        self.model.clear()
        super().set_value(())
        self._refresh_horizontal_headers()

    def decimals(self) -> int:
        return self._decimals

    def set_decimals(self, decimals: int) -> None:
        self._decimals = decimals
        for delegate in self._delegates:
            if isinstance(delegate, FloatDelegate):
                delegate.decimals = decimals

    def headers(self) -> tuple[str, ...]:
        return self._headers

    def set_headers(self, headers: Sequence[str]) -> None:
        if not isinstance(headers, tuple):
            headers = tuple(headers)
        self._headers = headers
        self._refresh_horizontal_headers()

    def types(self) -> tuple[type, ...]:
        return self._types

    def set_types(self, types: Sequence[type]) -> None:
        if not isinstance(types, tuple):
            types = tuple(types)
        self._types = types

        self._delegates = []
        # Fill up types to column count
        if not types:
            types = [None] * (self.model.columnCount() - len(types))
        self.model.types = types

        for i, type_ in enumerate(types):
            if issubclass(type_, float):
                delegate = FloatDelegate(self.view)
                delegate.decimals = self._decimals
            elif issubclass(type_, int):
                delegate = IntegerDelegate(self.view)
            else:
                delegate = StyledItemDelegate(self.view)
            self.view.setItemDelegateForColumn(i, delegate)
            self._delegates.append(delegate)

    def start_index(self) -> int:
        return self._start_index

    def set_start_index(self, start_index: int) -> None:
        self._start_index = start_index
        self._refresh_vertical_headers()

    def value(self) -> tuple:
        return super().value()

    def set_value(self, value: Sequence) -> None:
        self.model.clear()
        if not value:
            return

        for row, row_data in enumerate(value):
            items = []
            if isinstance(row_data, dict):
                row_data = row_data.values()
            for column, cell_data in enumerate(row_data):
                item = QtGui.QStandardItem()
                item.setData(cell_data, QtCore.Qt.ItemDataRole.EditRole)
                items.append(item)
            if items:
                self.model.appendRow(items)

        super().set_value(self._tab_data_value())
        self._refresh_horizontal_headers()
        self._refresh_vertical_headers()

    def add_row(self) -> None:
        """Add a row."""

        items = []
        for i in range(self.model.columnCount()):
            item = QtGui.QStandardItem()
            if i < len(self._types):
                type_ = self._types[i]
                if issubclass(type_, numbers.Number):
                    item.setData(0, QtCore.Qt.ItemDataRole.EditRole)
                elif issubclass(type_, str):
                    item.setData('', QtCore.Qt.ItemDataRole.EditRole)
            items.append(item)
        self.model.insertRow(self.model.rowCount(), items)
        self._item_change()
        self._refresh_vertical_headers()

    def remove_row(self) -> None:
        """Remove a row."""

        self.model.takeRow(self.model.rowCount() - 1)
        self._item_change()

    def _item_change(self) -> None:
        super().set_value(self._tab_data_value())

    def _tab_data_value(self) -> tuple:
        """Return the data as nested tuples."""

        values = []
        for row in range(self.model.rowCount()):
            row_values = []
            for column in range(self.model.columnCount()):
                index = self.model.index(row, column)
                column_value = self.model.data(index, QtCore.Qt.ItemDataRole.EditRole)
                row_values.append(column_value)
            values.append(tuple(row_values))
        return tuple(values)

    def _refresh_horizontal_headers(self) -> None:
        """Refresh the horizontal header labels."""

        if self._headers:
            labels = self._headers
        else:
            labels = tuple(str(i) for i in range(self.model.columnCount()))
        self.model.setHorizontalHeaderLabels(labels)

        # Resize columns
        header = self.view.horizontalHeader()
        for i in range(header.count()):
            size = max(self.view.sizeHintForColumn(i), header.sectionSizeHint(i))
            self.view.setColumnWidth(i, size)

    def _refresh_vertical_headers(self) -> None:
        """Refresh the vertical header labels."""

        start = self._start_index
        end = self.model.rowCount() + self._start_index
        labels = tuple(str(i) for i in range(start, end))
        self.model.setVerticalHeaderLabels(labels)
