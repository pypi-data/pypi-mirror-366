import re
import fnmatch
from kabaret import flow
from libreflow.baseflow.site import SiteSelection
from libreflow.baseflow.file import Revision

from .sync_utils import resolve_pattern


class ActiveSiteChoiceValue(flow.values.SessionValue):
    
    DEFAULT_EDITOR = 'choice'
    
    _choices = flow.SessionParam(None).ui(editor='set')

    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            names = working_sites.get_site_names(use_custom_order=True, active_only=True)
            self._choices.set(names)
        
        return self._choices.get()

    def revert_to_default(self):
        choices = self.choices()
        current_site = self.root().project().get_current_site_name()
        if current_site in choices:
            self.set(current_site)


class ActiveSitesMultichoiceValue(ActiveSiteChoiceValue):
    
    DEFAULT_EDITOR = 'multichoice'
    
    exclude_choice = flow.SessionParam()
    
    def choices(self):
        if self._choices.get() is None:
            working_sites = self.root().project().get_working_sites()
            names = working_sites.get_site_names(use_custom_order=True, active_only=True)
            self._choices.set(names)
        
        choices = self._choices.get().copy()
        exclude_choice = self.exclude_choice.get()
        
        if exclude_choice is not None:
            try:
                choices.remove(exclude_choice)
            except ValueError:
                pass
        
        return choices


class ActiveSiteAutoSelectChoiceValue(ActiveSiteChoiceValue):
    
    def choices(self):
        choices = super(ActiveSiteAutoSelectChoiceValue, self).choices()
        choices = ['Auto select'] + choices.copy()
        
        return choices


class SiteMultiSelection(flow.Object):
    
    source_site = flow.Param(None, ActiveSiteAutoSelectChoiceValue).ui(label='From', icon=('icons.libreflow', 'upload')).watched()
    target_sites = flow.Param([], ActiveSitesMultichoiceValue).ui(label='To', icon=('icons.libreflow', 'download'))
    
    def child_value_changed(self, child_value):
        if child_value is self.source_site:
            source_site = self.source_site.get()
            self.target_sites.exclude_choice.set(source_site)
            self.target_sites.touch()


# File revisions
# ---------------------------------


class RequestedRevisions(flow.DynamicMap):
    
    STYLE_BY_STATUS = {
        'Available': ('#45cc3d', ('icons.libreflow', 'blank')),
        'Requested': ('#b9c2c8', ('icons.libreflow', 'exclamation-sign-colored')),
        'NotAvailable': ('#cc3b3c', ('icons.libreflow', 'blank')),
        'Undefined': ('#cc3b3c', ('icons.libreflow', 'unavailable')),
    }
    
    request_action = flow.Parent()
    oids = flow.SessionParam([]).ui(editor='set')
    
    def mapped_names(self, page_num=0, page_size=None):
        return self.oids.get()
    
    def get_mapped(self, name):
        if not self.has_mapped_name(name):
            raise MappedNameError(self.oid(), name)

        try:
            obj = self._mng.get_object(name)
        except ValueError:
            raise

        return obj
    
    def columns(self):
        return ['Revision']

    def update(self, pattern):
        self.oids.set(self.request_action.get_oids(pattern))
    
    def _fill_row_cells(self, row, item):
        row['Revision'] = item.oid()
    
    def _fill_row_style(self, style, item, row):
        status = 'Undefined'
        
        if hasattr(item, 'request_as'):
            status = item.get_sync_status(site_name=self.request_action.sites.target_site.get())
            
        style['Revision_foreground-color'] = self.STYLE_BY_STATUS[status][0]
        style['Revision_icon'] = self.STYLE_BY_STATUS[status][1]


class RequestRevisions(flow.Action):
    
    ICON = ('icons.gui', 'share-option')

    pattern = flow.Param("").ui(
        placeholder="Revision oid pattern"
    )
    sites = flow.Child(SiteSelection).ui(expanded=True)
    revisions = flow.Child(RequestedRevisions).ui(expanded=True)
    
    def allow_context(self, context):
        current_site = self.root().project().get_current_site()
        return (
            context
            and context.endswith('.details')
            and current_site.request_files_from_anywhere.get()
        )

    def needs_dialog(self):
        self.message.set('<h1>Request files</h1>')
        return True
    
    def get_oids(self, pattern_str):
        oids = []
        patterns = []
        
        for pattern in pattern_str.split(';'):
            patterns += resolve_pattern(pattern)
        
        for pattern in patterns:
            oids += self.glob(self.root().project().oid(), pattern, 0)
        
        return oids

    def get_buttons(self):
        self.sites.source_site.set(self.root().project().get_current_site().name())
        target_site_choices = self.sites.target_site.choices()
        
        if not target_site_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Close']
        
        self.sites.target_site.set(target_site_choices[0])

        return ["Send requests", "Refresh list", "Close"]
    
    def ls(self, root_oid):
        related_info, mapped_names = self.root().session().cmds.Flow.ls(root_oid)
        relation_oids = [rel_info[0] for rel_info in related_info]
        mapped_oids = ["%s/%s" % (root_oid, name) for name in mapped_names]
        
        return relation_oids + mapped_oids
    
    def get_last_publication(self, file_oid):
        o = self.root().get_object(file_oid)
        
        try:
            head = o.get_head_revision()
        except AttributeError:
            return None
        
        if not head:
            return None
        
        return head.name()
    
    def glob(self, root_oid, pattern, level):
        if level >= pattern.count("/") - 1:
            return [root_oid]

        matches = []
        level_pattern = "/".join(pattern.split("/")[:level + 3])

        if level_pattern.endswith("[last]"):
            file_oid = self.root().session().cmds.Flow.resolve_path(root_oid + "/../..")
            head_name = self.get_last_publication(file_oid)

            if not head_name:
                return []
            
            pattern = pattern.replace("[last]", head_name)
            level_pattern = level_pattern.replace("[last]", head_name)
        
        for oid in self.ls(root_oid):
            if fnmatch.fnmatch(oid, level_pattern):
                matches += self.glob(oid, pattern, level + 1)
        
        return matches

    def send_requests(self, target_sites, source_site=None):
        auto_select_enabled = (source_site == "Auto select")
        for rev in self.revisions.mapped_items():
            # Skip objects which are not file revisions
            if not isinstance(rev, Revision):
                continue

            if auto_select_enabled:
                source_site = rev.site.get()

            # Skip revisions not available on selected source site
            if rev.get_sync_status(site_name=source_site) != 'Available':
                continue
            
            for target_site in target_sites:
                # Skip revisions already available on selected target site
                if rev.get_sync_status(site_name=target_site) == 'Available':
                    continue

                rev.request_as.sites.source_site.set(source_site)
                rev.request_as.sites.target_site.set(target_site)
                rev.request_as.sites.auto_select_enabled.set(auto_select_enabled)
                rev.request_as.run(None)
    
    def run(self, button):
        if button == "Close":
            return
        elif button == "Refresh list":
            self.revisions.update(self.pattern.get())
            self.revisions.touch()
            return self.get_result(close=False)
        
        source_site = self.sites.source_site.get()
        target_site = self.sites.target_site.get()
        self.send_requests([target_site], source_site)
        self.revisions.touch()
        return self.get_result(close=False)


class MultiRequestedRevisions(RequestedRevisions):
    
    STYLE_BY_STATUS = {
        'Available': ('#45cc3d', ('icons.libreflow', 'checked-symbol-colored')),
        'Requested': ('#b9c2c8', ('icons.libreflow', 'exclamation-sign-colored')),
        'NotAvailable': ('#cc3b3c', ('icons.libreflow', 'blank')),
        'Undefined': ('#cc3b3c', ('icons.libreflow', 'unavailable')),
    }
    
    request_action = flow.Parent()
    source_sites = flow.SessionParam(list).ui(hidden=True)
    
    def columns(self):
        site_names = self.request_action.sites.target_sites.get() + self.source_sites.get()
        site_names += [self.root().project().get_exchange_site().name()]
        site_names = list(dict.fromkeys(site_names))

        return ['Revision'] + site_names
    
    def _fill_row_cells(self, row, item):
        row['Revision'] = item.oid()
        
        for col in self.columns()[1:]:
            row[col] = ''
    
    def _fill_row_style(self, style, item, row):
        style['Revision_icon'] = ('icons.libreflow', 'blank')
        
        if not hasattr(item, 'request_as'):
            style['Revision_icon'] = self.STYLE_BY_STATUS['Undefined'][1]
            return
        
        site_names = self.request_action.sites.target_sites.get() + self.source_sites.get()
        exchange_name = self.root().project().get_exchange_site().name()
        site_names = list(dict.fromkeys(site_names))

        for site_name in site_names:
            status = item.get_sync_status(site_name=site_name)
            style[site_name + '_icon'] = self.STYLE_BY_STATUS[status][1]
        
        status = item.get_sync_status(exchange=True)
        style[exchange_name+'_icon'] = self.STYLE_BY_STATUS[status][1]


class MultiRequestRevisions(RequestRevisions):
    
    ICON = ('icons.libreflow', 'multi-share-option')
    
    sites = flow.Child(SiteMultiSelection).ui(expanded=True)
    revisions = flow.Child(MultiRequestedRevisions).ui(expanded=True)
    
    def get_buttons(self):
        self.sites.source_site.set(self.sites.source_site.choices()[0])
        target_sites_choices = self.sites.target_sites.choices()
        
        if not target_sites_choices:
            msg = self.message.get()
            if msg is None:
                msg = ''
            
            msg += (
                '<h3><font color="#D5000D">Making requests is not possible since '
                'there is no other site defined for this project.</font></h3>'
            )
            self.message.set(msg)
            
            return ['Close']

        return ['Send requests', 'Refresh list', 'Close']
    
    def run(self, button):
        if button == 'Close':
            return
        elif button == 'Refresh list':
            self.revisions.update(self.pattern.get())
            source_sites = []
            for oid in [r.oid() for r in self.revisions.mapped_items()]:
                try:
                    site_name = self.root().session().cmds.Flow.get_value(oid + '/site')
                except flow.exceptions.MissingRelationError:
                    # Skip if not a file revision
                    continue
                source_sites.append(site_name)
            self.revisions.source_sites.set(source_sites)
            self.revisions.touch()
            return self.get_result(close=False)
        
        target_sites = self.sites.target_sites.get()
        source_site = self.sites.source_site.get()
        self.send_requests(target_sites, source_site)
        self.revisions.touch()
        return self.get_result(close=False)