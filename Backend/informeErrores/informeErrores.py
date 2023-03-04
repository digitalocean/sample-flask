from datetime import datetime
def reporte(exceptionn,origenError):
    f = open("informeErrores/informe de errores.txt", "a")
    f.write(str(datetime.now()))
    f.write("\n")
    f.write(origenError)
    f.write("\n")
    f.write(str(exceptionn))
    f.write("\n\n")
    f.close()
