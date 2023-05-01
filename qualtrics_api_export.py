import http.client, pandas as pd, zipfile, json
from io import BytesIO #To read data encoded bytes
from time import sleep ##To create delays between consecutive API calls

#Data center and API token associated with Qualtrics account.
dataCenter = ""
QUALTRICS_API_TOKEN = ""

# create the request
conn = http.client.HTTPSConnection(f"{dataCenter}.qualtrics.com")
body = '''
{
    "format": "csv",
    "useLabels":"true"
}
'''
headers = {
 'X-API-TOKEN' : f'{QUALTRICS_API_TOKEN}',
 'Content-Type': 'application/json'
}

#ID of survey you want to extract the data from
surveyID = ""

conn.request("POST", f"/API/v3/surveys/{surveyID}/export-responses/", body, headers)
#res it what the API returns after sending the request. After you read() it, thats the results
res = conn.getresponse()
data = res.read()

#The result that is return is a dictionary encoded in bytes. Using the decode function in conjuction with the loads
#function returns the dictionary with the information that you need; the progressId
progressID = json.loads(data.decode("utf-8"))["result"]["progressId"]

#Initialize the two fields that we need from the request
status, fileID = "", ""
while True:
  #The next request is a "GET" and returns the status and fileId of the requested survey file data.
  #Depending on the size of the file, it may take a while for the "status" to be complete
  #The loop pauses then sends the request and if status is complete then the request returns a fileId and breaks out of the loop
  #If status is not complete the code pauses before running the request again.
  sleep(7)
  conn.request("GET", f"/API/v3/surveys/{surveyID}/export-responses/{progressID}", body, headers)
  res = conn.getresponse()
  data = res.read()

  status = json.loads(data.decode("utf-8"))["result"]["status"]
  if status == "complete":
    fileID = json.loads(data.decode("utf-8"))["result"]["fileId"]
    break

#The last "GET" request returns the file that was requested. The API response returns a byte encoded zipfile so it is impossible to
#decode the string as in the previous requests. 
conn.request("GET", f"/API/v3/surveys/{surveyID}/export-responses/{fileID}/file", body, headers)
res = conn.getresponse()
data = res.read()

#Using the IO and zipfile library, we extract the file which dumps the file into the enviroment
zipfile.ZipFile(BytesIO(data)).extractall()

conn.close()


df = pd.read_csv("Path to File").drop([0,1])
df.reset_index(drop=True, inplace=True)
