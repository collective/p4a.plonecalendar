===================
 p4a.plonecalendar
===================

Overview
========

p4a.plonecalendar provides nice calendaring views for Plone, specifically
a Month, Week and Day view, and also nice lists of past and previous 
events.

There are today better calendaring views for Plone, specifcally solgema.fullcalendar.
However, that's a JavaScript calendar, so if you need a calendar that you can use
without JavaScript, for example for accessibility reasons, then p4a.plonecalendar
is a good choice.

Upgrading from version 2.0
==========================

p4a.plonecalendar 2.1 removes the dependency on p4a.subtyper. As a result
upgrading to p4a.plonecalendar can be a bit of work.

Step 1:
-------

Firstly you need to add p4a.subtyper to your buildout.cfg.

Under [instance] add "4a.subtyper" to the eggs property, remove
p4a.plonecalendars zcml entries and replace them with p4a.subtypers zcml
entries. The result should look something like this:

    [instance]
    ...
    
    eggs = 
        Plone
        p4a.plonecalendar
        p4a.subtyper
        ${buildout:eggs}

    zcml = 
        p4a.subtyper
        p4a.subtyper-meta

Run buildout and restart the server.

Step 2:
-------

Go to the ZMI and open the Upgrades tab of portal_setup: 
   http://yourplonesite/portal_setup/manage_upgrades
   
Choose the p4a.plonecalendar:default profile, and the upgrade named
"Upgrade to 2.1: Remove all marker interfaces" should be visible.
Select it and press "Upgrade."

Step 3:
-------

Then go to the quickinstaller: 
   http://yourplonesite/portal_quickinstaller/manage_installProductsForm
   
Here, reinstall P4A Plone Calendar. You will after this have to go to all
calendars and select a Calendar View as default view again.

Step 4 (optional):
------------------

If you have no other parts of Plone4Artists installed you can also uninstall
Plone4Artists Subtyper, and remove it from the buildout.cfg.


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
