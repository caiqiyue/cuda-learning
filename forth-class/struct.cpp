#include <iostream>

int main()
{

    struct Student
    {
        int age;
        std::string name;
        bool sex;
        std::string class_name =  "一班";
    };

    std::cout << sizeof(int) << std::endl;
    std::cout << sizeof(std::string) << std::endl;
    std::cout << sizeof(bool) << std::endl;
    std::cout << sizeof(Student) << std::endl;

    Student s1 = {10,"caiqyue",true};
    std::cout << s1.name << s1.age << s1.sex << s1.class_name << std::endl;



    Student class_two[2] = 
    {
        {9,"cajhdad",1,"二班"},
        {11,"ca312414hdad",0,"二班"}
    };

        std::cout << sizeof(class_two) / sizeof(Student) << std::endl;

    for (int i = 0; i < sizeof(class_two) / sizeof(Student); i ++)
    {
        std::cout << class_two[i].name << std::endl;
    }

    Student * p = &s1;
    Student * p_arr = class_two;

    p->name = "caiqiyue123";
    std::cout << (*p).name << std::endl;
    std::cout << p->name << std::endl;

    std::cout << p_arr[1].name << std::endl;
    std::cout << (*(p_arr + 1)).name << std::endl;
    std::cout << (p_arr + 1)->name << std::endl;

    Student * p_arr_new = new Student[] {{12,"fasdfa",1},{312,"efwe",0,"sandasa"}};

    std::cout  << p_arr_new[1].class_name << std::endl;
    std::cout  << (p_arr_new+1)->class_name << std::endl;
    std::cout  << (*(p_arr_new+1)).class_name << std::endl;

    delete[] p_arr_new;
    p_arr_new = nullptr;


    return 0;
}