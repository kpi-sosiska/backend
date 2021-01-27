#!/usr/bin/python

import asyncio

import parser
import presenter


def main():
    import argparse

    argparser = argparse.ArgumentParser(description='Парсит rozklad.org.ua, сохраняет группы и преподов')
    argparser.add_argument('--force-update', '-f', action='store_true', dest="force_update",
                           help='Перезаписывать существующие записи')

    args = argparser.parse_args()

    asyncio.get_event_loop().run_until_complete(parser.main(args.force_update))

    # presenter.FilePresenter.present()
    presenter.CSVPresenter.present()


if __name__ == '__main__':
    main()
