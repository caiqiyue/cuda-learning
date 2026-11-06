#include <iostream>

int main()
{

    double num1 = 10;
    double * num1_ptr = &num1;

    std::cout << *num1_ptr << std::endl;


    int v[3] = {1,2,3};
    std::cout << v << std::endl;
    int * p = v;
    std::cout << *p << std::endl;
    std::cout << p << std::endl;
    std::cout << *(p + 1) << std::endl;
    p++ ;
    std::cout << p  << std::endl;
    std::cout << v+1 << std::endl;
    *p = 10;
    std::cout << v[1] << std::endl;
    return 0;
}