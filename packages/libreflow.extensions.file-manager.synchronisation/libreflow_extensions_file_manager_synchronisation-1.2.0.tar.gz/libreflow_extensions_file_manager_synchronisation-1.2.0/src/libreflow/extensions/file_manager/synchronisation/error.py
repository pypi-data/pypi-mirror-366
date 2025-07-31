from kabaret import flow


class SyncErrorCounter(flow.DynamicMap):

    _error_count = flow.Param(list)

    def refresh_error_count(self):
        count = []
        sites = self.root().project().get_working_sites()
        site_names = sites.get_site_names(use_custom_order=True, active_only=True)

        for name in site_names:
            s = sites[name]
            count.append((s.name(), s.oid(), len(s.get_jobs(status='ERROR'))))
        
        self._error_count.set(count)
    
    def columns(self):
        return ['Site', 'Nb errors']

    def rows(self):
        count = self._error_count.get()
        rows = []

        for site_name, site_oid, nb_err in count:
            style = {'icon': ('icons.libreflow', 'blank')}
            oid = site_oid + '/queue'
            
            if nb_err > 0:
                style['foreground-color'] = '#D5000D'
                style['Nb errors_foreground-color'] = '#D5000D'
            
            rows.append((oid,
                {
                    'Site': site_name,
                    'Nb errors': nb_err,
                    'activate_oid': oid,
                    '_style': style
                }
            ))
        
        return rows


class ShowSiteSyncErrors(flow.Action):

    error_counter = flow.Child(SyncErrorCounter).ui(
        label='Errors',
        expanded=True)
    
    def allow_context(self, context):
        return context and context.endswith('.inline')

    def get_buttons(self):
        self.message.set('<h2>Synchronization errors</h2>')
        return ['Refresh', 'Close']
    
    def run(self, button):
        if button == 'Close':
            return
        
        self.error_counter.refresh_error_count()
        self.error_counter.touch()
        return self.get_result(close=False)