import re

def resolve_pattern(pattern_oid, filters=None):
    '''
    Returns a list of patterns which correspond to all substitution combinations of `pattern_oid`.
    Substitute string are specified in `pattern_oid` between brackets and separated with comas (`{s0, s1, ...}`).
    A substitute can be prefixed with "filter:", in which case its value is retrieved from the `filters` dictionary.
    '''
    match = re.search(r'{[^{}]+}', pattern_oid)
    if not match:
        return [pattern_oid]

    if filters is None:
        filters = {}

    def get_key(sub):
        if not sub.startswith('filter:'):
            return sub
        filter_name = sub.replace('filter:', '')
        return filters.get(filter_name)

    substitutes = match.group()[1:-1].split(',')
    substitutes = [get_key(sub.replace(' ', '')) \
        for sub in substitutes]
    sub_oids = [pattern_oid.replace(match.group(), sub, 1) \
        for sub in substitutes \
        if sub is not None]
    oids = [oid \
        for sub_oid in sub_oids \
        for oid in resolve_pattern(sub_oid, filters)]
    return oids
