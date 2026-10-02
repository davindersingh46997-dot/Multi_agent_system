from brain.database.session import get_db

    
def create_user(db,user):

    """
    Create a new user in the database.
    """

    if not db:
        raise ValueError("Database session is not provided.")

    if not user:
        raise ValueError("User data is not provided .")

