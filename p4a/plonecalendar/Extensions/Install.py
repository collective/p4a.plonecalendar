from p4a.plonecalendar.sitesetup import unsetup_portal

def uninstall(self, reinstall=False):
    unsetup_portal(self, reinstall=reinstall)
    
    