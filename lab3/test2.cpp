#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#include <iostream>

using namespace std;

int main()
{
    int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    cout << "Socket ID:" << s << endl;  // Socket ID:3
    close(s);

    s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    cout << "Socket ID:" << s << endl;  // Socket ID:3
    close(s);
    return 0;

    // 값이 재사용 되어도 같은 소켓이 아님
    // 값이 우연히 같아도 둘은 완전히 다른 소켓
    // 따라서 socket()으로 얻어낸 것은 오직 1회만 close()해야 함
}