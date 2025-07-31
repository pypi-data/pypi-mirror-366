from datetime import datetime
from importlib.metadata import version
import sys

from log import CustomLogger

from drive.utilities.parser import generate_cmd_parser


def main() -> None:
    parser = generate_cmd_parser()

    args = parser.parse_args()

    # getting the programs start time
    start_time = datetime.now()

    # creating and configuring the logger and then recording user inputs
    logger = CustomLogger.create_logger()

    if args.output.is_dir():
        logger.configure(
            args.output, args.log_filename, args.verbose, args.log_to_console
        )
    else:
        logger.configure(
            args.output.parent, args.log_filename, args.verbose, args.log_to_console
        )

    logger.info(f"DRIVE version: {version('drive-ibd')}")

    logger.info(f"command passed to DRIVE: {' '.join(sys.argv)}")

    # record the input parameters using a method from the logger object that
    # takes the parser as an argument
    logger.record_namespace(args)

    logger.debug(f"Parent directory for log files and output: {args.output.parent}")

    logger.info(f"Analysis start time: {start_time}")

    args.func(args)

    end_time = datetime.now()

    logger.info(
        f"Analysis finished at {end_time}. Total runtime: {end_time - start_time}"
    )


if __name__ == "__main__":
    main()
