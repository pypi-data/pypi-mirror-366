# class Remapping
# composition  would involve composing terminals
# which are somehow the last thing in matching functions.

# this /might/ be done faster using parsing like Lark

def classes():
    # just to create a copy of the following.
    # too lazy to convert them to be able to be instantiated.
    class Termination:
        """ 'pre'-processing """
        terminals = {
            int, float,
            str,
            bool,
            type(None), # weird
            # does json have datetime?
            }
        terminals = tuple(terminals)
        @classmethod
        def visit(cls, p, k, v):
            return True

        @classmethod
        def map(cls, d):
            from boltons.iterutils import remap
            return remap(d, visit=cls.visit)


    class Identification:
        types = (int, str)

        from dataclasses import dataclass
        @dataclass(frozen=True)
        class ID:
            value: int | str # usually. types above
            def __str__(self) -> str:
                return str(self.value)
        class anonID(ID): ...
        
        terminals = {Termination.terminals}|{ID, anonID}
        terminals = tuple(terminals)

        subject_keys = ('id',)
        deanon = False
        # cant do 
        # subject_key = subject_keys[0] 
        # @classproperty 'deprecated'
        # def subject_key
        object_keys = {'refid', 'idref' }

        class list:
            key =   '__rdftype__'
            value = '__rdfseq__'
        
        @classmethod
        def maybeanon(cls, id):
            if cls.deanon:
                return cls.ID(id)
            else:
                assert(cls.deanon is False)
                return cls.anonID(id)
            
        @classmethod
        def enter(cls, p, k, v):
            subject_key = cls.subject_keys[0]
            def dicthasid(v):
                for id in cls.subject_keys:
                    if id in v:
                        yield id

            if type(v) is dict:
                dids = dicthasid(v)
                dids = tuple(dids)
                return (
                    #        wrap in ID
                    {sk: cls.ID(v[sk]) for sk in dids}
                    or {subject_key: cls.maybeanon(id(v))},
                    #       ..the rest of the data
                    ((k,v) for k,v in  v.items() if k not in dids ) )
            elif type(v) is list:
                # id(lst) is not deterministic. don't think it's a 'problem'
                return ({
                        subject_key: cls.maybeanon(id(v)),
                        cls.list.key: cls.list.value
                        },
                        enumerate(v))
            else:
                assert(isinstance(v, cls.terminals))
                return k, False
        
        @classmethod
        def visit(cls, p, k, v):
            # interpret object identifier cases
            # no anon. it's there.
            if k in cls.object_keys:
                if isinstance(v, cls.types):
                    return k, cls.ID(v)
            if p: # example connectedIds: [id1,id2,id3]
                if any(k in cls.object_keys for k in p):
                    if isinstance(v, cls.types):
                        return k, cls.ID(v)
            return True

        @classmethod
        def map(cls, d):
            from boltons.iterutils import remap
            return remap(d, enter=cls.enter, visit=cls.visit)
    

    class Tripling:
        """
        (identified) data -> triples
        """
        from dataclasses import dataclass
        @dataclass(frozen=True)
        class Triple:
            subject: 's'
            predicate: 'p'
            object: 'o'

            def __str__(self) -> str:
                return f"{self.subject} {self.predicate} {self.object}"
            
        class list(list):  #ordered set? TODO

            def __str__(self) -> str:
                _ = '\n'.join([str(i) for i in self])
                return _
        _exclude_keys = {}
        
        @classmethod
        def enter(cls, p, k, v):
            if isinstance(v, dict):
                assert(any(sk in v for sk in Identification.subject_keys))
                def _(v, subject_key):
                    for ik, iv in v.items():
                        if isinstance(iv, dict):
                            for sk in Identification.subject_keys:
                                if sk in iv:
                                    yield from (
                                        cls.Triple(v[subject_key] , ik, iv[sk] ),
                                        iv, )
                        else:
                            assert(isinstance(iv, Identification.terminals ))
                            if not ((ik in Identification.subject_keys) and (type(iv) is Identification.anonID)):
                                if ik not in cls._exclude_keys:
                                    yield cls.Triple(v[subject_key], ik, iv)
                def __(v):
                    for sk in Identification.subject_keys:
                        if sk in v: yield from _(v, sk)
                return cls.list(), enumerate(__(v))
            else:
                assert(isinstance(v, cls.Triple))
                # no nesting. no need to 'enter'
                return None, False
        
        @classmethod
        def visit(cls, p, k, v):
            if isinstance(v, cls.Triple):
                if v.predicate in Identification.subject_keys:
                    if isinstance(v.object, Identification.ID):
                        return k, cls.Triple(v.subject, v.predicate, v.object.value)
            return True

        
        @classmethod
        def map(cls, d, flatten=True):
            from boltons.iterutils import remap
            _ = remap(d, enter=cls.enter, visit=cls.visit)
            if not flatten:
                return _
            else:
                _ = cls.flatten(_, seqtypes=(cls.list))
                _ = frozenset(_)
                _ = cls.list(_)
                return _
        
        @classmethod
        def flatten(cls, items, seqtypes=(list, tuple)):
            def flatten(items, seqtypes=seqtypes):
                #https://stackoverflow.com/questions/10823877/what-is-the-fastest-way-to-flatten-arbitrarily-nested-lists-in-python
                try:
                    for i, x in enumerate(items):
                        while isinstance(x, seqtypes):
                            items[i:i+1] = x
                            x = items[i]
                except IndexError:
                    pass
                return items
            return flatten(items, seqtypes=seqtypes)


    class RDFing:

        class Triple(Tripling.Triple):
            def __str__(self) -> str:
                if isinstance(self.subject, Tripling.Triple):
                    #                     but take out the dot
                    s = f"<<{str(self.subject)[:-1]}>>"
                else:
                    s = str(self.subject)
                if isinstance(self.object, Tripling.Triple):
                    o = f"<<{str(self.object)[:-1]}>>"
                else:
                    o = str(self.object)
                return f"{s} {self.predicate} {o}."
        class list(Tripling.list):
            id_prefix =                 'id'
            id_uri =                    f"urn:example:{id_prefix}:"
            key_prefix =                'prefix'
            key_uri =                   f"urn:example:{key_prefix}:"

            def __str__(self) -> str:
                _ =     f'prefix rdf:                   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> \n'
                _ = _ + f'prefix {self.id_prefix}:      <{self.id_uri}>     \n'
                _ = _ + f'prefix {self.key_prefix}:     <{self.key_uri}>    \n\n'
                _ = _ + super().__str__()
                return _
        
        from urllib.parse import quote as urlquote
        @classmethod
        def uq(cls, s):
            #the characters '_.-~' are never quoted. bc some new rfc
            # https://datatracker.ietf.org/doc/html/rfc3986.html
            # but ~ bad for ttl.
            # and period cant be in the end.
            #period (%2E) or tilde (%7E)
            if s:
                ll = s[-1]
                if ll == '.': 
                    ll = f'%2E' # cant end with dot
                    s = s[:-1]+ll
                if '~' in s: # always a problem
                    s = s.replace('~', '%7E')
            return cls.urlquote(s, safe='') # default safe='/' which is *NOT* safe
        @classmethod
        def triple(cls, s, p, o):
            m = {True: 'true', False:'false', None: '\"null\"'} # not rdf:nil which is specific to a rdf:List
            from types import NoneType
            # SUBJECT
            assert(isinstance(s, Identification.ID))
            if type(s) is Identification.ID:
                s = str(s)
                s = cls.uq(s)
                s = f'{cls.list.id_prefix}:{s}'
            else:
                assert(type(s) is Identification.anonID)
                s = str(s)
                s = cls.uq(s)
                s = f'_:{s}'
            # special list/seq handling
            if p == Identification.list.key and o == Identification.list.value:
                return cls.Triple(s, "rdf:type", "rdf:Seq")

            # PREDICATE
            # just need to take care of int predicates
            if isinstance(p, int):
                p = f'rdf:_{p}'
            else:
                assert(isinstance(p, str))
                p = cls.uq(p)
                p = f'{cls.list.key_prefix}:{p}'
            
            # OBJECT
            #      need to escape quotes
            if isinstance(o, str):
                # dont want to encode('unicode_escape').decode()
                # to not lose unicode chars
                # escape all the backslashes, first..
                o = o.replace("\\", "\\\\")
                # /then/ ...
                # escape spacing things
                o = o.replace('\n', '\\n')
                o = o.replace('\r', '\\r')
                o = o.replace('\f', '\\f')
                o = o.replace('\t', '\\t')
                # inner quotes
                o = o.replace('"', '\\"')
                # outer quote
                o = '"'+o+'"'
            elif isinstance(o, (bool, NoneType)): # https://github.com/w3c/json-ld-syntax/issues/258
                o = m[o]
            elif isinstance(o, Identification.ID):
                if type(o) is Identification.ID:
                    o = str(o)
                    o = cls.uq(o)
                    o = f'{cls.list.id_prefix}:{o}'
                else:
                    assert(type(o) is Identification.anonID)
                    o = str(o)
                    o = cls.uq(o)
                    o = f'_:{o}'
            else:
                o = str(o)
            return cls.Triple(s,p,o)

        @classmethod
        def visit(cls, v):
            assert(isinstance(v, Tripling.Triple))
            s = v.subject
            p = v.predicate
            o = v.object
            return cls.triple(s,p,o)

        @classmethod
        def map(cls, d, ):
            _ = map(cls.visit, d)
            _ = cls.list(_)
            return _

    _ = locals()
    from inspect import isclass
    for n,c in _.items(): assert(isclass(c))
    from types import SimpleNamespace as NS
    return NS(**_)

defaults = classes()
def json2rdf(
        data: str | dict,
        *,
        sort =              True, # (attempt to) make conversion deterministic
        # id interpretation
        subject_id_keys =   defaults.Identification.subject_keys,
        deanon:bool =       defaults.Identification.deanon,
        object_id_keys =    defaults.Identification.object_keys,
        # # uri construction
        id_prefix =         (defaults.RDFing.list.id_prefix,
                             defaults.RDFing.list.id_uri),
        key_prefix =        (defaults.RDFing.list.key_prefix,
                             defaults.RDFing.list.key_uri),
        ):
    """
    sort: the triples
    subject_keys: set of keys to create a uri out of in for the *subject*.
        the first key will be used to create a predicate if one does not exist.
        example: {"id": 1, "key":"abc" } ->
            prefix:1 prefix:key "abc".
            prefix:1 prefix:id prefix:1.
        example: case when no id key in data or no id key is set: {"key: "abc"} ->
            prefix:generated prefix:key "abc".
            prefix:generated prefix:id prefix:generated.
    object_keys: set of keys to interpret as a uri out of as an *object*.
        example: {"id": 1, "refid": 2,} ->
            prefix:1 prefix:refid prefix:2.
    deanon: can be set to True to use id_prefix when no id key is present.
        otherwise, a blank/anon node will be used.
    """
    f = classes()
    if not subject_id_keys:  # hack for the case when no identifier is desired from the input
        import uuid          # todo: ya right.
        subject_id_keys = {str(uuid.uuid4())} # impossible key in data
        f.Tripling._exclude_keys = subject_id_keys
    f.Identification.deanon = deanon
    f.Identification.subject_keys = [k for k in subject_id_keys if k in frozenset(subject_id_keys)]
    f.Identification.object_keys = frozenset(object_id_keys)

    f.RDFing.list.id_prefix,      f.RDFing.list.id_uri =    id_prefix
    f.RDFing.list.key_prefix,     f.RDFing.list.key_uri =   key_prefix

    d = data
    def triples(data):
        _ = data
        _ = f.Termination.map(_)
        _ = f.Identification.map(_)
        _ = f.Tripling.map(_)
        return _
    if isinstance(d, str):
        from json import loads
        d = loads(d)

    d = triples(d)
    if sort:
        d = sorted(d, key=str)
        d = f.RDFing.map(d)
    d = str(d)
    return d

j2r = json2rdf

if __name__ == '__main__':
    from .cli import _
