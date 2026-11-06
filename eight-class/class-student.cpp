#include <iostream>

#include <string>


class Student
{
    public:
    int age;
    std::string name;

    void print_class()
    {
        std::cout << "nihao" << std::endl;
    }


};




int main()
{
    Student s1;
    s1.name = 'caiqiyue';
    s1.age = 210;
    s1.print_class();
    return 0;
}