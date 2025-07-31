

import sys

from ...session import KabaretSession

from qtpy import QtCore, QtWidgets
from .widgets.main_window import MainWindowManager
from .widgets.flow.flow_view import FlowView
from .widgets.flow import FlowViewPlugin

class KabaretStandaloneGUISession(KabaretSession):

    def __init__(self,
        session_name='Standalone', tick_every_ms=10, debug=False,
        layout_mgr=False, layout_autosave=False, layout_savepath=None
    ):
        super(KabaretStandaloneGUISession, self).__init__(session_name, debug)
        self.main_window_manager = None
        self.tick_every_ms = tick_every_ms
        self._current_view = None

        # Layout management
        self.layout_manager = layout_mgr
        self.layout_autosave = layout_autosave
        self.layout_savepath = layout_savepath
        
        self.layout_load = False
        self.layout_sessionpath = None

        if self.layout_manager:
            self.log_info("Enabling Layout Manager")
        
        if self.layout_autosave:
            self.log_info("Enabling Layout Autosave")

    def is_gui(self):
        return True

    def register_plugins(self, plugin_manager):
        super(KabaretStandaloneGUISession, self).register_plugins(plugin_manager)
        plugin_manager.register(FlowViewPlugin, 'kabaret.flow_view')

    def create_window_manager(self):
        return MainWindowManager.create_window(self)
        
    def start(self):
        app = QtWidgets.QApplication(sys.argv)
        app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus, False)
        QtWidgets.QApplication.setOrganizationName("Supamonks")
        QtWidgets.QApplication.setApplicationName("Kabaret")
        self.main_window_manager = self.create_window_manager()
        self.main_window_manager.install()

        self.main_window_manager.main_window.setFocusPolicy(QtCore.Qt.StrongFocus)
        QtWidgets.QApplication.instance().focusChanged.connect(self.watch_focus)

        timer = QtCore.QTimer(self.main_window_manager.main_window)
        timer.timeout.connect(self.tick)
        timer.start(self.tick_every_ms)

        app.exec_()

    def watch_focus(self, old, new):
        current_view = None
        if not new:
            return

        view_type_name = FlowView.view_type_name()
        for _, view in self._views.items():
            if view.view_type_name() != view_type_name:
                continue
            children = view.findChildren(type(new), new.objectName())
            parent = view.parent()
            if (
                (new is view)
                or (children and new in children)
                or (new is parent)
            ):
                current_view = view
                break

        if not current_view:
            return

        try:
            self._current_view = current_view
            if self._current_view:
                self.dispatch_event("focus_changed", view_id=self._current_view._view_id)

        except RuntimeError:
            # Internal C++ object already deleted :/
            self._current_view = None

    def current_view(self):
        if not self._current_view:
            return self.find_view(FlowView.view_type_name())
        return self._current_view
    
    def register_view_types(self):
        '''
        Subclasses can register view types and create defaults view here.
        Use:
            type_name = self.register_view_type(MyViewType)
        to register a view type.
        
        And optionally:
            self.add_view(type_name)
        to create a default view.
        '''
        super(KabaretStandaloneGUISession, self).register_view_types()

    def _get_layout_state(self):
        return self.main_window_manager.get_layout_state()

    def _set_layout_state(self, state):
        self.main_window_manager.set_layout_state(state)
    
    def _get_geometry_state(self):
        return self.main_window_manager.get_geometry_state()
    
    def _set_geometry_state(self, state):
        self.main_window_manager.set_geometry_state(state)

    def _on_cluster_connected(self):
        '''
        Overridden to also dispatch a 'cluster_connection' event to GUI.
        '''
        super(KabaretStandaloneGUISession, self)._on_cluster_connected()
        self.dispatch_event(
            'cluster_connection',
            cluter_name=self._cluster_actor.get_cluster_name()
        )

    # def dispatch_event(self, event_type, **data):
    #     if self.main_window_manager is not None:
    #         self.main_window_manager.receive_event(event_type, data)
    #     super(KabaretStandaloneGUISession, self).dispatch_event(event_type, **data)
