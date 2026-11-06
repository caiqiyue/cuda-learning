#include <iostream>
#include <iomanip>
int main()
{



    float num = 10;

    float num1 = 123.32;

    float num2 = 123.4567890;

    double num3 = 123.4567890;

    std::fixed;
    std::cout.width(20);
    std::cout << num << std::endl;
    std::cout << num1 << std::endl;
    std::cout << num2 << std::endl;
    std::cout << num3 << std::endl;


    std::cout << "128 is " << sizeof(128)  <<  std::endl;
    std::cout << "0.8932  is " << sizeof(0.8932) << std::endl;

 


    float a = 1.23456789f;
    double b = 1.23456789;

    std::cout << "default float: " << a << '\n';
    std::cout << "fixed float: " << std::fixed << std::setprecision(9) << a << '\n';
    std::cout << "fixed double: " << b << '\n';
    std::cout << "width example: [" << std::setw(20) << b << "]\n";
    std::cout << "sizeof(float)=" << sizeof(a) << '\n';


    return 0;
}