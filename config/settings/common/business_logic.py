# This file holds settings specific to the project
LIMIT_HOUR = 1  # Expiration time for session
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = LIMIT_HOUR * 60 * 60
