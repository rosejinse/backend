#include <fstream>
#include <string>
#include <iostream>
#include <arpa/inet.h>

#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <unistd.h>

#include "person.pb.h"

using namespace std;
using namespace mju;

int main()
{
    Person *p = new Person;
    p->set_name("DK Moon");
    p->set_id(12345678);
    
    Person::PhoneNumber* phone = p->add_phones();
    phone->set_number("010-111-1234");
    phone->set_type(Person::MOBILE);
     
    phone = p->add_phones();
    phone->set_number("02-100-1000");
    phone->set_type(Person::HOME);
    
    const string s = p->SerializeAsString();
    cout << "Length:" << s.length() << endl;
    cout << s << endl;


    int sk = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sk < 0)
        return 1;

    string buf = s;

    struct sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(10001);
    sin.sin_addr.s_addr = inet_addr("127.0.0.1");

    int numBytes = sendto(sk, buf.c_str(), buf.length(),
                          0, (struct sockaddr *)&sin, sizeof(sin));
    cout << "Sent: " << numBytes << endl;
    cout << "Sent: " << buf << endl;

    char buf2[65536];
    socklen_t sin_size = sizeof(sin);   // 보낸 사람 주소 담을 변수 크기
    numBytes = recvfrom(sk, buf2, sizeof(buf2), 0,
                        (struct sockaddr *)&sin, &sin_size);
    cout << "Recevied: " << numBytes << endl;
    cout << "Recevied: " << buf2 << endl;
    cout << "From " << inet_ntoa(sin.sin_addr) << endl; // inet_ntoa: inet network to askii




    Person *p2 = new Person;
    p2->ParseFromString(buf2);
    cout << "Name:" << p2->name() << endl;
    cout << "ID:" << p2->id() << endl;
    for(int i = 0; i < p2->phones_size(); ++i) {
        cout << "Type:" << p2->phones(i).type()  << endl;
        cout << "Phone:" << p2->phones(i).number() << endl;
    }

    ofstream f("mybinary", ios_base::out | ios_base::binary);
    f << s;

    close(sk);
}
