# New Pipe Subscription Manager
Little script to import YouTube subscriptions into NewPipe app.

# How to use script:
First, you need to get the latest version of Python 3. You can download it [here](https://www.python.org/downloads/).
Than follow installation [instructions](http://docs.python-guide.org/en/latest/starting/installation/)
Finally you need to ran the script:

`import_subscriptions.py [-h] [xml_path] [db_path]`

Import subscriptions from subscription_manager.xml to NewPipe database

positional arguments:
  xml_path    Path to subscription_manager.xml file. You can get it here:
              https://www.youtube.com/subscription_manager?action_takeout=1
  db_path     Path to NewPipeData-*.zip You can optain it in NewPipe app.
              Go to Settings -> Content -> Export database

optional arguments:
  -h, --help  show help message and exit
 
For example:
`./import_subscriptions.py ~/Downloads/subscription_manager.xml ~/Downloads/NewPipeData.zip`

Or in some cases:

`python3 ./import_subscriptions.py ~/Downloads/subscription_manager.xml ~/Downloads/NewPipeData.zip` 
