# https://github.com/raymondlowe/Google-Search-Console-Add-Missing-Variations
# by Raymond Lowe
# 
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import httplib2
from apiclient.discovery import build
import pandas 
from urllib.parse import urlparse

# copied from original example
def get_service(api_name, api_version, scope, client_secrets_path):
  """Get a service that communicates to a Google API.

  Args:
    api_name: string The name of the api to connect to.
    api_version: string The api version to connect to.
    scope: A list of strings representing the auth scopes to authorize for the
      connection.
    client_secrets_path: string A path to a valid client secrets file.

  Returns:
    A service that is connected to the specified API.
  """
 
  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      client_secrets_path, scope=scope,
      message=tools.message_if_missing(client_secrets_path))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage(api_name + '.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service

# Pseudocode

# Connect to GSC
scope = ['https://www.googleapis.com/auth/webmasters']

# Authenticate and construct service.
service = get_service('webmasters', 'v3', scope, 'client_secrets.json')

# Download list-of-properties of current sites

profiles = service.sites().list().execute()

dataframe = pandas.DataFrame(list(profiles['siteEntry']))
#now it is a dataframe

profileslist = dataframe['siteUrl'].tolist()
#now it is a list again

# Loop through list-of-properties
for i in profileslist:
  
#   If item does not startsc-domain:
  if i[:10] != "sc-domain:":

    # strip it down to just the domain name
    url = str(i)
    if url[:7] == 'http://':
      url = url[7:]
    if url[:8] == 'https://':
      url = url[8:]    
    if url[:4] == 'www.':
      url = url[4:]    

    # consider the four possible variations
    for variation in ['https://','http://','https://www.','http://www.']:
      proposal = variation + url 
      if proposal not in profileslist:
        print('Add: '+proposal)
        results = service.sites().add(siteUrl=proposal).execute()
      else:
        print('Skip: '+proposal)


print("--done--")

