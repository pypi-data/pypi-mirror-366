import weakref
from locator_parser.common import Reader, Writer


class FileWriter(Writer):

    def __init__(self, file_path):
        self.__path = file_path

        super(FileWriter, self).__init__()

    def flush(self):
        with open(self.__path, "w") as fout:
            for line in self.lines:
                if line[-1:] != "\n":
                    line += "\n"

                fout.write(line)


class PrintWriter(Writer):

    def flush(self):
        print("\n".join(self.lines))


class FileReader(Reader):

    def __init__(self, file_path):
        self.iterable_object = open(file_path.replace('"', ""), "r")
        self.__finalizer = weakref.finalize(self, lambda x: x.close(), self.iterable_object)

        super(FileReader, self).__init__()


class LinesReader(Reader):

    def __init__(self, lines):
        self.iterable_object = lines.split("\n")

        super(LinesReader, self).__init__()
