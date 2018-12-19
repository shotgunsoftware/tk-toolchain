from sgtk.platform import Engine


class TestEngine(Engine):

    def _emit_log_message(self, handler, record):
        print(handler.format(record))
