#include <iostream>

int main()
{

    return 0;
}
/*

PS E:\ai-learning\07-inference-and-serving\cuda-learning\first-class\test_multi_main> g++ a.cpp b.cpp -o combined.exe
C:/msys64/ucrt64/bin/../lib/gcc/x86_64-w64-mingw32/16.2.0/../../../../x86_64-w64-mingw32/bin/ld.exe: C:\Users\ADMINI~1\AppData\Local\Temp\ccziirxT.o:b.cpp:(.text+0x0): multiple definition of `main'; C:\Users\ADMINI~1\AppData\Local\Temp\cco5zEdN.o:a.cpp:(.text+0x0): first defined here
collect2.exe: error: ld returned 1 exit status
PS E:\ai-learning\07-inference-and-serving\cuda-learning\first-class\test_multi_main> 
*/