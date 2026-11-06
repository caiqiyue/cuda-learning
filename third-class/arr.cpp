#include <iostream>

int main()
{
    int num1[] = {1,2,3,4,5,6};

    int *p = num1;
    for (int i = 0;i < 6; i ++)
    {
        std::cout << *(p + i) << std::endl;
    }


    int * num = new int[5];
    for (int j = 0; j < 5;j++)
    {
        num[j] = j + 1;
        std::cout << num[j] << std::endl;
    }

    int * new_num = new int[6];
    int pos = 3;
    int data = 10;
    int offset = 0;
    for (int v = 0;v < 6;v++)
    {
        if (v == pos)
        {
            new_num[v] = data;
            offset += 1;
        }
        else
        {
            new_num[v] = num[v-offset];
        }
    }

    delete[] num;
    num = new_num;

    for (int z = 0;z<6;z++)
    {
        std::cout << num[z] << std::endl;
    }
    delete[] num;
    num = nullptr;


    //int num_new[] = new int[6];


    return 0;
}