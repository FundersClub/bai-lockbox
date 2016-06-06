# This file is part of bai-lockbox.

# bai-lockbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# bai-lockbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with bai-lockbox.  If not, see
# <http://www.gnu.org/licenses/>.

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
