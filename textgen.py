import argparse
import csv as _csv
import json as _json
import click
from jinja2 import Environment, FileSystemLoader


class TemplateEngine:
    def __init__(self, template_name, template_folder="."):
        self.env = Environment(loader=FileSystemLoader(template_folder))
        self.template = self.env.get_template(template_name)

    def render(self, data):
        return self.template.render(data)


class DataLoader:
    def __init__(self, filename, encoding='utf-8'):
        self.filename = filename
        self.encoding = encoding

    def __iter__(self):
        yield from self.pick()

    def pick(self):
        raise NotImplementedError()


class CsvLoader(DataLoader):
    def pick(self):
        with open(self.filename, encoding=self.encoding, newline="") as f:
            csv = _csv.DictReader(f)
            yield from csv


class JsonLoader(DataLoader):
    def pick(self):
        with open(self.filename, encoding=self.encoding) as f:
            json = _json.load(f)
            if not isinstance(json, list):
                raise TypeError("this JSON data is not start list.")
            yield from json


DATA_LOADER_CLASSES = {
    "csv": CsvLoader,
    "json": JsonLoader,
}


def createDataLoader(loader_str, filename):
    try:
        return DATA_LOADER_CLASSES[loader_str.lower()](filename)
    except KeyError as e:
        raise


@click.command()
@click.option("--template", "-t", default="template.txt", help="template name")
@click.option("--datafile", "-f", default="data.csv", help="data file")
@click.option("--dataformat", default="csv", help="data format")
@click.option("--onefile", is_flag=True, help="data format")
def main(template, datafile, dataformat, onefile):
    template = TemplateEngine(template)
    loader = createDataLoader(dataformat, datafile)

    if onefile:
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(template.render({"data": loader}))
    else:
        for i, d in enumerate(loader):
            with open("output{:04d}.txt".format(i), "w", encoding="utf-8") as f:
                f.write(template.render({"data": [d]}))


if __name__ == "__main__":
    main()
