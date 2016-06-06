class LockboxError(Exception):
    pass


class LockboxDefinitionError(LockboxError):
    '''Base exception for problems related to the actual definition of a
    new lockbox record.
    '''
    pass


class LockboxParseError(LockboxError):
    '''Base exception for problems related to reading a BAI Lockbox
    record.
    '''
    pass


class LockboxConsistencyError(LockboxError):
    '''Exception for problems relating to the consistency of the data in a
    correctly parsed lockbox file.
    '''
    pass
