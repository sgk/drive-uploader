#!/usr/bin/python
# vim: set fileencoding=utf-8

# Copyright (c) 2015 by Shigeru KANEMOTO, All rights reserved.
# Licensed under the MIT license.

import sys
import os
import os.path
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'lib')

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

MARKER = 'UPLOADDIR.txt'

def GetDirectory(drive, path):
  path = path.split('/')
  if len(path) > 0 and path[0] == '':
    path.pop(0)
  if len(path) > 0 and path[-1] == '':
    path.pop(-1)

  d = drive.CreateFile({'id': 'root'})
  for c in path:
    files = drive.ListFile({'q': u"title='%s' and '%s' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'" % (c, d.get('id'))}).GetList()
    if len(files) == 0:
      return None
    d = files[0]
  return d

def CheckAndUpload(drive, srcDirPath, dstDirPath):
  # Check if the correct directory
  try:
    open(os.path.join(srcDirPath, MARKER))
  except IOError, e:
    print >>sys.stderr, e
    return

  # Get the list of files
  try:
    files = os.listdir(srcDirPath)
  except OSError, e:
    print >>sys.stderr, e
    return
  files.remove(MARKER)
  if len(files) == 0:
    # Nothing to upload
    return

  # Google Drive
  dstDir = GetDirectory(drive, dstDirPath)
  if dstDir == None:
    print >>sys.stderr, u'No such directory on server: %s' % dstDirPath
    return
  dstDirId = dstDir.get('id')

  for fname in files:
    if fname.startswith('.') or fname.startswith('_'):
      continue
    srcFilePath = os.path.join(srcDirPath, fname)
    if not os.path.isfile(srcFilePath):
      continue
    tmpFilePath = os.path.join(srcDirPath, '_' + fname)

    print >>sys.stderr, 'Uploading:', srcFilePath

    # Duplicate Check
    if len(drive.ListFile({'q': u"title='%s' and '%s' in parents and trashed=false" % (fname, dstDirId)}).GetList()) != 0:
      print >>sys.stderr, u'Duplicate: %s/%s' % (dstDirPath, fname)
      continue

    # New file instance
    dstFile = drive.CreateFile(
      {
        'title': fname,
        'parents': [
          {'kind': 'drive#fileLink', 'id': dstDirId}
        ]
      }
    )

    try:
      # On Windows, assert the file is not opened by other process.
      os.rename(srcFilePath, tmpFilePath)

      dstFile.SetContentFile(tmpFilePath)
      dstFile.Upload()
      del dstFile # Without this, the next remove fails on Windows.

      os.remove(tmpFilePath)
      print >>sys.stderr, u'Uploaded: %s/%s' % (dstDirPath, fname)
    except (IOError, OSError, WindowsError), e:
      print >>sys.stderr, e

def main():
  auth = GoogleAuth()
  auth.LocalWebserverAuth()
  drive = GoogleDrive(auth)

  print >>sys.stderr, 'Start watching directories...'
  while True:
    # Change here according to your environment.
    CheckAndUpload(drive, u'src', u'dst')
    time.sleep(30)

if __name__ == '__main__':
  main()
