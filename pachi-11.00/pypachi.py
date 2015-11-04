from cffi import FFI
from urlparse import urlparse, parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

ffi = FFI()
ffi.cdef("""
      //dummy declarations
      typedef int coord_t;
      typedef int stone;
      struct board;
      struct engine;
      struct time_info;

      struct move {
      	coord_t coord;
      	stone color;
      };

      struct engine* engine_uct_init(char *arg, struct board *b);
      struct board* board_init(char *fbookfile);
      char * uct_notify_play(struct engine *e, struct board *b, struct move *m, char *enginearg);

      void uct_done(struct engine *e);

      void board_print_stderr(struct board *board);
      int board_play(struct board *board, struct move *m);
      coord_t * uct_genmove(struct engine *e, struct board *b, struct time_info *ti, stone color, bool pass_all_alive);

      struct time_info* time_info_init(void);
      void board_resize(struct board *board, int size);
      void board_clear(struct board *board);

      int printf(const char *format, ...);
""")

#while True:
#   reply = C.uct_genmove(engine, board, t_black, 1, 0)
#   move.coord = reply[0]
#   move.color = 1
#   reply = C.uct_notify_play(engine, board, move, null_cstr)
#   ret = C.board_play(board, move)
#   C.board_print_stderr(board)
#
#   reply = C.uct_genmove(engine, board, t_white, 1, 0)
#   move.coord = reply[0]
#   move.color = 2
#   reply = C.uct_notify_play(engine, board, move, null_cstr)
#   ret = C.board_play(board, move)
#   C.board_print_stderr(board)

move = ffi.new("struct move*")
C = None
try:
   import os
   print os.path.exists(os.path.join(os.getcwd(), "libpachi.so"))
   C = ffi.dlopen("libpachi.so")         # loads the entire C namespace
except Exception as e:
   print e
   print("trying osx")
if C == None:
   C = ffi.dlopen("libpachi.dylib")      # loads the entire C namespace
null_cstr = ffi.cast("char*", 0)
board = C.board_init(null_cstr)
size = 9
C.board_resize(board, size)
C.board_clear(board)
engine = C.engine_uct_init(null_cstr, board)
t_black = C.time_info_init()
t_white = C.time_info_init()

class myHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      self.do_POST()
   def do_POST(self):
      self.log_message("do_POST %s" % self.path)
      self.send_response(200)
      self.send_header('Content-type','application/json')
      self.end_headers()
      q = parse_qs(urlparse(self.path).query)
      if q.has_key("method"):
         self.log_message("do_GET method:%s" % (q["method"][0]))
         if q["method"][0] == "docs":
            self.docs(q)
         elif q["method"][0] == "setmove":
            self.setmove(q)
         elif q["method"][0] == "getmove":
            self.getmove(q)
         elif q["method"][0] == "newboard":
            self.newboard(q)
         else:
            self.wfile.write('{"result":"failed"}')
      else:
         self.wfile.write('{"result":"failed"}')
      return
   def setmove(self, q):
      global engine
      global size
      global t_black
      global t_white
      global C
      global move
      self.log_message("self.setmove %s" % q)
      if q["color"][0] == "black":
         move.color = 1
      else:
         move.color = 2
      x = int(q["x"][0])
      y = int(q["y"][0])
      move.coord = (x + 1) + (size * (y + 1))
      reply = C.uct_notify_play(engine, board, move, null_cstr)
      ret = C.board_play(board, move)
      C.board_print_stderr(board)
      if ret == -1:
         self.wfile.write('{"result":"failed"}')
      else:
         self.wfile.write('{"result":"ok"}')
      return
   def getmove(self, q):
      global engine
      global size
      global t_black
      global t_white
      global C
      global move
      self.log_message("self.getmove %s" % q)
      time = None
      if q["color"][0] == "black":
         time = t_black
         move.color = 1
      else:
         time = t_white
         move.color = 2
      reply = C.uct_genmove(engine, board, time, 1, 0)
      move.coord = reply[0]
      ret = C.board_play(board, move)
      C.board_print_stderr(board)
      y = int(move.coord / size)
      x = move.coord - size * y
      x = x - 1
      y = y - 1
      if ret == -1:
         self.wfile.write('{"result":"failed"}')
      else:
         self.wfile.write('{"result":"ok", "x":"%s", "y":"%s"}' % (x,y))
      return
   def newboard(self, q):
      global engine
      global size
      global t_black
      global t_white
      global C
      self.log_message("self.newboard %s" % q)
      size = int(q["size"][0])
      assert(size >= 9 and size <= 19)
      C.board_resize(board, size)
      C.board_clear(board)
      C.uct_done(engine)
      engine = C.engine_uct_init(null_cstr, board)
      t_black = C.time_info_init()
      t_white = C.time_info_init()
      self.wfile.write('{"result":"ok"}')
   def docs(self, q):
      self.log_message("self.docs %s" % q)
      self.wfile.write("""
                       {"query":"?method=getmove&color=black", "response":{"result":"ok","x":"1","y":"2"}
                       ,"query":"?method=setmove&color=white&x=1&y=2", "response":{"result":"ok"}
                       ,"query":"?method=newboard&size=9", "response":{"result":"ok"}
                       }""")
class http_server:
    def __init__(self):
        self.server = HTTPServer(('', 8080), myHandler)
        self.server.serve_forever()

if __name__ == '__main__':
    http_server()
