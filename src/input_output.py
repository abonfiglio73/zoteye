from __future__ import annotations
from typing import TYPE_CHECKING
from logger import LogLevel
import pickle
import gzip
import os
import io

if TYPE_CHECKING:
    from main import ZotEyeApp


class InputOutput:

    def __init__(self, app: ZotEyeApp):
        self.app = app

    def save_ngram_index(
        self,
        pdf_ngram_index: dict,
        pickle_path: str,
        chunk_size: int = 10,
        progress_interval: int = 5,
    ):

        items = list(pdf_ngram_index.items())
        total = len(items)
        self.app.logger.log(
            f"{self.app.translator.gettext('started_saving')}: {pickle_path}",
            LogLevel.SAVE,
        )

        with gzip.open(pickle_path, "wb") as f:
            # Write the total item count first
            pickle.dump(total, f, protocol=pickle.HIGHEST_PROTOCOL)
            buffer_count = 0

            # Serialize in small dict chunks
            for i in range(0, total, chunk_size):
                chunk = dict(items[i : i + chunk_size])
                pickle.dump(chunk, f, protocol=pickle.HIGHEST_PROTOCOL)
                buffer_count += len(chunk)

                # Periodic progress update
                if buffer_count % progress_interval == 0:
                    percent = int((i + chunk_size) / total * 100)
                    size_now = os.path.getsize(pickle_path)
                    self.app.logger.progress(percent, size_now)

        self.app.logger.progress_done()

        self.app.logger.log(
            f"{self.app.translator.gettext('completed_saving')}: {pickle_path} ({os.path.getsize(pickle_path) / 1024:.1f} KB)",
            LogLevel.SUCCESS,
        )

    def load_ngram_index(
        self,
        pickle_path: str,
        chunk_size: int = 1024 * 1024,
    ) -> dict:

        self.app.logger.log(
            f"{self.app.translator.gettext('started_loading')}: {pickle_path}",
            LogLevel.FOLDER,
        )

        file_size = os.path.getsize(pickle_path)
        bytes_read = 0
        buffer = bytearray()

        # Buffered read to provide progressive feedback in the UI
        with open(pickle_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                buffer.extend(chunk)
                bytes_read += len(chunk)

                percent = int(bytes_read / file_size * 100)
                self.app.logger.progress(percent, bytes_read)

        # Decompress and rebuild the dictionary from pickled chunks
        decompressed = gzip.decompress(buffer)
        loaded_items = {}
        bio = io.BytesIO(decompressed)

        # Read total
        total_expected = pickle.load(bio)  # value not directly used

        while True:
            try:
                chunk = pickle.load(bio)
                if isinstance(chunk, dict):
                    loaded_items.update(chunk)
            except EOFError:
                break

        self.app.logger.progress_done()
        self.app.logger.log(
            f"{self.app.translator.gettext('completed_loading').format(items=len(loaded_items))}",
            LogLevel.SUCCESS,
        )

        return loaded_items
