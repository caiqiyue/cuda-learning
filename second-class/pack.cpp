
#include <iostream>
#include <cstdint>

int main()
{
    uint8_t q1 = 3;
    uint8_t q2 = 6;

    // 把两个 4-bit 数值打包成 8 bit
    uint8_t packed = (q2 << 4) | q1;

    // 解包
    uint8_t a = packed & 0x0F;
    uint8_t b = (packed >> 4) & 0x0F;

    std::cout << "a = " << int(a) << '\n';
    std::cout << "b = " << int(b) << '\n';

    return 0;
}
