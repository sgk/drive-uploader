Google Drive Uploader
2015/6/4 by sgk

Summary:
Check your local folder periodically and upload the found files to your Google Drive. The uploaded files will be removed from your local folder.

Usage:
1. Visit the Google API console and create a project with the Drive API enabled.
2. Follow the menu "APIs & auth"->"Credentials". Download the credentials JSON
   and save it as "clients_secret.json" in this directory.
3. Open "uploader.py" with your favorite editor. Change the main loop to
   reflect your folder name.
4. Create an empty file "UPLOADDIR.txt" in your source folder.
5. Run "uploader.py". On the first time, the browser opens automatically and
   asks to authorize the access to the Drive.
