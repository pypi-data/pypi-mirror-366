import os, shutil, glob
from pathlib import Path
import mimetypes
import chardet, codecs
from email.header import Header, decode_header, make_header
from mailbagit.models import Attachment
import mailbagit.helper.common as common
import html
import uuid

from mailbagit.loggerx import get_logger

log = get_logger()


def relativePath(mainPath, file):
    """
    Gets the relative path of an input file within the input directory structure
    Useful for getting the path of messages within an email account

    Parameters:
        mainPath (String): Parent or provided directory path
        file (String): Email file path

    Returns:
        String: emailFolder
    """

    fullPath = Path(mainPath).resolve()
    fullFilePath = Path(file).resolve()
    relPath = str(fullFilePath.relative_to(fullPath))
    if relPath == ".":
        return ""
    else:
        return relPath


def safely_decode(body_type, binary_text, encodings, errors):
    """
    Tries to safely decode text for message bodies using an encodings dict.
    Goes through encodings by priority and uses the first successful one.
    Tries to detect encoding if all else fails.
    Fully documents the encoding and label for each one that fails

    Parameters:
        body_type (str): a description of the body (i.e. HTML or Text)
        binary_text (binary): an encoded string
        encodings (dict):
            Integer key denoting priority (dict):
                "name" (str):
                "label" (str): a description for the encoding, such as its source
        errors (List): List of Error objects defined in models.py

    Returns:
        test (str): a decoded unicode string
        used (str): The encoding used to decode the text
        errors (List): List of Error objects defined in models.py
    """
    errorObj = None
    used = None
    success = False
    failed = []
    valid = []
    for priority in encodings.keys():
        # for EML/MBOX could be None
        if encodings[priority]["name"]:
            try:
                valid_encoding = codecs.lookup(encodings[priority]["name"]).name.lower()
                valid.append(valid_encoding)
                text = binary_text.decode(valid_encoding, errors="strict")
                used = encodings[priority]["name"]
                success = True
                break
            except Exception as e:
                errorObj = e
                failed.append(encodings[priority]["name"])

    if success == False:
        try:
            detected = chardet.detect(binary_text)["encoding"]
            text = binary_text.decode(detected, errors="strict")
            used = detected
            if len(valid) < 1:
                # desc = "No valid listed encodings, but successfully decoded " + body_type + " body with detected encoding " + detected
                # Don't actually raise this warning, not sure if user cares that much?
                pass
            else:
                desc = (
                    "Failed to decode "
                    + body_type
                    + " message body with listed encoding(s) "
                    + ", ".join(failed)
                    + " (lies!), but successfully decoded with detected encoding "
                    + detected
                )
                errors = common.handle_error(errors, errorObj, desc, "warn")
        except UnicodeDecodeError as e:
            if len(valid) < 1:
                desc = "No valid listed encodings. Failed to decode " + body_type + " message body with detected encoding " + detected
                # just replace the errors
                text = binary_text.decode(detected, errors="replace")
                used = detected
            else:
                desc = "Failed to decode " + body_type + "message body with listed encoding(s) " + ", ".join(failed)
                # just replace the errors
                text = binary_text.decode(valid[0], errors="replace")
                used = valid[0]
            errors = common.handle_error(errors, e, desc, "error")

    return text, used, errors


def parse_part(part, bodies, attachments, errors):
    """
    Used for EML and MBOX parsers
    Parses a part of an email message for multipart messages or a full message with a single part

    Parameters:
        part (email.Message.message part):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        bodies (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        attachments (list): a list of attachment object as defined in models.py
        errors (List): List of Error objects defined in models.py
    Returns:
        bodies (dict):
            "msg" contains a list of human readable error messages
            "stack_trace" contains a list of full stack traces
        attachments (list): a list of attachment object as defined in models.py
        errors (List): List of Error objects defined in models.py
    """
    content_type = part.get_content_type()
    content_disposition = part.get_content_disposition()
    content_id = part["Content-ID"]

    # Extract body
    try:
        if content_disposition != "attachment" and content_disposition != "inline":
            if content_type == "text/html" or content_type == "text/plain":
                encodings = {}
                encodings[1] = {"name": part.get_content_charset(), "label": "listed charset"}
                message_body, part_encoding, errors = safely_decode(content_type, part.get_payload(decode=True), encodings, errors)
                if content_type == "text/html":
                    bodies["html_encoding"] = part_encoding
                    bodies["html_body"] = message_body
                elif content_type == "text/plain":
                    bodies["text_encoding"] = part_encoding
                    bodies["text_body"] = message_body
    except Exception as e:
        desc = "Error parsing message body"
        errors = common.handle_error(errors, e, desc)

    # Extract attachments
    attachmentCount = 0
    if part.get_content_maintype() == "multipart":
        pass
    elif content_disposition is None and content_id is None:
        pass
    else:
        try:
            if not part.get_payload(decode=True):
                if part.get_filename():
                    desc = "Missing attachment content, failed to read attachment " + part.get_filename()
                else:
                    desc = "Missing attachment content and filename, failed to read attachment"
                errors = common.handle_error(errors, None, desc)
            else:
                # Generate a Content-ID if none is available
                if content_id is None:
                    content_id = uuid.uuid4().hex

                attachmentFile = part.get_payload(decode=True)
                if part.get_filename():
                    attachmentName = part.get_filename()
                else:
                    attachmentName = None
                    desc = "No filename found for attachment, integer will be used instead"
                    errors = common.handle_error(errors, None, desc)

                # Handle attachments.csv conflict
                # helper.controller.writeAttachmentsToDisk() handles this
                if attachmentName:
                    if attachmentName.lower() == "attachments.csv":
                        desc = "attachment " + attachmentName + " will be renamed to avoid filename conflict with mailbag spec"
                        errors = common.handle_error(errors, None, desc, "warn")
                        attachmentWrittenName = str(attachmentCount) + os.path.splitext(attachmentName)[1]
                    else:
                        attachmentWrittenName = common.normalizePath(attachmentName.replace("/", "%2F"))
                else:
                    attachmentWrittenName = str(attachmentCount)

                attachment = Attachment(
                    Name=attachmentName,
                    WrittenName=attachmentWrittenName,
                    File=attachmentFile,
                    MimeType=content_type,
                    Content_ID=content_id,
                )
                attachments.append(attachment)
                attachmentCount += 1
        except Exception as e:
            desc = "Error parsing attachments"
            errors = common.handle_error(errors, e, desc)

    return bodies, attachments, errors


def decode_header_part(header, errors):
    """
    Used for to decode strings according to RFC 1342.
    If the string is not encoded, just return it.
    For encoded strings it tries to decode it with email.header.decode_header().
    If we don't get a real encoding, it tries it best to detect it.
    Errors are logged and documented in the error report.

    Parameters:
        header (email.header.Header or string or None):
        errors (List): List of Error objects defined in models.py
    Returns:
        header_string (str): A as-best-as-we-can-do decoded string
        errors (List): List of Error objects defined in models.py
    """
    # headerObj, encoding = decode_header(header)[0]
    header_string = []
    for part in decode_header(header):
        headerObj, encoding = part
        if encoding:
            # Did we get a real encoding?
            try:
                encoding = codecs.lookup(encoding).name.lower()
            except:
                # If not, might as well try to detect it.
                encoding = chardet.detect(headerObj)["encoding"]
            try:
                header_string.append(headerObj.decode(encoding))
            except UnicodeDecodeError as e:
                # Document that the header isn't valid
                desc = "Error decoding header with " + encoding
                errors = common.handle_error(errors, e, desc)
                header_string.append(headerObj.decode(encoding, errors="replace"))
        else:
            if isinstance(headerObj, str):
                # Not encoded
                header_string.append(headerObj)
            else:
                # Oddly, there are weird cases where quotes (") return a binary with no encoding.
                # Dunno what to do here so just hopefully safely decode it?
                header_string.append(headerObj.decode(errors="replace"))

    return "".join(header_string), errors


def parse_header(header, errors):
    """
    Used to handle headers that have RFC 1342 encoding.
    Sometimes the whole header is encoded, while
    sometimes only part of the header string is encoded.
    In some cases we also get a Header object that
    decode_header_part() also handles.

    Parameters:
        header (email.header.Header or string or None):
        errors (List): List of Error objects defined in models.py
    Returns:
        header_string (str or None): A as-best-as-we-can-do decoded string
        errors (List): List of Error objects defined in models.py
    """
    if header is None:
        header_string = None
    else:
        if isinstance(header, str):
            header_list = []
            for header_part in header.split(" "):
                decoded_part, errors = decode_header_part(header_part, errors)
                header_list.append(decoded_part)
            header_string = " ".join(header_list)
        else:
            decoded_part, errors = decode_header_part(header, errors)
            header_string = html.unescape(decoded_part)

    return header_string, errors


def messagePath(headers):
    """
    Tries to read any email folder arragement from headers
    Useful for getting the path of messages within an email account

    Parameters:
        headers (email.message.Message): Can be used as a dict of email headers

    Returns:
        String: messagePath (must at least return an empty string)
    """

    if headers["X-Folder"]:
        messagePath = Path(headers["X-Folder"]).as_posix()
    else:
        messagePath = ""
    return messagePath


def moveFile(dry_run, keep, oldPath, newPath):
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    try:
        log.debug("from: " + str(oldPath))
        log.debug("to: " + str(newPath))
        if keep:
            shutil.copy2(oldPath, newPath)
        else:
            shutil.move(oldPath, newPath)
    except IOError as e:
        log.error("Unable to move file. %s" % e)


def getFileBeforeAfterPath(source_parent_dir, mailbag_dir, mailbag_name, input, file):
    """
    Creates file paths for input mail files and new paths. This is really for moving hierarchies of
    EML or MSG files, as the we need to recreate the directory structure relative to source_parent_dir
    in the mailbag. However, this is called for moving (copy with --keep) all source files into the
    mailbag, including single PST or MBOX files and companion files, which also may have relative
    subdirectories that need to be recreated.

    Parameters:
        source_parent_dir (String): Parent directory of the source files
        mailbag_dir (String): Path where the mailbag will be written
        mailbag_name (String): Mailbag name
        input (String): Email file format to be packaged into a mailbag
        file (String): Email file path

    Returns:
        full_source_parent_path (Path): Absolute path for source_parent_dir
        full_file_path (Path): Absolute path for file that is being moved
        file_new_path (str): Output path where the file will be moved
        relative_path (Path): Path for file relative to source directory. Used for logging/debugging.
    """
    full_source_parent_path = Path(source_parent_dir).resolve()
    full_file_path = Path(file).resolve()

    relative_path = full_file_path.relative_to(full_source_parent_path).parents[0]
    filename = full_file_path.name

    folder_new = os.path.join(mailbag_dir, "data", input)
    file_new_path = os.path.join(folder_new, relative_path, filename)

    return full_source_parent_path, full_file_path, file_new_path, relative_path


def moveWithDirectoryStructure(dry_run, keep, source_parent_dir, mailbag_dir, mailbag_name, input, file, errors):
    """
    Create new mailbag directory structure while maintaining the input data's directory structure.
    Uses for both email files matching the input file extension and companion files if that option is selected

    Parameters:
        dry_run (Boolean): option to perform a test creation of a mailbag
        keep (Boolean): option to preserve source data
        source_parent_dir (String): Parent directory of the source files
        mailbag_dir (String): Path where the mailbag will be written
        mailbag_name (String): Mailbag name
        input (String): Email file format to be packaged into a mailbag
        file (String): Email file path
        errors (List): List of Error objects for the message defined in models.py. moveWithDirectoryStructure is also called for moving companion files which do not have error objects since they are not messages. In that case errors should be an empty list ([]).

    Returns:
        file_new_path (Path): The path where the file was moved
        errors (List): List of Error objects defined in models.py
    """
    full_source_parent_path, full_file_path, file_new_path, relative_path = getFileBeforeAfterPath(
        source_parent_dir, mailbag_dir, mailbag_name, input, file
    )
    if keep:
        verb = "Copying"
    else:
        verb = "Moving"
    if file.lower().endswith("." + input.lower()):
        log.debug(f"{verb}: {str(full_file_path)} to: {str(file_new_path)} SubFolder: {str(relative_path)}")
    else:
        log.debug(f"{verb} companion file: {str(full_file_path)} to: {str(file_new_path)} SubFolder: {str(relative_path)}")

    errors = common.check_path_length(file_new_path, errors)
    if not dry_run:
        moveFile(dry_run, keep, full_file_path, file_new_path)
        # clean up old directory structure
        p = full_file_path.parents[0]
        while p != p.root and p != full_source_parent_path:
            if not os.listdir(p):
                log.debug("Cleaning: " + str(p))
                os.rmdir(p)
                # dirty hack since rmdir is not synchronous on Windows
                if os.name == "nt":
                    import time

                    time.sleep(0.01)
            p = p.parent

    return file_new_path, errors


def guessMimeType(filename):
    """
    Takes an file name and uses mimetypes to guess the mime type

    Parameters:
        filename (String): Attachment filename

    Returns:
        Mimetype (String)
    """
    return mimetypes.guess_type(filename)[0]
