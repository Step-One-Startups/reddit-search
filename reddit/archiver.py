from datetime import datetime
import logging
from collections.abc import Iterable, Iterator
from reddit.bdfr.archive_entry.base_archive_entry import BaseArchiveEntry
from reddit.bdfr.archive_entry.comment_archive_entry import CommentArchiveEntry
from reddit.bdfr.archive_entry.submission_archive_entry import SubmissionArchiveEntry
from reddit.bdfr.connector import RedditConnector
import prawcore
import praw.models
import json
from time import sleep
from pathlib import Path
from typing import Union
from reddit.bdfr.exceptions import ArchiverError


from reddit.configuration import Configuration


logger = logging.getLogger(__name__)


class Archiver(RedditConnector):
    def __init__(self, args: Configuration, logging_handlers: Iterable[logging.Handler] = ()):
        super(Archiver, self).__init__(args, logging_handlers)

    def download(self):
        self.entries = []
        for generator in self.reddit_lists:
            try:
                for submission in generator:
                    try:
                        if (submission.author and submission.author.name in self.args.ignore_user) or (
                            submission.author is None and "DELETED" in self.args.ignore_user
                        ):
                            logger.debug(
                                f"Submission {submission.id} in {submission.subreddit.display_name} skipped due to"
                                f" {submission.author.name if submission.author else 'DELETED'} being an ignored user"
                            )
                            continue
                        if submission.id in self.excluded_submission_ids:
                            logger.debug(f"Object {submission.id} in exclusion list, skipping")
                            continue
                        logger.debug(f"Attempting to archive submission {submission.id}")
                        self.write_entry(submission)
                    except prawcore.PrawcoreException as e:
                        logger.error(f"Submission {submission.id} failed to be archived due to a PRAW exception: {e}")
            except prawcore.PrawcoreException as e:
                logger.error(f"The submission after {submission.id} failed to download due to a PRAW exception: {e}")
                logger.debug("Waiting 60 seconds to continue")
                sleep(60)
        self._write_all_entries_to_disk()
        return self.entries
    

    @staticmethod
    def _pull_lever_entry_factory(praw_item: Union[praw.models.Submission, praw.models.Comment]) -> BaseArchiveEntry:
        if isinstance(praw_item, praw.models.Submission):
            return SubmissionArchiveEntry(praw_item)
        elif isinstance(praw_item, praw.models.Comment):
            return CommentArchiveEntry(praw_item)
        else:
            raise ArchiverError(f"Factory failed to classify item of type {type(praw_item).__name__}")

    def write_entry(self, praw_item: Union[praw.models.Submission, praw.models.Comment]):
        if self.args.comment_context and isinstance(praw_item, praw.models.Comment):
            logger.debug(f"Converting comment {praw_item.id} to submission {praw_item.submission.id}")
            praw_item = praw_item.submission
        archive_entry = self._pull_lever_entry_factory(praw_item)
        if self.args.format == "json":
            self._save_entry_json(archive_entry)
        else:
            raise ArchiverError(f"Unknown format {self.args.format} given")
        logger.info(f"Record for entry item {praw_item.id} written to disk")


    def _save_entry_json(self, entry: BaseArchiveEntry):
        self.entries.append(entry.compile())


    def _write_all_entries_to_disk(self):
        if not len(self.entries):
            logger.debug("No entries to write")
            return
        content = json.dumps(self.entries)
        current_time = datetime.now().strftime("%H-%M-%S")
        file_path = Path(self.download_directory, f"{current_time}_{len(self.entries)}.json")
        with Path(file_path).open(mode="w", encoding="utf-8") as file:
            logger.debug(
                f"Writing {len(self.entries)} entries to file in json"
                f" format at {file_path}"
            )
            file.write(content)
