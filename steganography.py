#!/usr/bin/python
import string,sys,os.path, random
import ImageFile  # Thanks to http://wordaligned.org for the steganography code!
import pystega as pystega 


# AS FAR AS I CAN READ:               This product uses the Flickr API but
# FLICKR'S TOS DO *NOT*               is not endorsed or certified by Flickr.
# BAN THIS AS OF TODAY,               Neither I nor Flickr are responsible for
# THEY ARE EXPLICIT IN                ANY damage, intentional or accident to
# SECTION 3: DO NOT USE               your property, freedom, right to vote,
# AS GENERAL IMAGE HOST               personal belongings, physical health, 
# WE ARE USING THEM AS                metaphysical health, mental health, or
# A HOST FOR EVERYTHING               sanity. THIS IS DONE WITHOUT THE EXPRESS
# ~ Kemus                             PERMISSION OF YAHOO/FLICKR, and I expect
# t @feedmecode                       it will stop working permanently, causing
# g feedmecode@gmail.com              full data loss, and the men in vans will
# y feedmecode@yahoo.com              take me away, who knows they might even
# github: kemus                       give me an internship...

#f= FlickrAPI("5ba8d6f0cab29be62c6f54ea66998b15","0d66ff189cdd75b2")
if len(sys.argv) < 2: 
  # debug("DECODE BY: python steganography.py encryptedimage")
  # debug("ENCODE BY: python steganography.py file picture picture2 ...")
  # debug("Running with test arguments")
  sys.argv=[sys.argv[0], 'message.txt', 'picture.jpg']
messagepath = sys.argv[1]
picturepaths = sys.argv[2:]
numpictures = len(picturepaths)
def debug(*messages):
  print "Debug: ",
  for message in messages: print message,
  print
def crash(*errors):
  print "Error: ",
  for error in errors: print error,
  print
  exit(1)


def getpic(picturepath):
  debug("Loading next picture...")
  
  try:
    picturepath = os.path.expandvars(os.path.expanduser(picturepath))
    picturepath = os.path.abspath(picturepath)
    if not os.path.exists(picturepath) or not os.path.isfile(picturepath):
      crash("Could not find picture", picturepath, " file ",picturepath)
    with open(picturepath, 'rb') as picturefile: 
      parser = ImageFile.Parser()
      nextdata = picturefile.read(1024)
      if not nextdata:
        crash( "no data")
      while nextdata:
        parser.feed(nextdata)
        nextdata = picturefile.read(1024)
      picture = parser.close()
      npixels = picture.size[0] * picture.size[1]
      nbands = len(picture.getbands())
      pichides = npixels*nbands/8
      debug("Picture ",picturepath, "loaded\n"+
      "       ",picturepath,"can hide", str(pichides), "bytes")
      return picture, picturepath , pichides     
  except Exception as e:
    crash("Could not open picture file ", picturepath,e) 


def encode(messagepath,picturepaths):
  basepid=random.randint(1000,8000)
  numpics = 0
  pid = 0
  debug("Encoding with picturepaths=", picturepaths)
  try:
    messagepath = os.path.expandvars(os.path.expanduser(messagepath))
    messagepath = os.path.abspath(messagepath)
    message = True
    if not os.path.exists(messagepath):
      crash("Could not find file ",messagepath)
    if os.path.isdir(messagepath):
      crash("TO BE IMPLEMENTED AFTER MY ESSAY")
    out =getpic(picturepaths[pid])
    pic, picturepath,plen = out
    with open(messagepath, 'r') as  messagefile:   
      message = messagefile.read()
    messagelen = len(message)
    processed = ""
    while message:
      pid = (pid+1)%numpictures
      numpics+=1
      pin = messagepath     
      processing,message=message[:plen],message[plen:]
      processed += processing
      hid=pystega.disguise(pic.copy(),processing, pin)
      hid2=hid.save("DCIM"+str(basepid+pid)+".png")
      debug("Picture #"+str(basepid+pid)+":", pic.mode, pic.format, "hid")
      debug(str(len(processing)) + "/" + str(plen) + " of file used")
      debug(str(len(processed))+ "/" + str(messagelen) + " of payload hidden")
    return "DCIM"+str(basepid+pid)+".png"  
  except Exception as e: 
    crash("Could not open message file ",str(e))

#Decode
def decode():
  picturename=sys.argv[1]
  out,pout=pystega.reveal(getpic(picturename)[0])
  print pout, out


if(len(sys.argv)==2):
 decode()
 pass

else:
  fout = encode(messagepath, picturepaths)
#  f.api_request('http://api.flickr.com/services/upload/', 'POST', {'hidden':'2'},open(fout))

