#define __FUTILS_FREESTD_NOT_STDC__
#include <freestd.cpp>
#include <stub/plt_stub.cpp>
#include <freestd/stdio.h>
#include <fnet/util/http/header.h>
extern "C" {
#include <libs/wasm/ipc.h>
}
__attribute__((export_name("main")))
extern "C" int main() {
    char buf[100];
    futils_snprintf(buf,100,"Hello, World!\n");
    auto service = ipc_lookup("echo");
    struct message m;
    m.type = ECHO_MSG;
    futils_memcpy(m.echo.data, buf, 100);
    m.echo.data_len = futils_strlen(buf);
    ipc_call(service, &m);
    auto pb= futils::helper::CharVecPushbacker(buf,100);
    auto err= ::futils::http::header::render_request(pb, "GET", "/index.html",[](auto&& render){
        render("Host", "localhost");
        render("User-Agent", "WasmOS futils");
    });
    return 0;
}

