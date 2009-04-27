from p4a.plonecalendar import sitesetup

def install(portal):
    sitesetup.setup_portal(portal)

def uninstall(portal):
    #import pdb;pdb.set_trace()
    sitesetup.unsetup_portal(portal)
