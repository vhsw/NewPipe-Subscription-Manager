#!/usr/bin/env python3

import argparse
import sqlite3
import zipfile
from pathlib import Path
from urllib import request
from xml.dom import minidom


def create_path_obj(path, suffix=''):
    p = Path(path)
    if not p.exists():
        raise Exception(f'Wrong path {p}')
    str_path = str(p.resolve())
    if p.suffix.upper() != suffix.upper():
        raise Exception(f'File "{str_path}" must be {suffix.upper()} file')
    return p


def unpack_new_pipe_data(path):
    p = create_path_obj(path, '.ZIP')
    # Zipfile path-like objects handling must be fixed someday
    zip_ref = zipfile.ZipFile(str(p.resolve()), 'r')
    path_to_extract = p.parent.joinpath('.newpipe')
    zip_ref.extractall(path_to_extract)
    zip_ref.close()
    return path_to_extract


def open_db(path_to_db):
    # sqlite path-like objects handling must be fixed someday too
    conn = sqlite3.connect(str(path_to_db.joinpath('newpipe.db')))
    return conn


def update_db(conn, data):
    c = conn.cursor()
    current_subscriptions = [_[0] for _ in c.execute('SELECT url FROM subscriptions').fetchall()]
    new_subscriptions = [
        (s['service_id'], s['url'], s['name'], s['avatar_url'], s['subscriber_count'], s['description']) for s in data
        if s['url'] not in current_subscriptions]
    c.executemany(
        '''INSERT INTO subscriptions (service_id, url, name, avatar_url, subscriber_count, description)
           VALUES (?,?,?,?,?,?)''',
        new_subscriptions)
    conn.commit()


def resolve_data(url_list):
    data = []
    for num, url in enumerate(url_list):
        print(f'\rloading subscriptions... {num+1}/{len(url_list)}', end='\r')
        response = request.urlopen(url)
        xml_doc = minidom.parse(response)
        author = xml_doc.getElementsByTagName('author')[0]
        uri = author.getElementsByTagName('uri')[0].firstChild.nodeValue
        name = author.getElementsByTagName('name')[0].firstChild.nodeValue
        data.append(
            {'service_id': 0, 'url': uri, 'name': name, 'avatar_url': '', 'subscriber_count': 0,
             'description': ''})
    return data


def parse_oxml(path):
    p = create_path_obj(path, '.XML')
    xml_doc = minidom.parse(str(p.resolve()))
    item_list = xml_doc.getElementsByTagName('outline')
    return [s.attributes['xmlUrl'].value for s in item_list if 'xmlUrl' in s.attributes.keys()]


def pack_back_new_pipe_data(db_file_path, path_to_zip):
    with zipfile.ZipFile(str(path_to_zip.resolve()), 'w', zipfile.ZIP_DEFLATED) as myzip:
        name = db_file_path.name
        myzip.write(db_file_path.joinpath('newpipe.db'), 'newpipe.db')
        myzip.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Import subscriptions from subscription_manager.xml to NewPipe database')
    parser.add_argument('xml_path', action='store', type=str, nargs='?', default='',
                        help='Path to subscription_manager.xml file.\nYou can get it here: https://www.youtube.com/subscription_manager?action_takeout=1')
    parser.add_argument('db_path', action='store', type=str, nargs='?', default='',
                        help='Path to NewPipeData-*.zip\nYou can get optain it in NewPipe app navigating to Settings -> Content -> Export database')
    results = parser.parse_args()

    db_file_path = unpack_new_pipe_data(results.db_path)
    cursor = open_db(db_file_path)
    url_list = parse_oxml(results.xml_path)
    subscr_list = resolve_data(url_list)
    update_db(cursor, subscr_list)
    pack_back_new_pipe_data(db_file_path, create_path_obj(results.db_path, '.ZIP'))
    print('\nDone!')
