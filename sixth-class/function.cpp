#include <iostream>


int add(int a,int b)
{
    return a + b;
}


void print_f()
{
    std::cout << "nihao" << std::endl;
}

void print_f_mul(int n)
{
    for (int i = 0; i < n;i++)
    {
        print_f();
    }
}


void swap_value(int a,int b)
{
    int tmp = a;
    a = b;
    b = tmp;
}

void swap_address(int * a,int * b)
{
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

void swap_reference(int &a,int &b)
{
    int tmp = a;
    a = b;
    b= tmp;
}

void print_arr_size(int arr[])
{
    std::cout << sizeof(arr) << std::endl;
}








int main()
{
    return 0;

}