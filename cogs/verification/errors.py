from dataclasses import dataclass
from utils.errors import WhiteException

class VerificationError(WhiteException):
    pass

class AlreadyVerified(VerificationError):
    pass

class OwnershipNotProved(VerificationError):
    pass

class RequirementsNotSatsified(VerificationError):
    pass

@dataclass
class MissingPermissions(VerificationError):
    add_role: bool
    remove_role: bool
    change_nickname: bool
    create_role: bool