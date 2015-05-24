#MCSC2015 writeup for ELF-1<br>

```
root@kali:~/Desktop# file fact
fact: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 2.6.24,
BuildID[sha1]=0xff11602da873d33f1f021be4600ed89c6a7b38a1, not stripped
```

On exécute le programme, pour comprendre le fonctionnement :
```
root@kali:~/Desktop# ./fact
Enter your password
AAAAAA
no no noo noo
```

Le programme effectue une vérification de mot de passe
On analyse l’exécutable à l’aide de l’outil ltrace (http://linux.die.net/man/1/ltrace) .
```
root@kali:~/Desktop# echo AAAA | ltrace ./fact
…
strcmp("EEGG", "Ecd3l7G?9m") = -30
…
```

On remarque que le programme compare deux chaines de caractéres, "EEGG" et "Ecd3l7G?9m"
Une deuxième exécution nous donne le résultat suivant :
```
root@kali:~/Desktop# echo BBBB | ltrace ./fact
strcmp("CCCC", "Ecd3l7G?9m") = -2
```

Donc le programme applique une fonction à notre chaine de caractère avant de la comparer avec le mot "Ecd3l7G?9m"
On a le texte clair, et le texte chiffré. 
Un petit script python pour automatiser la tâche :

```
cat attack.py
import commands
import string
import time
cypher = "Ecd3l7G?9m"
passwd=''
for i in range (len(cypher)):
 for key in string.printable:
 res = commands.getstatusoutput('echo "'+passwd+str(key)+'" | ltrace -o res -e strcmp ./fact')
 text=open('res')
 lettre=str(text.read().split('"')[1])
 if lettre==cypher[0:i+1]:
 passwd=passwd+key
 print passwd
 i+=1
 break
print "mot de passe est "+passwd
```

Résultat de l’exécution du script :
```
root@kali:~/Desktop# python atack.py
A
Ab
Abd
Abd0
Abd0k
Abd0k5
Abd0k5A
Abd0k5A1
Abd0k5A11
Abd0k5A11i
mot de passe est Abd0k5A11i
```
Et Voila !!
```
root@kali:~/Desktop# ./fact
Enter your password
Abd0k5A11i
You win :D ^^
```
