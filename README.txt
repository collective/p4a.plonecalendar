p4a.plonecalendar Package Readme
=========================

Overview
--------
This package contains the extensions that require Plone, and the adaptions
to Plone. This is mainly support for Plone event types and iCalendar 
import/export.



Importing an iCalendar file via http
------------------------------------
Plone4Artists calendar can import an iCalendar file over http into a Plone
calendar. This is useful for example if another site presents a schedule
that you also want to present or integrate into your site.

Importing an icalendar file over http is done with: 

  http://path/to/calendar/import_from_url?url=http://url/to/icalendarfile.ics
  
This will open up a connection to the other site, get the icalendar file
called "icalendarfile.ics" and import it into the folder located at 
/path/to/calendar/


