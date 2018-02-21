# Smarttrack
Smarttrack Mailroom System replacement

As Smarttrack Mailroom System has no longer support by vendor

Even you paid a big bucks you still cannot get the old tracking recording.

So i re-write the system by python. 

Only have 2 function

1. Scan the package and print a lable then store the info to database

2. Search the record and display the signature.

This system need some python package

1. Python 3.7
2. appJar (GUI)
3. MysqlDB (DB connect)
4. PIL (Display signature)
5. WMI (Get local IP)
6. zebra (Print lable)
7. wheel
8. pywin32

For the database part, I use Mysql. Only 6 Table is needed.
you can import from the old Smarttrack DB
`carriersservices`
`employees`
`itemlog`
`itemstatus`
`senders`
`signatures`



