import MySQLdb

# import mysql.connector

import sys
from PIL import Image
import base64 
import io
import PIL.Image

db = MySQLdb.connect(user='root', password='wks01admin',
                              host='localhost',
                              database='smarttrack')



# db = mysql.connector.connect(user='root', password='abhi',
#                              host='localhost',
#                              database='cbir')

#image = Image.open('C:\Users\Abhi\Desktop\cbir-p\images.jpg')
#blob_value = open('C:\Users\Abhi\Desktop\cbir-p\images.jpg', 'rb').read()
#sql = 'INSERT INTO img(images) VALUES(%s)'    
#args = (blob_value, )
#cursor.execute(sql,args)

cursor=db.cursor()
sql1='SELECT SigSignature FROM smarttrack.signatures where SigID = 42300;'
db.commit()
cursor.execute(sql1)
data=cursor.fetchall()
# print type(data[0][0])
file_like=io.BytesIO(data[0][0])
img=PIL.Image.open(file_like)
img.show()
db.close()