#include <iostream>

#include <string>


int main(){
    int age = 10;
    float height = 21.3f;
    double weight = 120.22;
    char a = 'a';
    std::string name = "caiqiyue";
    bool is_student = false;

    std::cout << is_student << std::endl;
    std::cout << age << std::endl;
    std::cout << height << std::endl;
    std::cout << weight << std::endl;
    std::cout << a << std::endl;
    std::cout << name << std::endl;
    std::cout << std::boolalpha << is_student << '\n';
    return 0;
}