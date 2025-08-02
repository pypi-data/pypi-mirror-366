class RevisionPublishError(Exception):
    pass


class RevisionPublishStatusError(RevisionPublishError):
    pass


class RevisionRevertError(Exception):
    pass


class RevisionRevertStatusError(RevisionRevertError):
    pass


class RevisionRevertContentError(RevisionRevertError):
    pass
