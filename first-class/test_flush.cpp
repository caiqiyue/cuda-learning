
#include <iostream>
#include <thread>
#include <chrono>

int main()
{
    std::cout << "Hello";

    std::this_thread::sleep_for(//等待睡5秒
        std::chrono::seconds(5)
    );

    std::cout << " World" << std::flush;

    return 0;
}
