#!/usr/bin/env python3

"""Creates an archive in Simple Archive Format for batch import into DSpace."""

import csv
import os
import os.path
import shutil
import xml.etree.ElementTree as ET


class CreateArchive():
    """Placeholder."""

    def __init__(self, gs):
        """Placeholder."""
        self.csv_path = gs.csv_path
        self.bit_path = gs.bit_path
        self.archive_path = gs.archive_path
        self.create_zip = gs.create_zip
        self.split_zip = gs.split_zip
        self.zip_size = int(gs.zip_size)
        self.zip_unit = gs.zip_unit
        self.create_license = gs.create_license
        self.license_file = gs.license_file
        self.license_bundle = gs.license_bundle
        self.license_text = gs.license_text
        self.restrict_access = gs.restrict_access
        self.group_name = gs.group_name
        self.saf_folder_list = []

    def new_dir(self, saf_dir, row_num):
        """Create new directory for each DSpace record."""
        os.makedirs(os.path.join(saf_dir, ('item_{}'.format(row_num))))

    def change_dir(self, saf_dir, row_num):
        """Change current working directory to newly created directory."""
        os.chdir(os.path.join(saf_dir, ('item_{}'.format(row_num))))

    def write_license(self, contents_file):
        """Placeholder."""
        contents_file.write('{}    bundle:{}'.format(self.license_file, self.license_bundle))
        with open('{}'.format(self.license_file), 'w', encoding='utf-8') as license:
            license.write('{}'.format(self.license_text))

    def write_contents_file(self, data):
        """Create contents file with file names and copy files to directory."""
        with open('contents', 'a', encoding='utf-8') as contents_file:
            for csv_file_name in data.split('||'):
                if self.restrict_access:
                    contents_file.write('{}' '\t' 'group:{}' '\n'.format(csv_file_name, self.group_name))
                else:
                    contents_file.write('{}' '\n'.format(csv_file_name))
                for dirpath, dirnames, filenames in os.walk(self.bit_path):
                    for fname in filenames:
                        if csv_file_name == fname:
                            shutil.copy2(os.path.join(dirpath, fname), '.')
            if self.create_license:
                self.write_license(contents_file)

    def write_dc_metadata(self, header_split, data_split):
        """Write metadata to dublin core file."""
        for value in data_split:
            dc_value = ET.Element('dcvalue')
            dc_value.attrib['element'] = header_split[1]
            if len(header_split) == 3:
                dc_value.attrib['qualifier'] = header_split[2]
            dc_value.text = value
            if os.path.isfile('dublin_core.xml'):
                with open('dublin_core.xml', 'a', encoding='utf-8') as dc_file:
                    dc_file.write('  {}' '\n'.format(
                        str(ET.tostring(dc_value, encoding='utf-8'), 'utf-8')))
            else:
                with open('dublin_core.xml', 'w', encoding='utf-8') as dc_file:
                    dc_file.write('<?xml version="1.0" encoding="UTF-8"?>' '\n')
                    dc_file.write('<dublin_core>' '\n')
                    dc_file.write('  {}' '\n'.format(
                        str(ET.tostring(dc_value, encoding='utf-8'), 'utf-8')))

    def write_schema_metadata(self, schema_file, header_split, data_split, schema):
        """Write metadata to other schema file."""
        for value in data_split:
            dc_value = ET.Element('dcvalue')
            dc_value.attrib['element'] = header_split[1]
            if len(header_split) == 3:
                dc_value.attrib['qualifier'] = header_split[2]
            dc_value.text = value
            if os.path.isfile(schema_file):
                with open(schema_file, 'a', encoding='utf-8') as dc_file:
                    dc_file.write('  {}' '\n'.format(
                        str(ET.tostring(dc_value, encoding='utf-8'), 'utf-8')))
            else:
                with open(schema_file, 'a', encoding='utf-8') as dc_file:
                    dc_file.write('<?xml version="1.0" encoding="UTF-8"?>' '\n')
                    dc_file.write('<dublin_core schema="{}">' '\n'.format(schema))
                    dc_file.write('  {}' '\n'.format(
                        str(ET.tostring(dc_value, encoding='utf-8'), 'utf-8')))

    def write_closing_tag(self):
        """Write closing tag to each xml file."""
        for file_name in os.listdir('.'):
            if file_name.endswith('xml'):
                with open(file_name, 'a', encoding='utf-8') as dc_file:
                    dc_file.write('</dublin_core>' '\n')

    def create_files(self, saf_dir, row_num, headers, row):
        """Write CSV metadata to appropriate files."""
        self.new_dir(saf_dir, row_num)
        self.change_dir(saf_dir, row_num)
        for header, data in zip(headers, row):
            header_split = header.split('.')
            schema = header_split[0]
            data_split = data.split('||')
            schema_file = 'metadata_{}.xml'.format(header_split[0])
            if data:
                if header_split[0] == 'filename':
                    self.write_contents_file(data)
                elif header_split[0] == 'dc':
                    self.write_dc_metadata(header_split, data_split)
                else:
                    self.write_schema_metadata(schema_file, header_split, data_split, schema)
        self.write_closing_tag()

    def open_csv(self):
        """Placeholder."""
        saf_folder_name = 'SimpleArchiveFormat'
        self.saf_folder_list.append(saf_folder_name)
        saf_dir = os.path.join(self.archive_path, saf_folder_name)
        with open(self.csv_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            row_num = 1
            for row in reader:
                self.create_files(saf_dir, row_num, headers, row)
                row_num += 1

    def open_csv_split(self):
        """Placeholder."""
        with open(self.csv_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            headers = next(reader)
            saf_folder_number = 1
            row_num = 1
            total_size = 0
            if self.zip_unit == 'MB':
                zip_size = self.zip_size * 1000000
            else:
                zip_size = self.zip_size * 1000000000
            for row in reader:
                saf_folder_name = 'SimpleArchiveFormat{}'.format(saf_folder_number)
                saf_dir = os.path.join(self.archive_path, saf_folder_name)
                self.create_files(saf_dir, row_num, headers, row)
                files = [f for f in os.listdir('.') if os.path.isfile(f)]
                for f in files:
                    total_size += os.path.getsize(f)
                if total_size >= zip_size:
                    saf_folder_number += 1
                    saf_dir = os.path.join(self.archive_path, saf_folder_name)
                    cur_dir = os.getcwd()
                    cur_folder = os.path.split(cur_dir)[-1]
                    new_dir = os.path.join(saf_dir, cur_folder)
                    os.chdir(saf_dir)
                    shutil.move(cur_dir, new_dir)
                    total_size = 0
                    files = [f for f in os.listdir('.') if os.path.isfile(f)]
                    for f in files:
                        total_size += os.path.getsize(f)
                if saf_folder_name not in self.saf_folder_list:
                    self.saf_folder_list.append(saf_folder_name)
                row_num += 1

    def zip_archive(self):
        """Placeholder."""
        dst_folder_list = os.listdir(self.archive_path)
        for folder in dst_folder_list:
            folder_path = os.path.join(self.archive_path, folder)
            if folder in self.saf_folder_list and os.path.isdir(folder_path):
                shutil.make_archive(folder_path, 'zip', folder_path)
