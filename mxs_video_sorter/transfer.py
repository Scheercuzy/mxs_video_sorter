import logging
import progressbar
import shutil
import time
import threading
import os

logger = logging.getLogger('main')


def transferer(config, match_queue):
	logger.info("Transferer Running")

	global counter
	counter = 0
	full_queue_size = match_queue.qsize()

	if config.args.transfer and not config.args.review:
		logger.debug("Progress Bar thread started")
		bar = pbar_widgets(full_queue_size)
		_pbar_thread = threading.Thread(target=_pbar_run, args=(bar,), daemon=True)
		_pbar_thread.start()

	while True:
		counter += 1

		if match_queue.qsize() == 0:
			if _pbar_thread.is_alive():
				bar.finish()
			logger.debug("end of match queue")
			break

		fse = match_queue.get()

		if config.args.review:
			logger.log(15, "{} --> {}".format(fse.vfile.filename, fse.transfer_to))
			input("({} of {}) Press Enter to continue".format(counter, full_queue_size))
			continue

		if not config.args.transfer:
			logger.warning("Nothing was transfered because argument '-t' wasn't called")
			break

		logger.info("Working on {}".format(fse.vfile.filename))

		copy(config, fse)

		bar.update(counter)

	logger.info("Transferer Done")


def copy(config, fse):
	logger.debug("copying: '{}' to: '{}'".format(fse.vfile.filename, fse.transfer_to))
	shutil.copy(fse.vfile.abspath, fse.transfer_to)
	if not os.path.exists(os.path.join(fse.transfer_to, fse.vfile.filename)):
		logger.critical("The file {} was copied but doesn't exist in copied location".format(fse.vfile.filename))
		raise Exception("The file {} was copied but doesn't exist in copied location".format(fse.vfile.filename))
	logger.info("COPIED")
	if config.args.prevent_delete:
		return
	if fse.isdir:
		shutil.rmtree(fse.path_to_fse)
	else:
		os.remove(fse.path_to_fse)
	logger.info("DELETED FROM Input Folder")


def pbar_widgets(full_queue_size):
	widgets = [
		progressbar.AnimatedMarker(),
		" ",
		progressbar.Percentage(),
		' (',
		progressbar.SimpleProgress(),
		') ',
		progressbar.Bar(marker='=', left='[', right=']', fill='-'),
		progressbar.Timer(format=' %(elapsed)s')
	]
	return progressbar.ProgressBar(widgets=widgets, max_value=full_queue_size)


def _pbar_run(bar):
	while True:
		bar.update(counter)
		time.sleep(2)