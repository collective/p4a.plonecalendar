

def apply_patches():
    _apply_getSubObject_patch()

def _apply_getSubObject_patch():
    """Apply a patch to AT < 1.4 so that traversal checks for data
    object first, then zope 3 view, then acquired attributes.
    """
    
    try:
        from Products.Archetypes import bbb
        # the bbb module is included with AT 1.4 and higher where we do
        # not want this monkey patch to be in effect
        return
    except ImportError, e:
        pass

    try:
        from Products.Archetypes.BaseObject import BaseObject
    except ImportError, e:
        # this basically means Archetypes isn't available
        return
    
    if hasattr(BaseObject, '__p4a_orig_getSubObject'):
        # don't patch if already patched
        return

    from zope.app.publication.browser import setDefaultSkin
    from zope.app.traversing.interfaces import ITraverser, ITraversable
    from zope.component import getMultiAdapter, ComponentLookupError
    from zope.publisher.interfaces.browser import IBrowserRequest
    from Products.Five.traversable import FakeRequest
    import Products.Five.security
    from zExceptions import NotFound

    
    BaseObject.__p4a_orig_getSubObject = BaseObject.getSubObject
    
    def getSubObject(self, name, REQUEST, RESPONSE=None):
        obj = self.__p4a_orig_getSubObject(name, REQUEST, RESPONSE)
        if obj is not None:
            return obj
        
        # The following is a copy from Five's __bobo_traverse__ stuff,
        # see Products.Five.traversable for details.
        # Basically we're forcing Archetypes to look up the correct
        # Five way:
        #   1) check for data object first
        #   2) check for zope3 view 
        #   3) return nothing so that AT's default __bobo_traverse__ will use aq
        
        if not IBrowserRequest.providedBy(REQUEST):
            # Try to get the REQUEST by acquisition
            REQUEST = getattr(self, 'REQUEST', None)
            if not IBrowserRequest.providedBy(REQUEST):
                REQUEST = FakeRequest()
                setDefaultSkin(REQUEST)

        # Con Zope 3 into using Zope 2's checkPermission
        Products.Five.security.newInteraction()

        # Use the ITraverser adapter (which in turn uses ITraversable
        # adapters) to traverse to a view.  Note that we're mixing
        # object-graph and object-publishing traversal here, but Zope
        # 2 has no way to tell us when to use which...
        # TODO Perhaps we can decide on object-graph vs.
        # object-publishing traversal depending on whether REQUEST is
        # a stub or not?
        try:
            return ITraverser(self).traverse(
                path=[name], request=REQUEST).__of__(self)
        except (ComponentLookupError, LookupError,
                AttributeError, KeyError, NotFound):
            pass
        
        return None

    BaseObject.getSubObject = getSubObject
