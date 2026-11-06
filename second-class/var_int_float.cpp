#include <iostream>
#include <limits>

int main()

{

    std::cout << std::numeric_limits<int>::min() << '\n';
    std::cout << std::numeric_limits<int>::max() << '\n';

    std::cout << std::numeric_limits<unsigned int>::min() << '\n';
    std::cout << std::numeric_limits<unsigned int>::max() << std::endl;

    unsigned int age = 0;
    std::cout << age << std::endl;
    std::cout << std::addressof(age) << std::endl;

    age = age - 1;
    std::cout << age << std::endl;
    std::cout << std::addressof(age) << std::endl;


    return 0;
}