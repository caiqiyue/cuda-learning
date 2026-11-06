#include <iostream>

int main()
{
    int num = 10;
    int * p = &num;

    std::cout << num << std::endl;
    std::cout << &num << std::endl;

    std::cout << p << std::endl;
    std::cout << *p << std::endl;


    *p = 20;
    std::cout << *p << std::endl;
    std::cout << &num << std::endl;
    std::cout << num << std::endl;
    std::cout << p << std::endl;

    return 0;
}