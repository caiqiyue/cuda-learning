#ifndef STUDENT_H

#define STUDENT_H


#include <iostream>
#include <string>
#include <vector>
#include <memory>


struct Student
{
    std::string name;
    std::vector<double> scores;
};
// 返回学生平均分。
// const Student&：按引用传递，避免复制；const 表示函数不会修改学生信息。
double average_score(const Student& student);


// 在 Student* 列表中查找平均分最高的学生。
// const vector<...>&：按引用传递，避免复制；const 表示不修改列表。
// 返回 Student*：返回最高分学生的地址，只用于访问，不负责释放对象。
Student* find_top_student(
    const std::vector<Student*>& students
);

// 创建一个 Student 对象，并把地址写入调用者的指针。
// Student**：传入 Student* 的地址，使函数可以修改外部指针。
// name 和 scores 使用 const 引用，避免复制且不修改参数。
void create_student(
    Student ** result,
    const std::string& name,
    const std::vector<double>& scores
);

// 在 unique_ptr<Student> 列表中查找平均分最高的学生。
// unique_ptr 负责对象生命周期；本函数只访问对象，不负责释放。
// 返回 Student*：返回观察指针，不转移所有权。
Student* find_top_student(
    const std::vector<std::unique_ptr<Student>>& students
);


#endif