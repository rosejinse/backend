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
    if (s < 0)
        return 1;

    string buf = "test4";

    struct sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(20000 + 134);
    sin.sin_addr.s_addr = inet_addr("127.0.0.1");

    int numBytes = sendto(s, buf.c_str(), buf.length(),
                          0, (struct sockaddr *)&sin, sizeof(sin));
    cout << "Sent: " << numBytes << endl;   // Sent: 5
    cout << "Sent: " << buf << endl;        // Sent: test4

    char buf2[65536];
    socklen_t sin_size = sizeof(sin);   // 보낸 사람 주소 담을 변수 크기
    numBytes = recvfrom(s, buf2, sizeof(buf2), 0,
                        (struct sockaddr *)&sin, &sin_size);
    cout << "Recevied: " << numBytes << endl;
    cout << "Recevied: " << buf2 << endl;
    cout << "From " << inet_ntoa(sin.sin_addr) << endl; // inet_ntoa: inet network to askii

    close(s);
    return 0;
}