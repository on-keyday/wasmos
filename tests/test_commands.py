"""

Test shell server commands.

"""

import http
import http.server
import threading

def test_echo(run_wasmos):
    r = run_wasmos("echo howdy")
    assert "howdy" in r.log

def test_start(run_wasmos):
    r = run_wasmos("start hello")
    assert "Hello World!" in r.log

def test_hinavm(run_wasmos):
    r = run_wasmos("start hello_hinavm")
    assert "hinavm_server: pc=7: 123" in r.log
    assert "reply value: 42" in r.log

def test_ls(run_wasmos):
    r = run_wasmos("ls")
    assert "hello.txt" in r.log

def test_cat(run_wasmos):
    r = run_wasmos("cat hello.txt")
    assert "Hello World from HinaFS" in r.log

def test_write(run_wasmos):
    r = run_wasmos("write lfg.txt LFG; ls; cat lfg.txt")
    assert '[FILE] "lfg.txt"' in r.log
    assert '[shell] LFG' in r.log
    
def test_mkdir(run_wasmos):
    r = run_wasmos("mkdir new_dir; ls")
    assert '[DIR ] "new_dir"' in r.log

def test_delete_file(run_wasmos):
    r = run_wasmos("write lfg.txt LFG; delete lfg.txt; ls")
    assert '[FILE] "lfg.txt"' not in r.log

def test_delete_dir(run_wasmos):
    r = run_wasmos("mkdir new_dir; delete new_dir; ls")
    assert '[DIR ] "new_dir"' not in r.log

def test_shutdow(run_wasmos):
    r = run_wasmos("shutdown")
    assert "[shell] shutting down..." in r.log

def test_hinavm(run_wasmos):
    r = run_wasmos("start hello_hinavm")
    assert "hinavm_server: pc=7: 123" in r.log
    assert "reply value: 42" in r.log

def test_http(run_wasmos):
    class TeapotServer(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(418)
            self.end_headers()
            self.wfile.write("Hello HTTP!".encode("utf-8"))
    
    httpd = http.server.HTTPServer(("", 1234), TeapotServer)
    httpd_thread = threading.Thread(target=lambda: httpd.serve_forever(), daemon=True)
    httpd_thread.start()

    r = run_wasmos(
        "http http://10.0.2.100:1234/teapot",
        qemu_net0_options=["guestfwd=tcp:10.0.2.100:1234-tcp:127.0.0.1:1234"]
    )
    assert "Hello HTTP!" in r.log

    httpd.shutdown()
    httpd.server_close()
    httpd_thread.join()