/*

Pwn0 

- Author DJEKMANI Azz-Eddine 

- gcc -mpreferred-stack-boundary=2 -fno-stack-protector -z execstack -o 0.c 0


*/
#include <stdio.h>

#include <string.h>
#include <stdlib.h>



#define BUFF_SIZE 64



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



int main(int argc, char argv)

{

        if(argc)

	{

		printf("Go Out ... \n");

		exit(1);

	}



	printf("Good Boy\n");

	vuln();

        return 0;

}
