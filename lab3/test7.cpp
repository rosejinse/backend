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

    string buf = "test7";

    struct sockaddr_in sin;

    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = INADDR_ANY;
    sin.sin_port = htons(10000 + 134);
    if (bind(s, (struct sockaddr *) &sin, sizeof(sin)) < 0) {
        cerr << strerror(errno) << endl;
        return 0;
    }

    // -----------Sent part---------------
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(20000 + 134);
    sin.sin_addr.s_addr = inet_addr("127.0.0.1");

    int numBytes = sendto(s, buf.c_str(), buf.length(),
                          0, (struct sockaddr *)&sin, sizeof(sin));
    cout << "Sent: " << numBytes << ", " << buf << endl;

    // ----------Recevied part----------------
    char buf2[65536];
    memset(&sin, 0, sizeof(sin));
    socklen_t sin_size = sizeof(sin);
    numBytes = recvfrom(s, buf2, sizeof(buf2), 0,
                        (struct sockaddr *)&sin, &sin_size);
    cout << "Recevied: " << numBytes << ", " << buf2 << endl;
    cout << "From " << inet_ntoa(sin.sin_addr) << endl; // inet_ntoa: inet network to askii

    memset(&sin, 0, sizeof(sin));
    sin_size = sizeof(sin);
    int result = getsockname(s, (struct sockaddr *) &sin, &sin_size);
    if (result == 0) {
        cout << "My addr: " << inet_ntoa(sin.sin_addr) << endl;
        cout << "My port: " << ntohs(sin.sin_port) << endl;
    }

    close(s);
    return 0;
}