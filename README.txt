;-*-rst-*-

===================
 p4a.plonecalendar
===================

TODO: Add some info here about how to install with buildout and what the dependencies are (see setup.py)

Overview
========

p4a.plonecalendar is a project which extends the p4a.calendar framework to
run natively within a Plone environment.  It contains the extensions that
require Plone, and the adaptions to Plone. This is mainly support for Plone
event types and iCalendar import/export.


Installation
============

  1. When you're reading this you have probably already run 
     ``easy_install p4a.plonecalendar``. Find out how to install setuptools
     (and EasyInstall) here:
     http://peak.telecommunity.com/DevCenter/EasyInstall

  2. Create a file called ``p4a.plonecalendar-configure.zcml`` in the
     ``/path/to/instance/etc/package-includes`` directory.  The file
     should only contain this::

       <include package="p4a.plonecalendar" />


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
