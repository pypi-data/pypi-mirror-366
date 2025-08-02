from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path
from sisc.cli import SisCCLI
from os.path import join


def __run_fingerprint_uniform_move_fn(xml_path, base_output_path):
    for size in range(20, 105, 5):
        output_path = join(base_output_path, f'distance_{size}', 'fingerprint')
        Path(output_path).mkdir(parents=True, exist_ok=True)
        arguments = ['fingerprint', 'uniform', xml_path, output_path, '--move-notes', '--add-quotation-marks', '--distance', str(size)]
        SisCCLI.main(arguments)


def __run_fingerprint_uniform_no_move_fn(xml_path, base_output_path):
    for size in range(20, 105, 5):
        output_path = join(base_output_path, f'distance_{size}', 'fingerprint')
        Path(output_path).mkdir(parents=True, exist_ok=True)
        arguments = ['fingerprint', 'uniform', xml_path, output_path, '--no-move-notes', '--add-quotation-marks', '--distance', str(size)]
        SisCCLI.main(arguments)


def __run_align(txt_path, base_fingerprint_path, base_output_path):
    for size in range(20, 105, 5):
        fingerprint_path = join(base_fingerprint_path, f'distance_{size}', 'fingerprint')
        output_path = join(base_output_path, f'distance_{size}', 'aligned')
        Path(output_path).mkdir(parents=True, exist_ok=True)
        arguments = ['align', txt_path, fingerprint_path, output_path, '--max-num-processes', '60']
        SisCCLI.main(arguments)


def main():
    argument_parser = ArgumentParser()

    subparsers = argument_parser.add_subparsers(dest='command')
    subparsers.required = True

    parser_fingerprint = subparsers.add_parser('fingerprint')
    parser_fingerprint.add_argument('xml_path', metavar='xml-path')
    parser_fingerprint.add_argument('output_path', metavar='output-path')
    parser_fingerprint.add_argument('--move-notes', dest='move_notes', required=True, action=BooleanOptionalAction)

    parser_align = subparsers.add_parser('align')
    parser_align.add_argument('txt_path', metavar='txt-path')
    parser_align.add_argument('fingerprint_path', metavar='fingerprint-path')
    parser_align.add_argument('output_path', metavar='output-path')

    args = argument_parser.parse_args()

    if args.command == 'fingerprint':
        xml_path = args.xml_path
        output_path = args.output_path
        move_notes = args.move_notes

        if move_notes:
            __run_fingerprint_uniform_move_fn(xml_path, output_path)
        else:
            __run_fingerprint_uniform_no_move_fn(xml_path, output_path)

    elif args.command == 'align':
        txt_path = args.txt_path
        fingerprint_path = args.fingerprint_path
        output_path = args.output_path

        __run_align(txt_path, fingerprint_path, output_path)


if __name__ == '__main__':
    main()