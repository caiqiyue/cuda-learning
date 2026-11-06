#include "student.h"

double average_score(const Student& student)
{
    if (student.scores.empty())
    {
        return 0.0;
    }
    double total = 0.0;
    for (double score:student.scores)
    {
        total += score;
    }
    return total / student.scores.size();
}

void create_student(
    Student** result,
    const std::string& name,
    const std::vector<double>& scores
)
{
    if (result==nullptr)
    {
        return;
    }
    *result = new Student{name,scores};
}


Student* find_top_student(
    const std::vector<std::unique_ptr<Student>>& students
)
{
    if(students.empty())
    {
        return nullptr;
    }
    Student* top_student = students[0].get();
    
    for (const std::unique_ptr<Student>& student:students)
    {
        if(average_score(*student) > average_score(*top_student))
        {
            top_student = student.get();
        }
    }

    return top_student;
}