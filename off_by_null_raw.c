#include<stdio.h>
struct chunk{
	long *point;
	unsigned int size;
}chunks[9];


void add()
{
	unsigned int index=0;
	unsigned int size=0;
	puts("Index:");
	scanf("%d",&index);
	if(index>=9)
	{
		puts("wrong index!");
		exit(0);
	}
	if(chunks[index].point)
	{
		puts("already exist!");
		return ;
	}

	puts("Size:");
	scanf("%d",&size);
	chunks[index].point=malloc(size);
	chunks[index].size=size;
	
	if(!chunks[index].point)
	{
		puts("malloc error!");
		exit(0);
	}
	
	char *p=chunks[index].point;
	puts("Content:");
	p[read(0,chunks[index].point,chunks[index].size)]=0;
}
void show()
{
	unsigned int index=0;
	puts("Index:");
	scanf("%d",&index);
	if(index>=9)
	{
		puts("wrong index!");
		exit(0);
	}
	if(!chunks[index].point)
	{
		puts("It's blank!");
		exit(0);
	}
	puts(chunks[index].point);
}
void edit()
{
	unsigned int index;
	puts("Index:");
	scanf("%d",&index);
	if(index>=9)
	{
		puts("wrong index!");
		exit(0);
	}
	if(!chunks[index].point)
	{
		puts("It's blank!");
		exit(0);
	}
	char *p=chunks[index].point;
	puts("Content:");
	p[read(0,chunks[index].point,chunks[index].size)]=0;
}
void delete()
{
	unsigned int index;
	puts("Index:");
	scanf("%d",&index);
	if(index>=9)
	{
		puts("wrong index!");
		exit(0);
	}
	if(!chunks[index].point)
	{
		puts("It's blank!");
		exit(0);
	}
	
	free(chunks[index].point);
	chunks[index].point=0;
	chunks[index].size=0;
}
void menu()
{
	puts("(1) add a chunk");
	puts("(2) show content");
	puts("(3) edit a chunk");
	puts("(4) delete a chunk");
	puts(">");
}

void init()
{
	setvbuf(stdin,0,2,0);
	setvbuf(stdout,0,2,0);
	setvbuf(stderr,0,2,0);

}
void main()
{
	init();
	unsigned int choice;
	puts("Welcome to new school note.");
	while(1)
	{
		menu();
		scanf("%d",&choice);
		switch(choice)
		{
			case 1:
				add();
				break;
			case 2:
				show();
				break;
			case 3:
				edit();
				break;
			case 4:
				delete();
				break;
			default:
				exit(0);
		}
	}

}