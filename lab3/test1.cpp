#include <arpa/inet.h>  // the Internet 관련 함수들
#include <sys/socket.h> // socket 관련 함수들
#include <unistd.h>     // Unix 계열에서 표준 기능 함수들

#include <iostream>

using namespace std;

int main()
{
    int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    cout << "Socket ID:" << s << endl;      // Socket ID: 3

    close(s);
    return 0;
}