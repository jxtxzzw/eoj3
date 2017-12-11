class RepositoryException(Exception):

    def __str__(self):
        return 'RepositoryException: ' + super().__str__()

