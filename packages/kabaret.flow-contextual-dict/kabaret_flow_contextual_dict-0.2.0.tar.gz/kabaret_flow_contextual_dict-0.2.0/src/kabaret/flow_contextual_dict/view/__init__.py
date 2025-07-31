import re
from kabaret.app.ui.gui.widgets.widget_view import QtCore, QtWidgets, QtGui, DockedView
from kabaret.app.ui.gui.widgets.flow import FlowView
from kabaret.app.ui.gui.widgets.flow.navigator import Navigator
from kabaret.app.ui.gui.widgets.flow.navigation_control import NavigationBar
from kabaret.app import resources

from ..objects import get_extended_contextual_dict

from . import icons


CELL_MARGIN = 4
CELL_NAME_MAX_WIDTH = 300


class ValueEditor(QtWidgets.QLineEdit):
    '''
    This custom QLineEdit invalidates its text when
    the focus is lost.

    From https://stackoverflow.com/a/49207822
    '''

    def __init__(self, text, parent):
        super(ValueEditor, self).__init__(text, parent)
        self._confirmed = False
        self.editingFinished.connect(self._on_editing_finished)

    def isConfirmed(self):
        return self._confirmed

    def focusOutEvent(self, event):
        self._confirmed = False
        return super(ValueEditor, self).focusOutEvent(event)

    def _on_editing_finished(self):
        self._confirmed = True


class ContextualDictTableDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super(ContextualDictTableDelegate, self).__init__(parent)
        self.font = QtGui.QFont()
        self.metrics = QtGui.QFontMetrics(self.font)

    def createEditor(self, parent, option, index):
        # Show the current value when edited
        return ValueEditor(str(index.data(QtCore.Qt.UserRole)[1]['value']), parent)

    def setModelData(self, editor, model, index):
        # Do not update data if the enter/return key is not used
        if not editor.isConfirmed():
            return

        super(ContextualDictTableDelegate, self).setModelData(editor, model, index)

    def paint(self, painter, option, index):
        data = index.data(QtCore.Qt.UserRole)
        key_name, key_data = data
        if index.column() == 0:
            text = key_name
        else:
            text = str(key_data['value'])
        
        old_col = painter.pen().color()
        
        if key_data['is_new']:
            new_col = QtGui.QColor(painter.pen().color())
            new_col.setHslF(new_col.hueF(), new_col.saturationF(), 0.5 * new_col.lightnessF(), new_col.alphaF())
            painter.setBrush(new_col)
            painter.setPen(new_col)
            painter.drawRect(option.rect)
            # Restore default color
            painter.setBrush(old_col)
            painter.setPen(old_col)

        text_rect = QtCore.QRect(
            option.rect.topLeft() + QtCore.QPoint(CELL_MARGIN, CELL_MARGIN),
            option.rect.bottomRight() - QtCore.QPoint(CELL_MARGIN, CELL_MARGIN)
        )
        self.font.setItalic(key_data['is_flow_key'] and key_data['value'] == key_data['default_value'])
        self.font.setBold(key_data['is_local_edit'])
        text = self.metrics.elidedText(text, QtCore.Qt.ElideRight, text_rect.width())
        painter.setFont(self.font)
        painter.drawText(text_rect, QtCore.Qt.AlignVCenter, text)

        # Restore default color
        painter.setBrush(old_col)
        painter.setPen(old_col)

    def sizeHint(self, option, index):
        # Fit cell width to content
        key_name, key_data = index.data(QtCore.Qt.UserRole)
        text = key_name if index.column() == 0 else str(key_data['value'])
        size = super(ContextualDictTableDelegate, self).sizeHint(option, index)
        size.setWidth(min(1.2 * self.metrics.horizontalAdvance(text), CELL_NAME_MAX_WIDTH))
        return size


class ContextualDictTableModel(QtCore.QAbstractTableModel):

    def __init__(self, view, parent=None):
        super(ContextualDictTableModel, self).__init__(parent)
        self.view = view
    
    def rowCount(self, parent=None):
        return self.view.context_size()

    def columnCount(self, parent=None):
        return 2
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return ['Name', 'Value'][section]
        
        return None

    def flags(self, index):
        if index.column() == 0 or not self.view.context_is_editable():
            return QtCore.Qt.NoItemFlags
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def data(self, index, role):
        if role == QtCore.Qt.UserRole or role == QtCore.Qt.EditRole:
            return self.view.get_item(index.row())

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            self.view.set_item_value(index.row(), value)
            self.dataChanged.emit(index, index, [role])
            return True


class AddItemDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super(AddItemDialog, self).__init__(parent)

        self.lineedit_name = QtWidgets.QLineEdit()
        self.lineedit_name.setMinimumWidth(200)
        self.lineedit_name.setPlaceholderText('Name')
        self.lineedit_value = QtWidgets.QLineEdit()
        self.lineedit_value.setPlaceholderText('Value')
        self.btn_confirm = QtWidgets.QPushButton('Confirm')
        self.btn_cancel = QtWidgets.QPushButton('Cancel')
        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.lineedit_name, 0, 0, 1, 2)
        glo.addWidget(self.lineedit_value, 1, 0, 1, 2)
        glo.addWidget(self.btn_confirm, 2, 0)
        glo.addWidget(self.btn_cancel, 2, 1)
        self.setLayout(glo)

        # Install event handlers
        self.btn_confirm.clicked.connect(lambda b: self.accept())
        self.btn_cancel.clicked.connect(lambda b: self.close())

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)

    def item_name(self):
        return self.lineedit_name.text()

    def item_value(self):
        return self.lineedit_value.text()

    def reset_item(self):
        self.lineedit_name.setText('')
        self.lineedit_value.setText('')


class ContextualDictTableView(QtWidgets.QTableView):

    def __init__(self, view):
        super(ContextualDictTableView, self).__init__()
        self.view = view
        self.setModel(ContextualDictTableModel(view))
        self.setItemDelegate(ContextualDictTableDelegate())
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.menu = QtWidgets.QMenu(self)
        self.dialog_add = AddItemDialog(self)

    def contextMenuEvent(self, event):
        if not self.view.context_is_editable():
            return
        
        index = self.indexAt(event.pos())
        self.menu.clear()

        a = self.menu.addAction('Add key', lambda i=index: self._on_action_add_triggered(i))
        a.setIcon(resources.get_icon(('icons.gui', 'add')))

        if index.isValid() and self.view.item_is_edit(index.row()):
            a = self.menu.addAction('Remove key', lambda i=index: self._on_action_remove_triggered(i))
            a.setIcon(resources.get_icon(('icons.gui', 'remove')))
        
        self.menu.exec_(self.viewport().mapToGlobal(event.pos()))

    def _on_action_add_triggered(self, index):
        if self.dialog_add.exec() == QtWidgets.QDialog.Accepted:
            self.view.add_item(self.dialog_add.item_name(), self.dialog_add.item_value())
            self.dialog_add.reset_item()

    def _on_action_remove_triggered(self, index):
        self.view.remove_item(index.row())


class ContextualDictView(DockedView):
    
    def _build(self, top_parent, top_layout, main_parent, header_parent, header_layout):
        self._context = None
        self._context_view_oid = None
        self._project_oid = None # updated each time the navigator oid changes

        self._navigator = Navigator(
            self.session, None, None
        )
        self.nav_bar = NavigationBar(self, self._navigator)
        self.nav_ctrl = self.nav_bar.nav_ctrl
        self.nav_oid = self.nav_bar.nav_oid

        self.checkbox_active_view = QtWidgets.QCheckBox('Active view')
        self.cbb_context_name = QtWidgets.QComboBox()
        self.cbb_context_name.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.tableview_context = ContextualDictTableView(self)

        main_lo = QtWidgets.QVBoxLayout()
        main_lo.addWidget(self.nav_bar)
        main_lo.setContentsMargins(0, 0, 0, 0)
        main_lo.setSpacing(0)

        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.checkbox_active_view, 0, 0)
        glo.addWidget(self.cbb_context_name, 0, 2)
        glo.addWidget(self.tableview_context, 1, 0, 1, 3)
        glo.setColumnStretch(1, 1)
        
        glo.setContentsMargins(2, 2, 2, 2)
        glo.setSpacing(2)
        main_lo.addLayout(glo)
        main_parent.setLayout(main_lo)

        # Options menu
        self.view_menu.setTitle('Options')
        self._reload_contexts_action = self.view_menu.addAction(
            QtGui.QIcon(resources.get_icon(('icons.gui', 'refresh'))),
            'Reload contexts',
            self.update_contexts)

        # Event handlers
        self._navigator.add_on_current_changed(self._on_navbar_updated)
        self.cbb_context_name.currentTextChanged.connect(self._on_context_text_changed)

        self.update_contexts()

    def goto(self, oid):
        self._navigator.goto(oid, False)

    def active_view_enabled(self):
        return self.checkbox_active_view.checkState() == QtCore.Qt.Checked

    def current_oid(self):
        return self._navigator.current_oid()

    def context_name(self):
        return self.cbb_context_name.currentText()

    def context_size(self):
        return len(self._context) if self._context is not None else 0

    def context_is_editable(self):
        return self._context_view_oid is not None

    def get_item(self, index):
        return self._context[index]

    def set_item_value(self, index, value):
        if re.fullmatch(r'[-+]?[0-9]+', value):
            value = int(value)
        elif re.fullmatch(r'[+-]?([0-9]*[.])?[0-9]+', value):
            value = float(value)

        self.session.cmds.Flow.call(
            self._context_view_oid+'/edits/edit_map',
            'set_edit',
            args=[self._context[index][0], value],
            kwargs={}
        )
        self.update_current_context()

    def add_item(self, name, value):
        self.session.cmds.Flow.call(
            self._context_view_oid+'/edits/edit_map',
            'set_edit',
            args=[name, value],
            kwargs={}
        )
        self.update_current_context()

    def remove_item(self, index):
        self.session.cmds.Flow.call(
            self._context_view_oid+'/edits/edit_map',
            'remove_edit',
            args=[self._context[index][0]],
            kwargs={}
        )
        self.update_current_context()

    def item_is_edit(self, index):
        return self.session.cmds.Flow.call(
            self._context_view_oid+'/edits/edit_map',
            'has_edit',
            args=[self._context[index][0]],
            kwargs={}
        )

    def update_current_context(self):
        self.tableview_context.model().beginResetModel()
        self._context = None
        self._context_view_oid = None
        object_methods = dict(self.session.cmds.Flow.call(self.current_oid(), '?', [], {}))

        if 'root' in object_methods.keys():
            root = self.session.cmds.Flow.call(self.current_oid(), 'root', [], {})

            if hasattr(root, 'get_object'):
                # use get_extended_contextual_dict() to keep the original behavior
                # it implies to get the current flow object itself
                o = root.get_object(self.current_oid())
                context_name = self.context_name()
                context_view = None
                self._context = list(reversed([(k, v)
                    for k, v in get_extended_contextual_dict(o, context_name).items()]))

                if hasattr(o, 'get_contextual_view'):
                    context_view = o.get_contextual_view(context_name)
                elif hasattr(o, context_name):
                    context_view = getattr(o, context_name)
                if context_view is not None and context_view.allow_editing():
                    self._context_view_oid = context_view.oid()

        self.tableview_context.model().endResetModel()

    def update_contexts(self):
        current_project_oid = '/'+self.current_oid().split('/', 2)[1]

        if self._project_oid == current_project_oid:
            return

        self._project_oid = current_project_oid
        context_names = []
        project_methods = dict(self.session.cmds.Flow.call(self._project_oid, "?", [], {}))

        if 'get_context_names' in project_methods:
            context_names = self.session.cmds.Flow.call(
                self._project_oid, 'get_context_names', [], {})

        self.cbb_context_name.clear()
        self.cbb_context_name.insertItems(0, context_names)

    def receive_event(self, event, data):
        if event == 'focus_changed' and self.isVisible() and self.active_view_enabled():
            view_id = data['view_id']
            if view_id == self._view_id:
                return

            view = self.session.find_view(FlowView.view_type_name(), view_id)
            if view is None or view.flow_page.current_oid() == self.current_oid():
                return

            self.goto(view.flow_page.current_oid())

    def _on_navbar_updated(self):
        self.nav_oid.update()
        self.nav_ctrl.update()
        self.update_contexts()
        self.update_current_context()

    def _on_context_text_changed(self, text):
        self.update_current_context()
