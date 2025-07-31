import uuid
from kabaret import flow
from kabaret.flow_entities.entities import EntityCollection, Entity, Property, PropertyValue


class RemoveRequestRule(flow.Action):
    ICON = ('icons.gui', 'remove-symbol')
    _rule = flow.Parent()
    _rules = flow.Parent(2)
    _settings = flow.Parent(3)

    def needs_dialog(self):
        return False

    def run(self, button):
        settings = self._settings
        rules = self._rules
        rules.delete_entities([self._rule.name()])
        rules.touch()


class SiteNames(flow.values.SessionValue):
    DEFAULT_EDITOR = 'multichoice'
    STRICT_CHOICES = True

    def choices(self):
        sites = self.root().project().get_working_sites()
        return sites.get_site_names(active_only=True)

class EditTargetSites(flow.Action):
    ICON = ('icons.libreflow', 'edit-blank')
    sites = flow.SessionParam(list, value_type=SiteNames)
    _value = flow.Parent()
    _rule = flow.Parent(2)

    def needs_dialog(self):
        self.sites.set(self._value.get())
        return True

    def get_buttons(self):
        return ['Edit', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return

        self._value.set(self.sites.get())
        self._rule.touch()

class TargetSites(PropertyValue):
    edit = flow.Child(EditTargetSites)

class RequestRule(Entity):
    description = Property()
    pattern = Property()
    sites = Property(TargetSites).ui(editable=False)
    enabled = Property().ui(editor='bool')
    remove = flow.Child(RemoveRequestRule)

class AddRequestRule(flow.Action):
    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')
    description = flow.SessionParam('')
    pattern = flow.SessionParam('')
    sites = flow.SessionParam(list, value_type=SiteNames)
    _rules = flow.Parent()

    def needs_dialog(self):
        self.sites.revert_to_default()
        return True

    def get_buttons(self):
        return ['Add', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return

        _id = f"r{uuid.uuid4().hex}"
        self._rules.ensure_exist([_id])
        self._rules.touch()
        rule = self._rules[_id]
        rule.description.set(self.description.get())
        rule.pattern.set(self.pattern.get())
        rule.sites.set(self.sites.get())
        rule.enabled.set(True)
        self._rules.touch()

class RequestRules(EntityCollection):
    add_rule = flow.Child(AddRequestRule)

    @classmethod
    def mapped_type(cls):
        return RequestRule

    def columns(self):
        return ['Description', 'Pattern', 'Target sites']

    def _fill_row_cells(self, row, item):
        row['Description'] = item.description.get()
        row['Pattern'] = item.pattern.get()
        row['Target sites'] = item.sites.get()

    def _fill_row_style(self, style, item, row):
        icon = ('icons.gui', 'check')
        if not item.enabled.get():
            icon = ('icons.gui', 'check-box-empty')
        style['icon'] = icon
        style['Target sites_activate_oid'] = item.sites.edit.oid()
