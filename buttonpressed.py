import argparse
import datetime
import glob
import os
import pyPdf
import sane

def getNextDocNr(d):
    return (sorted([int(os.path.splitext(os.path.basename(i))[0]) for i in glob.glob(r'%s/*.pdf' % d)]) or [-1])[-1] + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Process scanbuttond input events.', formatter_class = argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('pages_dir', metavar = 'DIR', help = 'the directory to store the scanned pages before merging them together')
    parser.add_argument('documents_dir', metavar = 'DIR', help = 'the directory to store the merged documents to')

    parser.add_argument('page_scan_button', metavar = 'N', type = int, help = 'the button number to be pressed for scanning')
    parser.add_argument('document_button', metavar = 'N', type = int, help = 'the button number to be pressed for merging')

    parser.add_argument('button_number', metavar = 'N', type = int, help = 'the number of the button pressed')
    parser.add_argument('device_name', metavar = 'NAME', help = 'the name of the scanner device')

    parser.add_argument('--resolution', metavar = 'N', type = int, help = 'the scanner resolution', default = 300)
    parser.add_argument('--scanmode', metavar = 'MODE', help = 'the scan mode', default = 'color')
    parser.add_argument('--tsformat', metavar = 'FORMAT', help = 'the format of the timestamp', default = 'scan_%Y_%m_%d_%H_%M_%S')

    args = parser.parse_args()

    if args.button_number == args.page_scan_button:
        sane.init()

        s = sane.open([i for i in sane.get_devices() if i[0] == args.device_name][0][0])
        s.mode = args.scanmode
        s.resolution = args.resolution
        s.br_x=640. ; s.br_y=480.

        fName = r'%s/%d.pdf' % (args.pages_dir, getNextDocNr(args.pages_dir))
        s.scan().save(fName)

    elif args.button_number == args.document_button:
        output = pyPdf.PdfFileWriter()

        for i in glob.glob(r'%s/*.pdf' % args.pages_dir):
            output.addPage(pyPdf.PdfFileReader(file(i, 'rb')).getPage(0))
            os.remove(i)

        fName = r'%s/%s.pdf' % (args.documents_dir, datetime.datetime.now().strftime(args.tsformat))
        output.write(file(fName, 'wb'))
