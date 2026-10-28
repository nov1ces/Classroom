#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef struct { int number; char name[30]; char major[30]; } Student_info;
int main(void) {
    Student_info rows[6] = {0}, stu = {0};
    for (int i = 0; i < 6; ++i) rows[i].number = i;
    FILE *fp = tmpfile(); assert(fp != NULL);
    assert(fwrite(rows, sizeof(Student_info), 6, fp) == 6);
    assert(fseek(fp, 5L * sizeof(Student_info), SEEK_SET) == 0);
    assert(fread(&stu, sizeof(Student_info), 1, fp) == 1);
    assert(stu.number == 5); fclose(fp);
    fp = tmpfile(); assert(fp != NULL);
    for (int i = 0; i < 10000; ++i) assert(fputs("Hello world!", fp) >= 0);
    assert(ftell(fp) == 120000L);
    assert(fseek(fp, 16L, SEEK_SET) == 0 && fgetc(fp) == 'o');
    fclose(fp);
    printf("结构大小=%zu，第5号记录=%d，文本长度=120000，第16字节=o\n",sizeof(Student_info),stu.number);
}
