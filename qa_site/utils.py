import re


def extract_mentions(text)-> list:
   """
   Return a list containing the usernames in `text`;
   Remember usernames should be between 4 & 15 characters and alphanumeric(\w)
   """
   INVALID_USERNAME_LENGTH_THRESHOLD = 16
   
   # Note that this will get and trim words that have more than 16 chars. 
   result = re.findall(r"(^|[^@\w])@(\w{4,16})", text, re.UNICODE)

   # Now get words that don't have 16 chars. (that have 15 and below)
   usernames = [tuple[1] for tuple in result if len(tuple) != INVALID_USERNAME_LENGTH_THRESHOLD]

   return usernames
