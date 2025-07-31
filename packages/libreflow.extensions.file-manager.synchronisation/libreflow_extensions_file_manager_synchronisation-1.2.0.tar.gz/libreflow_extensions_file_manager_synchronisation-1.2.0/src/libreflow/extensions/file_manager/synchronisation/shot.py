from kabaret import flow

from .file import RequestRevisions, RequestedRevisions, MultiRequestRevisions, MultiRequestedRevisions


# Shots
# ---------------------------------


class ShotElements(flow.values.MultiChoiceValue):
    
    def choices(self):
        template = self.root().project().admin.dependency_templates['shot']
        choices = []
        
        for element, data in template.get_dependencies().items():
            if data.get('requestable', True):
                choices.append(element)
            
        return choices


class DependencyOptions(flow.Object):
    
    request_dependencies = flow.SessionParam(True).ui(editor='bool')
    include_last_revisions = flow.SessionParam(False).ui(
        editor='bool',
        tooltip='Include the latest revision of each dependency')


class ShotElementSelection(flow.Object):
    
    select_all_elements = flow.SessionParam(False).ui(editor='bool').watched()
    elements = flow.Param([], ShotElements).watched()

    _shot = flow.Parent(2)
    _sequence = flow.Parent(4)
    
    def __init__(self, parent, name):
        super(ShotElementSelection, self).__init__(parent, name)
        self._kitsu_casting = None
    
    def _get_casting(self):
        bindings = self.root().project().kitsu_bindings()
        casting = bindings.get_shot_casting(
            self._shot.name(),
            self._sequence.name()
        )

        return casting
    
    def ensure_kitsu_casting(self):
        if self._kitsu_casting is None:
            self._kitsu_casting = self._get_casting()
        
        return self._kitsu_casting
    
    def child_value_changed(self, child_value):
        if child_value is self.select_all_elements:
            if self.select_all_elements.get():
                self.elements.set(self.elements.choices())
            else:
                self.elements.set([])
    
    def compute_oids(self, include_dependencies=False, latest_dependencies=False):
        elements = self.elements.get()
        template = self.root().project().admin.dependency_templates['shot']
        bindings = self.root().project().kitsu_bindings()
        deps = template.get_dependencies()
        
        kitsu_casting = self.ensure_kitsu_casting()
        oids = set()
        
        for element in self.elements.get():
            dep_data = deps[element]
            kitsu_data = dep_data.get('kitsu', None)
            
            if kitsu_data is not None and kitsu_data.get('entity', None) == 'Asset':
                # Assets
                for asset_name, asset_data in kitsu_casting.items():
                    asset_type = asset_data['type']
                    
                    if asset_type != kitsu_data['type']:
                        continue
                    
                    files_data = template.get_dependency_files(element)
                    asset_oid = bindings.get_asset_oid(asset_name)
                    
                    # Get files
                    for file_name, file_data in files_data.items():
                        rev_oids = self._get_revision_oids(asset_oid, file_name, file_data, include_dependencies, latest_dependencies)
                        # pprint(oids)
                        oids = oids.union(set(rev_oids))
            else:
                # Shots
                files_data = template.get_dependency_files(element)
                
                for file_name, file_data in files_data.items():
                    rev_oids = self._get_revision_oids(self._shot.oid(), file_name, file_data, include_dependencies, latest_dependencies)
                    oids = oids.union(set(rev_oids))
        
        return sorted(list(oids))
    
    def _get_revision_oids(self, root_oid, file_name, file_data, include_dependencies=False, latest_dependencies=False):
        # Check if given file exists
        file_oid = "%s/tasks/%s/files/%s" % (
            root_oid,
            file_data['department'],
            file_name.replace('.', '_')
        )
        
        if not self.root().session().cmds.Flow.exists(file_oid):
            self.root().session().log_warning('Unknown file with oid ' + file_oid)
            return []
        
        revision_name = file_data.get('revision', '[last]')
        revision_oids = [file_oid + '/history/revisions/' + revision_name]
        
        # Return if dependencies are not requested
        if not include_dependencies:
            return revision_oids
        
        if revision_name == '[last]':
            revision_name = None
        
        # Get dependencies
        
        file_object = self.root().get_object(file_oid)
        dependencies = get_dependencies(
            leaf=file_object,
            predictive=True,
            real=True,
            revision_name=revision_name)
        
        for d in dependencies:
            if not d['in_breakdown']:
                self.root().session().log_warning(
                    'Dependency %s not in breakdown ' % d['entity_oid']
                )
                continue
            
            revision_oid = d['revision_oid']
            
            if revision_oid is None:
                self.root().session().log_warning((
                    'Dependency %s in breakdown '
                    'but not defined in the flow' % d['entity_oid']
                ))
                continue
            
            revision_oids.append(revision_oid)
            
        # Get predictive dependencies if required
        if latest_dependencies:
            real_deps = get_dependencies(
                leaf=file_object,
                predictive=True,
                revision_name=revision_name)
            
            for d in real_deps:
                revision_oid = d['revision_oid']
                
                if revision_oid is not None and not revision_oid in revision_oids:
                    revision_oids.append(revision_oid)
        
        return revision_oids


class RequestShot(RequestRevisions):
    
    selection = flow.Child(ShotElementSelection).ui(expanded=True)
    dependency_options = flow.Child(DependencyOptions).ui(expanded=True)
    revisions = flow.Child(RequestedRevisions).ui(expanded=True)
    pattern = flow.SessionParam('').ui(
        placeholder='Revision oid pattern',
        hidden=True)
    
    _shot = flow.Parent()
    _sequence = flow.Parent(3)
    
    def get_buttons(self):
        self.message.set('<h2>Request %s%s</h2>' % (self._sequence.name(), self._shot.name()))
        self.selection.ensure_kitsu_casting()
        
        return super(RequestShot, self).get_buttons()
    
    def run(self, button):
        if button == 'Close':
            return
        elif button == 'Request':
            return super(RequestShot, self).run(button)
        
        oids = self.selection.compute_oids(
            include_dependencies=self.dependency_options.request_dependencies.get(),
            latest_dependencies=self.dependency_options.include_last_revisions.get()
        )
        self.pattern.set(';'.join(oids))
        
        return super(RequestShot, self).run(button)


class MultiRequestShot(MultiRequestRevisions):

    selection = flow.Child(ShotElementSelection).ui(expanded=True)
    dependency_options = flow.Child(DependencyOptions).ui(expanded=True)
    revisions = flow.Child(MultiRequestedRevisions).ui(expanded=True)
    pattern = flow.SessionParam('').ui(
        placeholder='Revision oid pattern',
        hidden=True)
    
    _shot = flow.Parent()
    _sequence = flow.Parent(3)
    
    def get_buttons(self):
        self.message.set('<h2>Request %s%s towards multiple sites</h2>' % (self._sequence.name(), self._shot.name()))

        return super(MultiRequestShot, self).get_buttons()
    
    def run(self, button):
        if button == 'Close':
            return
        elif button == 'Request':
            return super(MultiRequestShot, self).run(button)
        
        oids = self.selection.compute_oids(
            include_dependencies=self.dependency_options.request_dependencies.get(),
            latest_dependencies=self.dependency_options.include_last_revisions.get()
        )
        self.pattern.set(';'.join(oids))
        
        return super(MultiRequestShot, self).run(button)


# Sequences
# ---------------------------------


class SequenceElements(flow.values.MultiChoiceValue):

    CHOICES = [
        'Sets',
        'Characters',
        'Props',
        'Audios',
        'Storyboards',
        'Layout scenes'
    ]


class ShotsMultichoiceValue(flow.values.MultiChoiceValue):
    
    _sequence = flow.Parent(3)
    
    def choices(self):
        return self._sequence.shots.mapped_names()


class SequenceElementSelection(flow.Object):
    
    select_all_elements = flow.SessionParam(False).ui(editor='bool').watched()
    elements = flow.Param([], ShotElements).ui(label="Elements to request")
    select_all_shots = flow.SessionParam(False).ui(editor='bool').watched()
    shots = flow.Param([], ShotsMultichoiceValue)

    _sequence = flow.Parent(2)
    
    def revert_to_defaults(self):
        self.elements.revert_to_default()
        self.shots.revert_to_default()
    
    def compute_oids(self, include_dependencies=False, latest_dependencies=False):
        oids = []
        elements = self.elements.get()
        
        for shot_name in self.shots.get():
            shot = self._sequence.shots[shot_name]
            shot.request.selection.elements.set(elements)
            
            oids += shot.request.selection.compute_oids(include_dependencies, latest_dependencies)
        
        return oids
    
    def child_value_changed(self, child_value):
        if child_value is self.select_all_shots:
            if self.select_all_shots.get():
                self.shots.set(self.shots.choices())
            else:
                self.shots.set([])
        elif child_value is self.select_all_elements:
            if self.select_all_elements.get():
                self.elements.set(self.elements.choices())
            else:
                self.elements.set([])


class RequestSequence(RequestRevisions):

    selection = flow.Child(SequenceElementSelection).ui(expanded=True)
    dependency_options = flow.Child(DependencyOptions).ui(expanded=True)
    revisions = flow.Child(RequestedRevisions).ui(expanded=True)
    pattern = flow.SessionParam('').ui(
        placeholder='Revision oid pattern',
        hidden=True,
    )

    _sequence = flow.Parent()
    
    def get_buttons(self):
        self.message.set('<h2>Request %s</h2>' % self._sequence.name())
        self.selection.revert_to_defaults()

        return super(RequestSequence, self).get_buttons()
    
    def run(self, button):
        if button == 'Close':
            return
        elif button == 'Request':
            return super(RequestSequence, self).run(button)
        
        oids = self.selection.compute_oids(
            include_dependencies=self.dependency_options.request_dependencies.get(),
            latest_dependencies=self.dependency_options.include_last_revisions.get()
        )
        self.pattern.set(';'.join(oids))
        
        return super(RequestSequence, self).run(button)


class MultiRequestSequence(MultiRequestRevisions):

    selection = flow.Child(SequenceElementSelection).ui(expanded=True)
    dependency_options = flow.Child(DependencyOptions).ui(expanded=True)
    revisions = flow.Child(MultiRequestedRevisions).ui(expanded=True)
    pattern = flow.SessionParam('').ui(
        placeholder='Revision oid pattern',
        hidden=True)
    
    _sequence = flow.Parent()
    
    def get_buttons(self):
        self.message.set('<h2>Request %s towards multiple sites</h2>' % self._sequence.name())
        self.selection.revert_to_defaults()

        return super(MultiRequestSequence, self).get_buttons()
    
    def run(self, button):
        if button == 'Close':
            return
        elif button == 'Request':
            return super(MultiRequestSequence, self).run(button)
        
        oids = self.selection.compute_oids(
            include_dependencies=self.dependency_options.request_dependencies.get(),
            latest_dependencies=self.dependency_options.include_last_revisions.get()
        )
        self.pattern.set(';'.join(oids))
        
        return super(MultiRequestSequence, self).run(button)