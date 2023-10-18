#include <chrono>
#include <iostream>
#include <mutex>
#include <thread>

using namespace std;

int sum = 0;
mutex m;

void f() {
    for (int i = 0; i < 10 * 1000 * 1000; ++i) {
        m.lock();
        ++sum;
        m.unlock(); // unlock()을 하지 않으면 누구든 접근하지 못함
        // unique_lock<mutex> ul(m);
        // 위의 경우 ul을 사용하지 않으면 그냥 생성자만 호출하고 끝내는 것과 다를 게 없음
        // ul(m)에서 ul을 빼먹지 않도록 주의
    }
}

int main() {
    thread t(f);
    for (int i = 0; i < 10 * 1000 * 1000; ++i) {
        m.lock();
        ++sum;
        m.unlock();
    }
    t.join();
    cout << "Sum: " << sum << endl;
}
