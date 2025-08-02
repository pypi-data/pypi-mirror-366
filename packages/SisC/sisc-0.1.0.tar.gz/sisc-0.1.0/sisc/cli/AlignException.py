class AlignException(Exception):

    def __init__(self, reason):
        self.reason = reason
        super().__init__(f'Could not align: {reason}')
