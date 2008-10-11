
class CreateEvent(object):
    """ Creates an Event for the given context
        and initializes it with a start/end date."""

    def create_event_by_date(self, day, id=None):
        """ Create an Event in a given context and set start
            and end date to 'day'.
        """
        type_name="Event"
        if id is None:
            id=self.context.generateUniqueId(type_name)

        # create a new Event, then set Start/End date
        new_id = self.context.invokeFactory(id=id, type_name=type_name)
        if new_id is None or new_id == '':
           new_id = id

        o=getattr(self.context, new_id, None)
        o.setStartDate(day)
        o.setEndDate(day)
        
        self.request.response.redirect('%s/%s/edit' % \
            (self.context.absolute_url(), new_id))