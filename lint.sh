#!/bin/bash

SCRIPT_NAME=$0
COMMAND=$1
FILEPATH=${2:-.}

function handle_exit {
    EXIT_CODE=$1
    if [[ $EXIT_CODE -ne 0 ]]; then
        echo $2
    fi
    exit $EXIT_CODE
}

case ${COMMAND} in
    check-format)
        poetry run black ${FILEPATH} --check
        handle_exit $? "Formatting error! Run \`$SCRIPT_NAME format\` to format the code"
        ;;
    check-flake8)
        poetry run flake8 ${FILEPATH}
        handle_exit $? "Flake8 error!"
        ;;
    check-isort)
        poetry run isort ${FILEPATH} --check-only
        handle_exit $? "Formatting error! Run \`$SCRIPT_NAME format\` to format the code"
        ;;

    check)
        set -e
        $SCRIPT_NAME check-format $FILEPATH
        $SCRIPT_NAME check-isort $FILEPATH
        $SCRIPT_NAME check-flake8 $FILEPATH
        echo "OK"
        ;;
  
    format)
        poetry run black ${FILEPATH}
        poetry run isort ${FILEPATH}
        ;;

    *)
        echo $"Usage: $SCRIPT_NAME {check|format}"
        exit 1

esac
