#include "trace_dat.h"
#include<iostream>
#include<string.h>

trace_dat::trace_dat(std::string filename)
{
    _filename_=filename;
    _datfile_.open(filename);
}

trace_dat::~trace_dat()
{
    _datfile_.close();
}

std::string trace_dat::test()
{
    return "hello";
}


//获取统计的事件名
std::vector<std::string> trace_dat::events()
{
    using namespace std;
    vector<string> et;
    et.push_back("events");
    
    return et;
}

int get_seg(char *data,struct dat_idseg_data *t)
{
    if (strncmp(data,"name: ",6)!=0){
        return 0;
    }
    int i=6;
    while(data[i]!='\n'){
    }
}


int main()
{
    using namespace std;
   
    ifstream fin;
    fin.open("../test.dat",ios::binary);
    struct dat_struct *tmp=new struct dat_struct;
    fin.read((char*)tmp,sizeof(struct dat_struct));
    
    //读取段
    while()


    fin.close();
    return 0;
}