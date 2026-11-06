#include <iostream>
#include <string>
using namespace std;

int main()
{

    char letter = 'a';
    cout << letter << '\n';
    cout << letter + 1 << '\n';
    cout << 'a' + 1 << '\n';

    char a[] = "ilikeyou";
    char *b = "dasda";
    cout << a << '\n';
    cout << b << '\n';

    // string lane;
    // cin >> lane;
    // cout << lane << '\n';

    string lane2;
    
    getline(cin, lane2);

    cout << lane2 << '\n';


    return 0;
}