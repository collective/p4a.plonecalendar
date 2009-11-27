;-*-rst-*-

===================
 p4a.plonecalendar
===================

Overview
========

p4a.plonecalendar is a project which extends the p4a.calendar framework to
run natively within a Plone environment.  It contains the extensions that
require Plone, and the adaptions to Plone. This is mainly support for Plone
event types and iCalendar import/export.

Requirements
============
Plone 3.x. Tested with 3.2 and 3.3 but may work with other versions.

Installation
============

1. Add p4a.plonecalendar as a dependency either to your buildout:
      [buildout]
      eggs = p4a.plonecalendar
      
2. Include p4a.plonecalendar ZCML:
      [instance]
      zcml = p4a.plonecalendar

Notes
=====

Importing an iCalendar file via http
------------------------------------

Plone4Artists calendar can import an iCalendar file over http into a Plone
calendar. This is useful for example if another site presents a schedule
that you also want to present or integrate into your site.

An example url for importing an icalendar file over http is::

  http://path/to/calendar/import_from_url?url=http://url/to/icalendarfile.ics
  
This will open up a connection to the other site, get the icalendar file
called "icalendarfile.ics" and import it into the folder located at 
/path/to/calendar/


Credits
=======

  * Maintainer, Lennart Regebro - regebro (at) gmail.com
  * Rocky Burt - rocky (at) serverzen.com
  * Nate Aune - natea (at) jazkarta.com
