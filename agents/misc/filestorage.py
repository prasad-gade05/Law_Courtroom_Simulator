import os
import glob
import csv
import re
import datetime
import hashlib

def get_dateobj(datestr):
    """Convert a date string to a datetime.date object."""
    ds = re.findall(r'\d+', datestr)
    return datetime.date(int(ds[0]), int(ds[1]), int(ds[2]))


class FileStorage:
    def __init__(self, datadir):
        self.datadir = datadir

    def save_json(self, results, filepath):
        """Save JSON data to a file."""
        try:
            json_doc = results.decode('utf8')
            with open(filepath, mode='w', encoding='utf-8') as json_file:
                json_file.write(json_doc)
        except Exception as e:
            print(f"Error saving JSON to {filepath}: {e}")

    def exists(self, filepath):
        """Check if a file exists."""
        return os.path.exists(filepath)

    def exists_original(self, origpath):
        """Check if an original file exists."""
        return bool(glob.glob(f'{origpath}.*'))

    def get_keyword_path(self, keyword):
        """
        Create and return the directory path for a specific keyword.
        Normalizes keyword names to avoid invalid characters in directories.
        """
        sanitized_keyword = re.sub(r'[^\w\s]', '_', keyword).replace(" ", "_")
        keyword_hash = hashlib.md5(sanitized_keyword.encode()).hexdigest()
        keyword_dir = os.path.join(self.datadir, keyword_hash)
        os.makedirs(keyword_dir, exist_ok=True)
        return keyword_dir

    def get_docpath(self, basepath, docsource, publishdate):
        """
        Create and return the directory path for storing a document based on source and publish date.
        """
        datadir = os.path.join(basepath, docsource)
        os.makedirs(datadir, exist_ok=True)

        d = get_dateobj(publishdate)
        datadir = os.path.join(datadir, f'{d.year}')
        os.makedirs(datadir, exist_ok=True)

        docpath = os.path.join(datadir, f'{d}')
        os.makedirs(docpath, exist_ok=True)

        return docpath

    def get_json_orig_path(self, docpath, docid):
        """Get paths for JSON and original document storage."""
        jsonpath = os.path.join(docpath, f'{docid}.json')
        origpath = os.path.join(docpath, f'{docid}_original')
        return jsonpath, origpath

    def get_tocwriter(self, datadir):
        """
        Create a CSV writer for Table of Contents (TOC).
        """
        fieldnames = ['position', 'docid', 'date', 'court', 'title']
        tocfile = os.path.join(datadir, 'toc.csv')
        try:
            tochandle = open(tocfile, 'w', encoding='utf8')
            tocwriter = csv.DictWriter(tochandle, fieldnames=fieldnames)
            tocwriter.writeheader()
            return tocwriter
        except Exception as e:
            print(f"Error creating TOC file in {datadir}: {e}")
            raise
