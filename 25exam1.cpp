// 1. 日志压缩
// 题目描述 服务器的日志文件中存储了一连串重复字符. 为了节省空间, 采用一种简单的压缩格式对其进行压缩.
//  压缩格式为: [字符][重复次数]. 如果重复次数为 1, 则不显示重复次数. 例如: EEEerr 压缩为 E3er2.
//   请编写程序, 压缩一个字符串. 注意区分大小写.

// 输入描述 一行, 一个字符串 (长度不超过 100, 仅包含大小写英文字母) .

// 输出描述 一行, 表示压缩后的字符串.

// 样例输入
#include<iostream>
#include<cstdio>
using namespace std;
int main()
{
    char m;
    int t=0;
    char i[100];
    while((m=getchar())!='\n'){
        i[t]=m;
        t++;
    }
    int r=0;
    for(int j=0;j<t;j++){
        if(i[j]!=i[j+1]) {
        if((j+1-r)>1) cout<<i[j]<<j+1-r;
        else cout<<i[j];
        r=j+1;
    }
    }
    return 0;
}