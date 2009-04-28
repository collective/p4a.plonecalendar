from p4a.plonecalendar import sitesetup

def install(portal):
    sitesetup.setup_portal(portal)

def uninstall(portal, reinstall=False):
    sitesetup.unsetup_portal(portal, reinstall=reinstall)
