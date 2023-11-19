#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <unistd.h>

#include <iostream>
#include <string>

using namespace std;

int main()
{
    int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (s < 0)  // 음수가 나온다면 오류가 발생한 것
        return 1;   

    string buf = "Hello World";

    struct sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(10000);    // Port num
    sin.sin_addr.s_addr = inet_addr("127.0.0.1");   // Address

    int numBytes = sendto(s, buf.c_str(), buf.length(),
                          0, (struct sockaddr *)&sin, sizeof(sin));
    cout << "Sent: " << numBytes << endl; 
    // Sent: 11 -> Hello World가 11 Bytes이므로 11이 출력

    close(s);
    return 0;
}