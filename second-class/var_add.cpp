#include <iostream>


int main()
{
    int age = 20;

    std::cout << age << std::endl;
    std::cout << &age << std::endl;
    std::cout << sizeof(age) << std::endl;
    age = 30;
    std::cout << age << '\n';
    std::cout << &age << std::endl;//修改值了，但是内存地址还是没有变
}