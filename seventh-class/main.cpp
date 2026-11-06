#include "student.h"
#include "ggml.h"

#include <cstddef>

#include <iostream>

#include <memory>

#include <vector>

int main()
{

    std::vector<std::unique_ptr<Student>> students;

    Student* raw_student = nullptr;


    create_student(
        &raw_student,
        "alice",
        {92.0,93.0,89.5}
    );

    students.emplace_back(raw_student);
    raw_student = nullptr;

        create_student(
        &raw_student,
        "Charlie",
        {95.0, 91.0, 96.0}
    );

    students.emplace_back(raw_student);
    raw_student = nullptr;

    std::cout << "所有学生：\n";

    for (const std::unique_ptr<Student>& student : students)
    {
        std::cout << student->name
                  << "，平均分："
                  << average_score(*student)
                  << '\n';
    }

    Student* top_student = find_top_student(students);

    if (top_student != nullptr)
    {
        std::cout << "\n最高分学生："
                  << top_student->name
                  << '\n';

        std::cout << "最高平均分："
                  << average_score(*top_student)
                  << '\n';
    }

        ggml_init_params params{};

    params.mem_size = 16 * 1024 * 1024;
    params.mem_buffer = nullptr;
    params.no_alloc = false;

    ggml_context* ctx = ggml_init(params);

    if (ctx == nullptr)
    {
        std::cerr << "failed to create ggml context\n";
        return 1;
    }

    ggml_tensor* tensor = ggml_new_tensor_1d(
        ctx,
        GGML_TYPE_F32,
        4
    );

    if (tensor == nullptr)
    {
        std::cerr << "failed to create tensor\n";
        ggml_free(ctx);
        return 1;
    }

    ggml_set_name(tensor, "demo_tensor");

    std::cout << "tensor name: "
              << ggml_get_name(tensor)
              << '\n';

    std::cout << "tensor elements: "
              << ggml_nelements(tensor)
              << '\n';

    std::cout << "tensor bytes: "
              << ggml_nbytes(tensor)
              << '\n';

    ggml_free(ctx);

    return 0;
}