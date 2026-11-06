#include <iostream>
#include <vector>

enum class RunState {
    Ready,
    Processing,
    Stopped
};

int main() {
    std::vector<int> requests = {8, -1, 16, 0, 32};
    RunState state = RunState::Ready;

    for (int tokens : requests) {
        if (tokens < 0) {
            std::cout << "跳过非法请求\n";
            continue;
        } else if (tokens == 0) {
            state = RunState::Stopped;
            break;
        } else {
            state = RunState::Processing;
            std::cout << "处理 token 数：" << tokens << '\n';
        }
    }

    switch (state) {
        case RunState::Ready:
            std::cout << "状态：就绪\n";
            break;
        case RunState::Processing:
            std::cout << "状态：处理中\n";
            break;
        case RunState::Stopped:
            std::cout << "状态：已停止\n";
            break;
    }

    return 0;
}