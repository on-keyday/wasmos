#include <freestd.cpp>
#include <stub/plt_stub.cpp>
#include <freestd/stdio.h>
#include <libs/wasm/ipc.h>

__attribute__((export_name("main")))
extern "C" int main() {
    char buf[100];
    futils_snprintf(buf,100,"Hello, World!\n");
    ipc_lookup("");
    return 0;
}

