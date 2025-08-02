import os
import sys
from structlog import get_logger

log = get_logger()


def allow_exit(input_string):
    """
    This allows a user to enter "exit" to exit the program for any prompt.
    """
    if input_string.lower() == "exit":
        sys.exit()


def yes_no(query):
    """
    A reusable guided prompt with validation for yes/no queries.
    Allows users to try again for invalid input.
    Accepts "yes", "y", "no", and "n" and is not case sensative

    Parameters:
        query (String): The question that will be displayed to the user in input()
    Returns:
        (Boolean)
    """
    input_string = ""
    input_options = ["yes", "y", "no", "n"]
    yes = False
    while not input_string.lower().strip() in input_options:
        input_string = input(query + " (" + ", ".join(input_options) + "): ")
        allow_exit(input_string)
        if not input_string.lower().strip() in input_options:
            print(f"Invalid input. Must be one of: {', '.join(input_options)}")
        elif input_string.lower().strip() == "y" or input_string.lower().strip() == "yes":
            yes = True
    if yes:
        return True
    else:
        return False


def in_options(query, options):
    """
    A reusable guided prompt with validation for queries where the
    Allows users to try again for invalid input.
    input must be one of a number of options

    Parameters:
        query (String): The question that will be displayed to the user in input()
    Returns:
        input_string (String): A string that must be inv
    """
    input_string = ""
    while not input_string.lower() in options:
        input_string = input(f"{query} ({', '.join(options)}): ")
        allow_exit(input_string)
        if not input_string.lower() in options:
            print(f"Invalid input. Must be one of: {', '.join(options)}")
    return input_string


def prompts(input_types, derivative_types, hashes, metadata_fields):
    """
    A set of guided prompts with validation to guide users with minimal command line experience
    to providing the options to create a mailbag.
    Does not return any values, but instead replaces sys.argv with user-provided input
    This is called by mailbagit.guided() to allow for options to be enterd via input().

    Parameters:
        input_types (List): The possible input formats
        derivative_types (List): The possible derivatives formats
        hashes (List): The possible custom checksums allowed by bagit-python
        metadata_fields (List): The possible bag-info.txt metadata fields
    """
    print('Mailbagit packages email export formats into a "mailbag".')

    # Which input format?
    input_format = in_options("Enter the file format you wish to package", input_types)

    # Path to files or directory
    path = ""
    pathValid = False
    while pathValid == False:
        path = input(f"Enter a path to a {input_format.upper()} file or a directory containing {input_format.upper()} files: ")
        allow_exit(path)
        if os.path.isfile(path):
            if path.lower().endswith("." + input_format.lower()):
                pathValid = True
            else:
                print(f"File {path} is not a {input_format.upper()} file.")
        elif os.path.isdir(path):
            pathValid = True
        else:
            print("Must be a valid path to a file or directory.")

    # What derivatives to create?
    # Don't allow same derivatives as input format
    if input_format.lower() in derivative_types:
        derivative_types.remove(input_format.lower())
    derivatives_formats = ["invalid"]  # Needs to start invalid because the loop ends when the values are valid.
    while not all(item in derivative_types for item in derivatives_formats):
        derivatives_input = input("Enter the derivatives formats to create separated by spaces (" + ", ".join(derivative_types) + "): ")
        allow_exit(derivatives_input)
        derivatives_formats = derivatives_input.split(" ")
        if not all(item in derivative_types for item in derivatives_formats):
            print(f"Invalid format(s). Must be included in: {', '.join(derivative_types)}.")

    # mailbag name
    mailbag_name = ""
    while len(mailbag_name) < 1 or os.path.isdir(os.path.join(path, mailbag_name)):
        mailbag_name = input("Enter a name or output path for the mailbag: ")
        allow_exit(mailbag_name)
        if len(mailbag_name) < 1:
            print("Invalid path")
        elif os.path.isdir(os.path.join(path, mailbag_name)):
            print("A directory already exists at " + os.path.join(path, mailbag_name))

    # Basic setup basic args
    input_args = [sys.argv[0], path, "-i", input_format, "-m", mailbag_name, "-d"]
    input_args.extend(derivatives_formats)

    # dry run?
    if yes_no("Would you like to try a dry run? This is a test run that will report errors but not alter your files."):
        input_args.append("-r")
    else:
        # keep?
        if yes_no("Would you like to keep the source file(s) as-is and copy them into the mailbag instead of moving them?"):
            input_args.append("-k")

    # more options?
    if yes_no("Would you like more options? If no, we will package the mailbag."):

        # Include companion files?
        if os.path.isdir(path):
            if yes_no("Would you like to include companion files (such as metadata files) that are present in the provided directory?"):
                input_args.append("-f")

        # Compress?
        input_format = in_options("Would you like to compress the mailbag?", ["no", "n", "zip", "tar", "tar.gz"])
        if not input_format == "no" and not input_format == "n":
            input_args.extend(["-c", input_format])

        # log to file?
        logValid = False
        logFile = False
        while logValid == False:
            log = input("Would you like to log to a file? ({path/to/file.log}, no, n): ")
            allow_exit(log)
            if log.lower().strip() == "no" or log.lower().strip() == "n":
                logValid = True
            elif len(os.path.dirname(log)) == 0 or os.path.isdir(os.path.dirname(log)):
                input_args.extend(["--log", log])
                logValid = True
                logFile = True
            else:
                print(f"{log} is not a valid path to a log file.")

        # JSON to stdout?
        """
        This is removed since the usability costs of another option outweights the limited expected use
        if logFile == False:
            if yes_no("Mailbagit will log to the console (stdout). Would you like it to log in JSON?"):
                input_args.append("--log_json")
        """

        # Custom CSS?
        # Only ask for HTML or PDF derivatives
        if "html" in derivatives_formats or any("pdf" in formats for formats in derivatives_formats):
            css = ""
            cssValid = False
            while cssValid == False:
                css = input("Would you like to apply custom CSS to HTML and PDF derivatives? ({path/to/file.css}, no, n): ")
                allow_exit(css)
                if css.lower().strip() == "no" or css.lower().strip() == "n":
                    cssValid = True
                elif os.path.isfile(css) and css.lower().endswith(".css"):
                    input_args.extend(["--css", css])
                    cssValid = True
                else:
                    print(f"{css} is not a path to a valid CSS file.")

        # Customize checksums?
        if yes_no("Mailbagit uses sha256 and sha512 by default. Would you like to customize the checksums used?"):
            custom_hashes = ["invalid"]  # Needs to start invalid because the loop ends when the values are valid.
            while not all(item in hashes for item in custom_hashes):
                hashes_input = input("Enter the checksum algorithms to use separated by spaces (" + ", ".join(hashes) + "): ")
                allow_exit(hashes_input)
                custom_hashes = hashes_input.split(" ")
                if not all(item in hashes for item in custom_hashes):
                    print(f"Invalid checksums(s). Must be included in: ({', '.join(hashes)}).")
            for custom_hash in custom_hashes:
                input_args.append("--" + custom_hash)

        # Custom metadata?
        if yes_no("Do you want to add custom metadata in bag-info.txt?"):
            print("Optional Metadata Fields:")
            print("\t" + "\n\t".join(metadata_fields))
            custom_metadata = {}
            metadata_done = False
            while metadata_done == False:
                metadata_input = input('Enter a field and value separated by colon (:), or enter "done" when complete: ')
                allow_exit(metadata_input)
                if metadata_input.lower().strip() == "done":
                    metadata_done = True
                elif len(metadata_input) < 1 or not ":" in metadata_input:
                    print(f'Invalid input. Must be a field and value separated by a colon. e.g. "capture-agent: Microsoft Outlook"')
                else:
                    custom_key, custom_value = metadata_input.split(":", 1)
                    if not custom_key in metadata_fields:
                        print(f"Invalid field \"{custom_key}\". Must be included in: ({', '.join(metadata_fields)}).")
                    else:
                        print(f'--> Adding "{custom_key.strip()}: {custom_value.strip()}" to bag-info.txt.')
                        custom_metadata[custom_key.strip()] = custom_value.strip()
            for field in custom_metadata.keys():
                input_args.extend(["--" + field, custom_metadata[field]])

    # Replace args with args from guided prompts
    sys.argv = input_args
