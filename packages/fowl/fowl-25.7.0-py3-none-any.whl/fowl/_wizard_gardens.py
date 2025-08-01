import os

import click


@click.group()
def wizard_gardens():
    """
    Experiments towards a unified Magic Wormhole UI and glue-code
    runner for local services across the network
    """
    pass


@wizard_gardens.command()
def polkit():
    """
    Can we ask for authentication via dbus?
    """
    import dbus
    #session = dbus.SessionBus()
    session = dbus.SystemBus()
    pk = session.get_object("org.freedesktop.PolicyKit1", "/org/freedesktop/PolicyKit1/Authority")
    print(pk)
    subject = [
        "unix-process",
         dict(
             pid=os.getpid(),
         ),
    ]
    action = "org.freedesktop.Flatpak.app-install"
    details = {}
    flags = {}
    cancellation_id = "cancel-me"
    foo = dbus.Interface(pk, dbus_interface="org.freedesktop.PolicyKit1.Authority")
    out = foo.CheckAuthorization(subject, action, details, flags, cancellation_id)
    print(out)
    if False:
        out = foo.EnumerateActions("org.freedesktop.PolicyKit1.Authority")
        names = sorted(i[0] for i in out)
        for x in names:
            print(x)
