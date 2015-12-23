#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void getFlag()
{
	printf("you win\n");
	char flag[26];
	FILE *f = fopen("flag.txt" , "r");
	fread(flag, 25 , 1 , f);
	flag[25] = '\0';
	write(1 , flag , strlen(flag));
}

void welcome()
{
char buff[64];
printf("your name bro: ");
fflush(stdout);
read(0 , buff, 80);
printf("Your are a good boy\n");

}
int main()
{
welcome();
return 0;
}
