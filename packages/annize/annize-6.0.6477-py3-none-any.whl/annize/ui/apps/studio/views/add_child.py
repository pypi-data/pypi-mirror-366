# SPDX-FileCopyrightText: © 2025 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
import klovve

import annize.i18n
import annize.ui.apps.studio.models.add_child


class AddChild(klovve.ui.ComposedView[annize.ui.apps.studio.models.add_child.AddChild]):

    def compose(self):
        return klovve.views.VerticalBox(
            items=[
                klovve.views.Label(
                    text=annize.i18n.tr("an_UI_chooseElementTypeToAdd"),
                    vertical_layout=klovve.ui.Layout(klovve.ui.Align.START)),
                klovve.views.Scrollable(
                    body=klovve.views.VerticalBox(items=self.bind.type_buttons),
                    vertical_layout=klovve.ui.Layout(min_size_em=10))])

    _SIMPLE_VALUE_TEXT = annize.i18n.tr("an_UI_simpleValue")

    def _(self):
        if not self.model:
            return ()
        return [klovve.views.Button(
            text=f"{AddChild._SIMPLE_VALUE_TEXT if object_type_feature is None else object_type_feature}\n"
                 f"{object_type_name}",
            style=klovve.views.Button.Style.FLAT,
            horizontal_layout=klovve.ui.Layout(klovve.ui.Align.FILL),
            action_name=str(i))
            for i, (object_type_feature, object_type_name, object_type) in enumerate(self.model.object_types)]
    type_buttons: list[klovve.views.Button] = klovve.ui.computed_list_property(_)


class AddChildDialog(klovve.ui.dialog.Dialog):

    def __init__(self, annize_application, object_types: list[tuple[str|None, str, type]], **kwargs):
        super().__init__(**kwargs)
        self.__annize_application = annize_application
        self.__object_types = tuple(object_types)

    def view(self):
        return AddChild(model=annize.ui.apps.studio.models.add_child.AddChild(
            annize_application=self.__annize_application,
            object_types=self.__object_types))

    @klovve.event.event_handler
    def __handle_action_triggered(self, event: klovve.app.Application.ActionTriggeredEvent):
        event.stop_processing()
        self.close(self.__object_types[int(event.action_name)])
