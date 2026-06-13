"""
UI компоненты для Discord
"""

from presentation.views.base import BaseView
from presentation.views.role_button import RoleButton
from presentation.views.role_panel_view import RolePanelView
from presentation.views.role_panel_paginated_view import RolePanelPaginatedView
from presentation.views.confirm_view import ConfirmView
from presentation.views.close_button_view import CloseButtonView

__all__ = [
    'BaseView',
    'RoleButton',
    'RolePanelView',
    'RolePanelPaginatedView',
    'ConfirmView',
    'CloseButtonView',
]