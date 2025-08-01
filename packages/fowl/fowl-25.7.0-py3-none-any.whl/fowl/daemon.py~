import automat


class FowlDaemon:
    """
    TODO: a good docstring
    """
    m = automat.MethodicalMachine()

    @m.state(initial=True)
    def waiting_code(self):
        """
        We do not yet have a wormhole code.
        """

    @m.state()
    def have_code(self):
        """
        We have a code.
        """

    @m.input()
    def wormhole_got_code(self, code):
        """
        We have acquired a Wormhole code somehow
        """

    waiting_code.upon(
        wormhole_got_code,
        enter=have_code,
        outputs=[]
    )
