#include<iostream>

//对类进行测试
class val_test
{
private:
    int num;
    int n;
public:
val_test(int number);
int get_num();
void set_num(int num);
~val_test();
};


val_test::val_test(int number)
{
    num=number;
    n=20;
}

val_test::~val_test()
{
}


int val_test::get_num()
{
    return n*num;
}

void val_test::set_num(int num)
{
    this->num=num;
}

using namespace std;
int main()
{
    val_test t(2);
    cout<<t.get_num();
    
    return 0;
}