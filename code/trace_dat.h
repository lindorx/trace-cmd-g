#include<string>
#include<fstream>
#include<vector>


typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;

#pragma pack(1)
struct dat_header_page{
    char name[11];
    char null;
    uint8 data_size;
    uint8 null1[7];
    char data[0xcd];
};

struct dat_header_event{
    char name[12];
    char null;
    uint8 data_size;
    uint8 null1[7];
    char data[0xcd];
};

struct dat_idseg_data{
    char *name;
    int id;
    char *format;
    char *print_fmt;
};

//记录每一段数据信息
struct dat_idseg{
    uint32 num_0x0f;
    uint32 size;
    uint32 null;
    char *data;
};

struct dat_struct{
    uint16 magic_number;
    char Dtracing[8];
    char null1[7];
    struct dat_header_page header_page;
    struct dat_header_event header_event;
};

//本代码用来解析dat文件
class trace_dat
{
    public:
    trace_dat(std::string filename);//构造函数
    ~trace_dat();
    std::string test();
    std::vector<std::string> events();//事件名
    

    private:
    std::string _filename_;
    std::ifstream _datfile_;
};


#pragma pack()