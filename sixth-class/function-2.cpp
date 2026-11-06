#include <iostream>





int add(int a,int b)
{
    int result = a + b;
    return result;
}

int * max_a_b(int * a,int * b)
{
    if (*a > *b)
    {
        return a;

    }
        
    return b;
}

int * add_ptr(int a,int b)
{
    int * rs = new int(a + b);
    return rs;
}

int * add_static(int a, int b)
{
    static int rs =  0;
    rs = a+b;
    return &rs;
}

int * arr_return(int arr[],const int length)
{
    for (int i =0;i<length;i++)
    {
        arr[i] = i;
    }
    return arr;
}




int main()
{

    return 0;
}